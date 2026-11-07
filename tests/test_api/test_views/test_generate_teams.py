import json
import os
import unittest
from unittest.mock import patch

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "algorithms.api.settings")
django.setup()

from django.test import Client

from local_run.run import DEFAULT_INPUT
from utils.api_auth import encrypt_api_auth_token

API_KEY = "test-key"
# sandbox=true skips the APILog entry, so the test needs no database
URL = "/api/generate/teams/?sandbox=true"


class TestGenerateTeamsEndpoint(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key_hash = encrypt_api_auth_token(API_KEY).hex()
        with open(DEFAULT_INPUT, encoding="utf-8") as f:
            cls.payload = json.load(f)

    def setUp(self):
        env_patch = patch.dict(os.environ, {"API_AUTH_ALLOWED_KEYS": self.key_hash})
        env_patch.start()
        self.addCleanup(env_patch.stop)
        self.client = Client()

    def post(self, payload, **headers):
        return self.client.post(
            URL, data=json.dumps(payload), content_type="application/json", **headers
        )

    def test_request_without_api_key__is_rejected(self):
        response = self.post(self.payload)
        self.assertEqual(response.status_code, 400)

    def test_request_with_invalid_api_key__is_rejected(self):
        response = self.post(self.payload, HTTP_X_API_KEY="wrong-key")
        self.assertEqual(response.status_code, 401)

    def test_no_configured_keys__rejects_every_key(self):
        with patch.dict(os.environ, {"API_AUTH_ALLOWED_KEYS": ""}):
            response = self.post(self.payload, HTTP_X_API_KEY=API_KEY)
        self.assertEqual(response.status_code, 401)

    def test_invalid_payload__returns_400(self):
        response = self.post({"students": []}, HTTP_X_API_KEY=API_KEY)
        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json()["error"])

    def test_valid_request__assigns_every_student_to_a_team(self):
        response = self.post(self.payload, HTTP_X_API_KEY=API_KEY)
        self.assertEqual(response.status_code, 200)

        body = response.json()
        self.assertIsNone(body["error"])
        assigned_ids = [
            s["id"] for team in body["teams"]["teams"] for s in team["students"]
        ]
        expected_ids = [s["id"] for s in self.payload["students"]]
        self.assertCountEqual(assigned_ids, expected_ids)
