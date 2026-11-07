# Algorithm API documentation

The API serves the team generation algorithms over HTTP. The main endpoint is
`POST /api/generate/teams/`. It accepts the same JSON payload as the local run
(see `local_run/sample_data/payload_priority_15_students.json`) and answers with
`{"teams": ..., "metadata": ..., "error": ...}`.

## Requirements

- Python 3.9 or 3.10
- No database server for local development: without `DB_ENGINE`, a SQLite file `db.sqlite3` is created in the repository root.

## Local setup

All commands run in the repository root.

1. Install the dependencies:
    ```bash
    python -m pip install -r requirements.txt
    ```
2. Create the configuration file:
    ```bash
    cp env/api.env.example env/.env
    ```
3. Choose an API key and generate its hash:
    ```bash
    python -m utils.api_auth <key>
    ```
   Put the printed hash into `API_AUTH_ALLOWED_KEYS` in `env/.env`. Several hashes are separated by spaces.
   Clients send the plain key, not the hash.
4. Create the database tables:
    ```bash
    python manage.py migrate
    ```
5. Start the API on port 8001 (port 8000 is used by the teamable-backend):
    ```bash
    python manage.py runserver 8001
    ```

## Calling the API

Every request needs the plain key in the `X-Api-Key` header. Without a key the API answers `400`,
with a wrong key `401`. If `API_AUTH_ALLOWED_KEYS` is empty, every request is rejected.

```bash
curl -X POST "http://localhost:8001/api/generate/teams/" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: <key>" \
  --data @local_run/sample_data/payload_priority_15_students.json
```

Every call is logged in the `APILog` table. Add `?sandbox=true` to the URL to skip the log entry.

## Tests

```bash
python -m unittest tests.test_api.test_views.test_generate_teams
```

## Production

`docker-compose.yml` starts the API with PostgreSQL and nginx. It uses the settings in
`algorithms/api/settings/prod.py` and reads `env/.env.prod`.
