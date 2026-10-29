from collections import defaultdict

from pydantic import BaseModel, ConfigDict
from sp_client import SpTask
from whiteboard import TaskStatus, WhiteboardItem


class SyncPlan(BaseModel):
    model_config = ConfigDict(frozen=True)
    reopen: list[SpTask]
    complete: list[SpTask]
    add: list[str]


def plan_sync(board_items: list[WhiteboardItem], sp_tasks: list[SpTask]) -> SyncPlan:
    sp_dict: defaultdict[str, list[SpTask]] = defaultdict(list)
    for task in sp_tasks:
        title = normalize_title(task.title)
        sp_dict[title].append(task)

    reopen: list[SpTask] = []
    complete: list[SpTask] = []
    add: list[str] = []

    for item in board_items:
        title = normalize_title(item.title)
        matches = sp_dict.get(title, [])

        has_open_match = any(not task.is_done for task in matches)

        if not matches and item.status == TaskStatus.NOT_DONE:
            add.append(item.title)
        elif has_open_match and item.status == TaskStatus.DONE:
            complete.extend(task for task in matches if not task.is_done)
        elif matches and not has_open_match and item.status == TaskStatus.NOT_DONE:
            # Reopen only the first match; duplicates are already done and reopening all would recreate them
            reopen.append(matches[0])

    return SyncPlan(reopen=reopen, complete=complete, add=add)


def normalize_title(title: str) -> str:
    return "".join(title.split()).lower()
