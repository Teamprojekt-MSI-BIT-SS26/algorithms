import copy
import json
import unittest
from pathlib import Path

from algorithms.ai.algorithm_runner import AlgorithmRunner
from algorithms.api.utils.generate_teams_data_loader import GenerateTeamsDataLoader
from algorithms.api.validators.generate_teams_validator import GenerateTeamsValidator
from algorithms.dataclasses.team_set.serializer import TeamSetSerializer

LOCAL_RUN_DIR = Path(__file__).parents[2] / "local_run"
SAMPLE_PAYLOADS = ["sample_payload.json", "sample_payload_18.json"]


def _with_algorithm_type(payload: dict, algorithm_type: str) -> dict:
    payload = copy.deepcopy(payload)
    options = payload["algorithm_options"]
    if algorithm_type == "random":
        payload["algorithm_options"] = {"algorithm_type": "random"}
    else:
        options["algorithm_type"] = algorithm_type
        if algorithm_type == "priority":
            options.setdefault("priorities", [])
    return payload


def _generate(payload: dict):
    # same steps as local_run/run.py and the API endpoint
    GenerateTeamsValidator(copy.deepcopy(payload)).validate()
    input_data = GenerateTeamsDataLoader(payload).load()
    runner = AlgorithmRunner(
        algorithm_type=input_data.algorithm_type,
        team_generation_options=input_data.team_generation_options,
        algorithm_options=input_data.algorithm_options,
    )
    return runner.generate(input_data.students)


class TestLocalRun(unittest.TestCase):
    """
    Test run with the sample data in local_run/ (12 and 18 students):
    every algorithm must produce a complete and valid team set without errors.
    """

    def test_sample_payloads_generate_valid_teams(self):
        for file_name in SAMPLE_PAYLOADS:
            base_payload = json.loads((LOCAL_RUN_DIR / file_name).read_text())
            options = base_payload["team_generation_options"]
            student_ids = sorted(s["id"] for s in base_payload["students"])
            self.assertTrue(10 <= len(student_ids) <= 20)

            for algorithm_type in ["random", "weight", "social", "priority"]:
                with self.subTest(payload=file_name, algorithm=algorithm_type):
                    payload = _with_algorithm_type(base_payload, algorithm_type)
                    team_set = _generate(payload)

                    self.assertEqual(len(team_set.teams), options["total_teams"])

                    # every student is assigned to exactly one team
                    assigned_ids = sorted(
                        s.id for team in team_set.teams for s in team.students
                    )
                    self.assertEqual(assigned_ids, student_ids)

                    for team in team_set.teams:
                        self.assertGreaterEqual(team.size, options["min_team_size"])
                        self.assertLessEqual(team.size, options["max_team_size"])

                    # output can be serialized to JSON (the format run.py writes)
                    json.dumps(TeamSetSerializer().default(team_set))


if __name__ == "__main__":
    unittest.main()
