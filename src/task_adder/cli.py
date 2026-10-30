import argparse
import mimetypes
import os
from pathlib import Path

import httpx
from dotenv import load_dotenv
from google import genai

from task_adder.sp_client import BASE_URL, ensure_sp_reachable, list_tasks
from task_adder.sync import apply_plan, plan_sync
from task_adder.whiteboard import TIMEOUT_MS, read_whiteboard


def main() -> None:
    parser = argparse.ArgumentParser(description="sync tasks from an image to SP")
    parser.add_argument("filepath", help="Path to image file", type=Path)
    parser.add_argument(
        "--dry-run", action="store_true", help="print plan without asking or applying"
    )
    args = parser.parse_args()

    file_type, _ = mimetypes.guess_file_type(args.filepath)
    if not file_type or not file_type.startswith("image/"):
        return parser.error("expected an image file")

    load_dotenv()
    api_token = os.environ["SP_TOKEN"]
    sp_headers = {"Authorization": f"Bearer {api_token}"}

    gemini_token = os.environ["GEMINI_API_KEY"]

    with httpx.Client(base_url=BASE_URL, headers=sp_headers) as sp_client:
        ensure_sp_reachable(sp_client)

        with genai.Client(
            api_key=gemini_token, http_options={"timeout": TIMEOUT_MS}
        ) as gemini_client:
            image = args.filepath.read_bytes()

            board_items = read_whiteboard(
                client=gemini_client, image=image, media_type=file_type
            )

        sp_tasks = list_tasks(sp_client)
        plan = plan_sync(board_items=board_items, sp_tasks=sp_tasks)
        if plan.is_empty():
            print("Nothing to sync")
            return

        print(plan.describe())
        if args.dry_run:
            return

        if input("Apply plan? (y/n): ").lower() == "y":
            apply_plan(client=sp_client, plan=plan)


if __name__ == "__main__":
    main()
