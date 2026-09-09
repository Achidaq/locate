# Locate

A small Python API prototype that stores device records and location coordinates submitted by a client. It uses Flask, Flask-SQLAlchemy, and SQLite.

The server does **not** discover a device's location. A separate client must supply the coordinates.

## Scope

- Register a device with a name and unique device ID.
- Submit latitude, longitude, and accuracy for a registered device.
- List registered devices.
- Retrieve recorded location history by target ID.

This is an unauthenticated prototype. Use synthetic data locally: anyone who can reach the API can read and write its records. Authentication, ownership checks, validation, and retention controls are required before using real location data or hosting it publicly.

## Local setup

The repository currently pins an older Flask stack. Dependency installation and runtime behavior have not been verified for this documentation update.

```bash
git clone https://github.com/Achidaq/locate.git
cd locate
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
flask --app tracker run --host 127.0.0.1 --port 5000
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

The optional `DATABASE_URL` process environment variable overrides the default SQLite URI; no `.env` file is loaded automatically. The tests use this setting for an in-memory database.

The first request creates the SQLite tables. The database is stored at `instance/tracking_advanced.db`. The included `Procfile` starts `gunicorn tracker:app`; production deployment requires additional access controls.

## Try the API

Use fictional device names and coordinates.

```bash
curl -X POST http://127.0.0.1:5000/add_target \
  -H "Content-Type: application/json" \
  -d '{"name":"Demo device","device_id":"demo-device-001"}'

curl http://127.0.0.1:5000/targets

curl -X POST http://127.0.0.1:5000/track \
  -H "Content-Type: application/json" \
  -d '{"device_id":"demo-device-001","latitude":"0.0","longitude":"0.0","accuracy":"10"}'
```

Read the numeric `id` from `/targets`, then request `/history/<id>`.

| Method | Route | Input / result |
| --- | --- | --- |
| POST | `/add_target` | JSON: `name`, `device_id`; returns success. |
| POST | `/track` | JSON: `device_id`, `latitude`, `longitude`, `accuracy`; returns success or 404 for an unknown device. |
| GET | `/targets` | Returns an array of device records with their numeric IDs. |
| GET | `/history/<target_id>` | Returns an array of coordinates, accuracy values, and timestamps. |

A successful write returns `{"status":"success"}` with HTTP 200. History entries contain `latitude`, `longitude`, `accuracy`, and `timestamp`.

## Repository map

| File | Purpose |
| --- | --- |
| `tracker.py` | Flask app, database models, and API routes. |
| `requirements.txt` | Python dependency versions. |
| `Procfile` | Gunicorn entry point. |
| `tests/test_api.py` | Isolated in-memory API smoke tests. |

## Checks

After installing dependencies:

```bash
python -m unittest discover -s tests -v
```

The tests use an in-memory SQLite database and synthetic data. They exercise device registration, coordinate submission, history retrieval, unknown-device handling, and database initialization outside a request.

## Known limitations

- No authentication, authorization, pagination, or explicit history ordering.
- Coordinates and accuracy are stored as strings, with no range or unit validation.
- Missing fields and duplicate device IDs currently produce HTTP 500 responses.
- Error responses include exception text; failed writes do not explicitly roll back the session.
- No schema migration tooling or dependency lockfile.
- Legacy dependency compatibility needs verification before this project is presented as runnable on a fresh machine.

## Next development priorities

1. Verify and refresh the dependency stack.
2. Add authentication and per-device access rules.
3. Validate requests and return consistent client-error responses.
4. Add transaction rollback, pagination, and migrations.
