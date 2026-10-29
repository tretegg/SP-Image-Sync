import pytest
from sp_client import SpTask
from sync import normalize_title, plan_sync
from whiteboard import TaskStatus, WhiteboardItem


def test_not_done_no_match_adds_task():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.NOT_DONE)]
    sp_tasks = [
        SpTask(title="test", is_done=True, task_id="1"),
        SpTask(title="fake", is_done=True, task_id="2"),
        SpTask(title="different task", is_done=True, task_id="3"),
    ]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == ["Do homework"]
    assert plan.complete == []
    assert plan.reopen == []


def test_not_done_open_match_skips():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.NOT_DONE)]
    sp_tasks = [
        SpTask(title="Do homework", is_done=False, task_id="1"),
        SpTask(title="fake", is_done=True, task_id="2"),
        SpTask(title="different task", is_done=True, task_id="3"),
    ]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == []
    assert plan.reopen == []


def test_not_done_all_done_reopens():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.NOT_DONE)]
    sp_tasks = [SpTask(title="Do homework", is_done=True, task_id="1")]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == []
    assert plan.reopen == [SpTask(title="Do homework", is_done=True, task_id="1")]


def test_done_no_match_skips():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.DONE)]
    sp_tasks = [
        SpTask(title="no task", is_done=False, task_id="1"),
        SpTask(title="fake", is_done=True, task_id="2"),
        SpTask(title="different task", is_done=True, task_id="3"),
    ]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == []
    assert plan.reopen == []


def test_done_open_match_completes():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.DONE)]
    sp_tasks = [SpTask(title="Do homework", is_done=False, task_id="1")]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == [SpTask(title="Do homework", is_done=False, task_id="1")]
    assert plan.reopen == []


def test_done_all_done_skips():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.DONE)]
    sp_tasks = [
        SpTask(title="Do homework", is_done=True, task_id="1"),
        SpTask(title="Do homework", is_done=True, task_id="2"),
    ]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == []
    assert plan.reopen == []


def test_reopens_only_one_duplicate():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.NOT_DONE)]
    sp_tasks = [
        SpTask(title="Do homework", is_done=True, task_id="1"),
        SpTask(title="Do homework", is_done=True, task_id="2"),
        SpTask(title="Do homework", is_done=True, task_id="3"),
    ]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == []
    assert plan.reopen == [SpTask(title="Do homework", is_done=True, task_id="1")]


def test_completes_all_open_duplicates():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.DONE)]
    sp_tasks = [
        SpTask(title="Do homework", is_done=False, task_id="1"),
        SpTask(title="Do homework", is_done=False, task_id="2"),
        SpTask(title="Do homework", is_done=False, task_id="3"),
    ]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == [
        SpTask(title="Do homework", is_done=False, task_id="1"),
        SpTask(title="Do homework", is_done=False, task_id="2"),
        SpTask(title="Do homework", is_done=False, task_id="3"),
    ]
    assert plan.reopen == []


def test_mixed_duplicates_skips():
    board = [WhiteboardItem(title="Do homework", status=TaskStatus.NOT_DONE)]
    sp_tasks = [
        SpTask(title="Do homework", is_done=True, task_id="1"),
        SpTask(title="Do homework", is_done=False, task_id="2"),
    ]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == []
    assert plan.reopen == []


def test_matches_ignore_case_and_spacing():
    board = [WhiteboardItem(title="calc    HW", status=TaskStatus.DONE)]
    sp_tasks = [
        SpTask(title="Calc hw  ", is_done=False, task_id="1"),
        SpTask(title="CalC Hw", is_done=False, task_id="2"),
    ]

    plan = plan_sync(board, sp_tasks)

    assert plan.add == []
    assert plan.complete == [
        SpTask(title="Calc hw  ", is_done=False, task_id="1"),
        SpTask(title="CalC Hw", is_done=False, task_id="2"),
    ]
    assert plan.reopen == []


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("  Calc   HW ", "calc hw"),
        ("  CALC   HW ", "caLc hw"),
    ],
)
def test_normalize_title_matches(a: str, b: str):
    assert normalize_title(a) == normalize_title(b)
