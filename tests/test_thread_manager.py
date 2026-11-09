"""
Unit tests for ThreadManager.
Verifies thread creation, message appending, thread isolation, and deletion.
"""

from src.chat.thread_manager import ThreadManager


def test_thread_creation():
    mgr = ThreadManager()
    t_id = mgr.create_thread()
    assert t_id is not None
    thread = mgr.get_thread(t_id)
    assert thread is not None
    assert len(thread.history) == 0


def test_thread_add_message():
    mgr = ThreadManager()
    t_id = mgr.create_thread()
    mgr.add_message(t_id, role="user", content="What is the exit load?")
    mgr.add_message(t_id, role="assistant", content="The exit load is 1%.")
    
    history = mgr.get_history(t_id)
    assert len(history) == 2
    assert history[0]["content"] == "What is the exit load?"
    assert history[1]["content"] == "The exit load is 1%."


def test_thread_isolation():
    mgr = ThreadManager()
    t1 = mgr.create_thread()
    t2 = mgr.create_thread()

    mgr.add_message(t1, role="user", content="Question for Thread 1")
    mgr.add_message(t2, role="user", content="Question for Thread 2")

    h1 = mgr.get_history(t1)
    h2 = mgr.get_history(t2)

    assert len(h1) == 1
    assert len(h2) == 1
    assert h1[0]["content"] == "Question for Thread 1"
    assert h2[0]["content"] == "Question for Thread 2"


def test_thread_deletion():
    mgr = ThreadManager()
    t_id = mgr.create_thread()
    assert mgr.get_thread(t_id) is not None
    deleted = mgr.delete_thread(t_id)
    assert deleted is True
    assert mgr.get_thread(t_id) is None

