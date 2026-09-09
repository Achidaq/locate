import importlib
import os
import unittest
from unittest.mock import patch


class LocateAPITest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Select a disposable database before SQLAlchemy initializes its engine.
        with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"}):
            cls.tracker = importlib.import_module("tracker")
        cls.tracker.app.config["TESTING"] = True

    def setUp(self):
        with self.tracker.app.app_context():
            self.tracker.db.drop_all()
        # This must also work during direct script startup, outside a request.
        self.tracker.create_tables()
        self.client = self.tracker.app.test_client()

    def tearDown(self):
        with self.tracker.app.app_context():
            self.tracker.db.session.remove()
            self.tracker.db.drop_all()

    def test_register_record_and_retrieve(self):
        response = self.client.post("/add_target", json={
            "name": "Demo device", "device_id": "demo-device-001"
        })
        self.assertEqual(response.status_code, 200)
        targets = self.client.get("/targets").get_json()
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]["device_id"], "demo-device-001")
        response = self.client.post("/track", json={
            "device_id": "demo-device-001",
            "latitude": "0.0", "longitude": "0.0", "accuracy": "10"
        })
        self.assertEqual(response.status_code, 200)
        response = self.client.get(f"/history/{targets[0]['id']}")
        self.assertEqual(response.status_code, 200)
        history = response.get_json()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["latitude"], "0.0")
        self.assertEqual(history[0]["longitude"], "0.0")
        self.assertEqual(history[0]["accuracy"], "10")
        self.assertTrue(history[0]["timestamp"])

    def test_unknown_device_is_rejected(self):
        response = self.client.post("/track", json={
            "device_id": "missing", "latitude": "0.0",
            "longitude": "0.0", "accuracy": "10"
        })
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["message"], "Target not found")

    def test_new_database_has_no_records(self):
        self.assertEqual(self.client.get("/targets").get_json(), [])
        self.assertEqual(self.client.get("/history/999").get_json(), [])


if __name__ == "__main__":
    unittest.main()
