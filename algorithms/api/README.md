# Algorithm API

The API serves the team generation algorithms over HTTP at `POST /api/generate/teams/`. It accepts the
same JSON payload as the local run (see `local_run/sample_data/payload_priority_15_students.json`).
The teamable-backend calls it to generate teams.

The full documentation (setup, interface, backend integration and tests) is in the project documentation:

- [Backend integration and interface](https://teamprojekt-msi-bit-ss26.github.io/documentation/umsetzung/Backend-Integration/INTEGRATION_EN/)
  ([Deutsch](https://teamprojekt-msi-bit-ss26.github.io/documentation/umsetzung/Backend-Integration/INTEGRATION/))
- [Payload and configuration](https://teamprojekt-msi-bit-ss26.github.io/documentation/umsetzung/Algorithmus/UEBERGABE_EN/)
  ([Deutsch](https://teamprojekt-msi-bit-ss26.github.io/documentation/umsetzung/Algorithmus/UEBERGABE/))

## Quick start

Requires Python 3.9 or 3.10. No database server is needed: without `DB_ENGINE`, a SQLite file
`db.sqlite3` is created in the repository root. All commands run in the repository root.

```bash
python -m pip install -r requirements.txt
cp env/api.env.example env/.env
python -m utils.api_auth <key>      # put the printed hash into API_AUTH_ALLOWED_KEYS in env/.env
python manage.py migrate
python manage.py runserver 8001
```

Clients send the plain key in the `X-Api-Key` header. Add `?sandbox=true` to the URL to skip the log entry.

```bash
curl -X POST "http://localhost:8001/api/generate/teams/" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: <key>" \
  --data @local_run/sample_data/payload_priority_15_students.json
```

Tests:

```bash
python -m unittest tests.test_api.test_views.test_generate_teams
```
