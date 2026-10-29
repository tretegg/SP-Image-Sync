import os
import time
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, ConfigDict

GEMINI_MODEL = "gemini-3.5-flash-lite"
PROMPT = """The image is a handwritten to-do whiteboard.
Extract the title of each task alongside their statuses.
The statuses can be one of: not_done, partially_done, done.
not_done will be an empty square next to the task title.
partially_done will be a partially filled square next to the task title.
done will be a filled square next to the task title.
Ignore everything outside of the whiteboard."""
MAX_ATTEMPTS = 4
RETRYABLE_CODES = {429, 500, 503, 504}
TIMEOUT_MS = 10000


class TaskStatus(Enum):
    NOT_DONE = "not_done"
    PARTIALLY_DONE = "partially_done"
    DONE = "done"


class WhiteboardItem(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: str
    status: TaskStatus


def read_whiteboard(
    client: genai.Client, image: bytes, media_type: str
) -> list[WhiteboardItem]:
    for attempt in range(MAX_ATTEMPTS):
        print(f"Trying attempt {attempt + 1}:")
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=[
                    types.Part.from_bytes(data=image, mime_type=media_type),
                    PROMPT,
                ],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=list[WhiteboardItem],
                ),
            )
            return response.parsed
        # Timeouts are not retried because of the worst-case latency
        except errors.APIError as e:
            print(e.code)
            if e.code not in RETRYABLE_CODES or attempt == MAX_ATTEMPTS - 1:
                raise

            time.sleep(2**attempt)


def main() -> None:
    load_dotenv()
    api_token = os.environ["GEMINI_API_KEY"]

    client = genai.Client(api_key=api_token, http_options={"timeout": TIMEOUT_MS})

    image = Path("whiteboard.jpg").read_bytes()

    time_before = time.perf_counter()
    result = read_whiteboard(client, image, "image/jpeg")
    time_taken = time.perf_counter() - time_before
    print(time_taken)

    for item in result:
        print(item)


if __name__ == "__main__":
    main()
