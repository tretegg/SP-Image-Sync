import os

import httpx
from dotenv import load_dotenv
from pydantic import AliasChoices, BaseModel, ConfigDict, Field, TypeAdapter

BASE_URL = "http://127.0.0.1:3876"


class SpTask(BaseModel):
    model_config = ConfigDict(frozen=True)
    title: str
    is_done: bool = Field(validation_alias=AliasChoices("isDone", "is_done"))
    task_id: str = Field(validation_alias=AliasChoices("id", "task_id"))


TASKS_LIST_ADAPTER = TypeAdapter(list[SpTask])


def ensure_sp_reachable(client: httpx.Client) -> None:
    response = client.get("/health")
    response.raise_for_status()


def add_task(client: httpx.Client, task_title: str) -> str:
    payload = {"title": task_title}
    response = client.post("/tasks", json=payload)
    response.raise_for_status()
    return response.json()["data"]["id"]


def list_tasks(client: httpx.Client) -> list[SpTask]:
    response = client.get("/tasks", params={"includeDone": True})
    response.raise_for_status()
    return TASKS_LIST_ADAPTER.validate_python(response.json()["data"])


def main() -> None:
    load_dotenv()
    api_token = os.environ["SP_TOKEN"]
    headers = {"Authorization": f"Bearer {api_token}"}

    with httpx.Client(base_url=BASE_URL, headers=headers) as client:
        ensure_sp_reachable(client)
        print(list_tasks(client))


if __name__ == "__main__":
    main()
