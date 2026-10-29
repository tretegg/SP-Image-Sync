import os

import httpx
from dotenv import load_dotenv

BASE_URL = "http://127.0.0.1:3876"


def ensure_sp_reachable(client: httpx.Client) -> None:
    response = client.get("/health")
    response.raise_for_status()


def add_task(client: httpx.Client, task_title: str) -> str:
    payload = {"title": task_title}
    response = client.post("/tasks", json=payload)
    response.raise_for_status()
    return response.json()["data"]["id"]


def main() -> None:
    load_dotenv()
    api_token = os.environ["SP_TOKEN"]
    headers = {"Authorization": f"Bearer {api_token}"}

    with httpx.Client(base_url=BASE_URL, headers=headers) as client:
        ensure_sp_reachable(client)
        print(add_task(client, "Test task"))


if __name__ == "__main__":
    main()
