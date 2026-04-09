import unittest
import os
import shutil
from core.memory import create_task, update_step, get_task, save_checkpoint, load_checkpoint

TEST_TASK_ID = "test_001"

class TestMemory(unittest.TestCase):

    def setUp(self):
        # Clean up before each test
        for d in ["memory/tasks", "memory/checkpoints"]:
            os.makedirs(d, exist_ok=True)

    def tearDown(self):
        for f in [f"memory/tasks/{TEST_TASK_ID}.json"]:
            if os.path.exists(f):
                os.remove(f)
        for f in os.listdir("memory/checkpoints"):
            if f.startswith(TEST_TASK_ID):
                os.remove(f"memory/checkpoints/{f}")

    def test_create_and_get_task(self):
        task = create_task(TEST_TASK_ID, "test input", {"phases": []})
        self.assertEqual(task["task_id"], TEST_TASK_ID)
        self.assertEqual(task["status"], "PENDING")

        loaded = get_task(TEST_TASK_ID)
        self.assertEqual(loaded["task_id"], TEST_TASK_ID)

    def test_update_step(self):
        create_task(TEST_TASK_ID, "test input", {"phases": []})
        update_step(TEST_TASK_ID, "1.1", "DONE", "some output")

        task = get_task(TEST_TASK_ID)
        self.assertEqual(task["steps"]["1.1"]["status"], "DONE")
        self.assertEqual(task["steps"]["1.1"]["output"], "some output")

    def test_checkpoint_save_and_load(self):
        save_checkpoint(TEST_TASK_ID, "1.1", "coder", "def hello(): pass")
        cp = load_checkpoint(TEST_TASK_ID, "1.1")
        self.assertIsNotNone(cp)
        self.assertEqual(cp["output"], "def hello(): pass")
        self.assertEqual(cp["agent_role"], "coder")

if __name__ == "__main__":
    unittest.main()
