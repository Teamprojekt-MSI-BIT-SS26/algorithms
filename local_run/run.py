"""
Run the team generation algorithm locally, without Canvas, Django server or database.

Reads a JSON file in the same format Canvas sends to POST /api/generate/teams,
runs the algorithm and prints/writes the generated teams.

Usage (from the repository root):
    python -m local_run.run                                   # uses sample_payload.json
    python -m local_run.run local_run/sample_payload_18.json  # 18 students
    python -m local_run.run path/to/payload.json -o teams.json

Automated test run with both sample payloads and all algorithm types:
    python -m unittest tests.test_local_run.test_local_run
"""
import argparse
import json
from pathlib import Path

from algorithms.ai.algorithm_runner import AlgorithmRunner
from algorithms.api.utils.generate_teams_data_loader import GenerateTeamsDataLoader
from algorithms.api.validators.generate_teams_validator import GenerateTeamsValidator
from algorithms.dataclasses.team_set.serializer import TeamSetSerializer

DEFAULT_INPUT = Path(__file__).parent / "sample_payload.json"


def main():
    parser = argparse.ArgumentParser(description="Generate teams locally.")
    parser.add_argument("input", nargs="?", default=DEFAULT_INPUT, type=Path)
    parser.add_argument("-o", "--output", type=Path, help="write teams as JSON")
    args = parser.parse_args()

    payload = json.loads(args.input.read_text())

    # same steps as the API endpoint (algorithms/api/views/generate_teams.py)
    GenerateTeamsValidator(payload).validate()
    input_data = GenerateTeamsDataLoader(payload).load()

    runner = AlgorithmRunner(
        algorithm_type=input_data.algorithm_type,
        team_generation_options=input_data.team_generation_options,
        algorithm_options=input_data.algorithm_options,
    )
    team_set = runner.generate(input_data.students)

    for team in team_set.teams:
        names = [s.name or str(s.id) for s in team.students]
        print(f"Team {team.id}: {', '.join(names)}")

    if args.output:
        result = TeamSetSerializer().default(team_set)
        args.output.write_text(json.dumps(result, indent=2))
        print(f"\nTeams written to {args.output}")


if __name__ == "__main__":
    main()
