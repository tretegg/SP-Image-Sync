import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from google import genai

from task_adder.sp_client import (
    list_tasks,
)
from task_adder.sync import apply_plan, plan_sync
from task_adder.whiteboard import read_whiteboard

TIMEOUT_MS = 10000
BASE_URL = "http://127.0.0.1:3876"


def main() -> None:
    load_dotenv()
    api_token = os.environ["SP_TOKEN"]
    sp_headers = {"Authorization": f"Bearer {api_token}"}

    gemini_token = os.environ["GEMINI_API_KEY"]

    with genai.Client(
        api_key=gemini_token, http_options={"timeout": TIMEOUT_MS}
    ) as client:
        image = Path("whiteboard2.jpg").read_bytes()
        gemini_result = read_whiteboard(
            client=client, image=image, media_type="image/jpeg"
        )

    with httpx.Client(base_url=BASE_URL, headers=sp_headers) as client:
        sp_tasks = list_tasks(client)
        plan = plan_sync(board_items=gemini_result, sp_tasks=sp_tasks)
        apply_plan(client=client, plan=plan)


if __name__ == "__main__":
    main()
