# Weather Enrichment Service

A small full-stack app for saving cities and fetching weather for them in the background.

The goal is intentionally simple:

1. A user adds a city.
2. The backend saves the city immediately.
3. The backend queues a Celery job.
4. The Celery worker calls the weather API.
5. The worker saves a weather snapshot.
6. The frontend shows each city with the latest saved weather.

No complicated design, no hidden magic, no fake data.

## What is included

- FastAPI backend
- PostgreSQL database
- SQLAlchemy models
- Celery worker
- Redis broker/result backend
- Open-Meteo weather API integration
- Angular frontend
- Docker Compose for the full stack
- Backend pytest tests

Open-Meteo is used because it is public and does not need an API key.

## Folder structure

```text
WES/
  backend/
    app/
      main.py            FastAPI routes
      models.py          SQLAlchemy database tables
      schemas.py         Request/response schemas
      tasks.py           Celery background job
      weather_client.py  Open-Meteo API client
      database.py        Database engine/session setup
      config.py          Environment-based settings
      create_db.py       Creates database tables
    tests/
      test_cities_api.py Backend API tests
    Dockerfile
    pyproject.toml

  frontend/
    src/app/
      app.component.*    Main Angular page
      city.service.ts    REST API calls
      city.model.ts      TypeScript interfaces
    Dockerfile
    nginx.conf
    package.json

  docker-compose.yml
  start_wes.sh
  start_wes.bat
  .env.example
  README.md
```

## Runtime architecture

```text
Browser
  |
  | HTTP
  v
Angular frontend :4200
  |
  | REST API
  v
FastAPI backend :8000
  |
  | SQLAlchemy
  v
PostgreSQL :5432

FastAPI backend
  |
  | enqueue task
  v
Redis :6379
  |
  | consume task
  v
Celery worker
  |
  | HTTPS request
  v
Open-Meteo API
  |
  | save weather snapshot
  v
PostgreSQL
```

## API behavior

### Add a city

```http
POST /cities
Content-Type: application/json

{
  "name": "Kyiv"
}
```

Response:

```json
{
  "id": 1,
  "name": "Kyiv",
  "latest_weather": null,
  "task_id": "celery-task-id"
}
```

The city is saved first. Then a Celery task is queued to fetch weather.

### List cities

```http
GET /cities
```

Response:

```json
[
  {
    "id": 1,
    "name": "Kyiv",
    "latest_weather": {
      "temperature": 20.0,
      "humidity": 32,
      "description": "partly cloudy"
    }
  }
]
```

If Celery has not finished yet, `latest_weather` is `null`.

### Manually update weather

```http
POST /cities/1/update-weather
```

Response:

```json
{
  "city_id": 1,
  "task_id": "celery-task-id",
  "status": "queued"
}
```

This does not block while weather is fetched. It only queues the job.

### Health check

```http
GET /health
```

Response:

```json
{
  "status": "ok"
}
```

## Database model

There are two tables.

### cities

Stores the city itself.

Important fields:

- `id`
- `name`
- `created_at`

### weather_data

Stores weather snapshots for a city.

Important fields:

- `id`
- `city_id`
- `temperature`
- `humidity`
- `description`
- `raw_payload`
- `fetched_at`

The app returns the most recent weather snapshot for each city.

## Run with Docker Compose

The project is portable. Copy the whole `WES` folder to another computer, install Docker Desktop or Docker Engine, then start it from the project root.

Requirements on the target computer:

- Windows/macOS: Docker Desktop installed and running
- Linux: Docker Engine and Docker Compose plugin installed and running
- Free ports: `4200`, `8000`, `5432`, and `6379`

You do not need to install Python, Node, Angular CLI, PostgreSQL, Redis, or Celery locally when using Docker. Docker builds and runs those pieces inside containers.

### One-click launchers

Linux/macOS:

```bash
./start_wes.sh
```

Windows:

```text
Double-click start_wes.bat
```

The launcher scripts:

- check that Docker is installed and running
- create `.env` from `.env.example` if needed
- run `docker compose up -d --build`
- wait for the backend health check
- open the frontend in the browser

### Manual Docker command

```bash
cd WES
cp .env.example .env
docker compose up --build
```

Open:

- Frontend: http://localhost:4200
- Backend API docs: http://localhost:8000/docs
- Backend health: http://localhost:8000/health

Stop everything:

```bash
docker compose down
```

Stop everything and delete the database volume:

```bash
docker compose down -v
```

## Run backend tests

```bash
cd /home/stirkolo/Documents/WES/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest -q
```

Expected result:

```text
4 passed
```

## Run frontend locally

```bash
cd /home/stirkolo/Documents/WES/frontend
npm install
npm start
```

The frontend expects the backend at:

```text
http://localhost:8000
```

That value is in:

```text
frontend/src/environments/environment.ts
```

## Run backend locally without Docker

You still need PostgreSQL and Redis running.

```bash
cd /home/stirkolo/Documents/WES/backend
python3 -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
python -m app.create_db
uvicorn app.main:app --reload
```

In a second terminal, start Celery:

```bash
cd /home/stirkolo/Documents/WES/backend
. .venv/bin/activate
celery -A app.celery_app.celery_app worker --loglevel=info
```

## Environment variables

The Docker setup reads `.env` if present.

Main variables:

```text
POSTGRES_DB=weather
POSTGRES_USER=weather
POSTGRES_PASSWORD=weather
DATABASE_URL=postgresql+psycopg://weather:weather@db:5432/weather
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1
CORS_ORIGINS=http://localhost:4200,http://127.0.0.1:4200
```

The default password is only for local development.

## Design choices

### Why weather is fetched asynchronously

Adding a city should be fast. The user should not wait for an external weather API call.

So the backend saves the city, queues a Celery task, and returns immediately.

### Why weather snapshots are stored

The app keeps a history of fetched weather records. The city list only shows the latest one.

This is simple now and leaves room for later history charts without changing the basic model.

### Why Open-Meteo

Open-Meteo is public, free for simple use, and does not require an API key.

The weather client does two calls:

1. Geocode the city name into latitude/longitude.
2. Fetch current temperature, humidity, and weather code.

The code converts weather codes into readable descriptions.

## Simple manual test

Start the stack:

```bash
docker compose up --build
```

Add a city:

```bash
curl -X POST http://localhost:8000/cities \
  -H 'Content-Type: application/json' \
  -d '{"name":"Kyiv"}'
```

Wait a few seconds, then list cities:

```bash
curl http://localhost:8000/cities
```

Queue a manual update:

```bash
curl -X POST http://localhost:8000/cities/1/update-weather
```

## Notes and limitations

- There is no login/authentication. This is a small service exercise.
- Database migrations are not included. Tables are created at startup for simplicity.
- City names are stored as submitted after trimming whitespace.
- If the weather provider is temporarily unavailable, Celery retries the task.
- The frontend refreshes manually. It does not use WebSockets or polling.

## Verification performed

The project was checked with:

```bash
cd /home/stirkolo/Documents/WES/backend
pytest -q

cd /home/stirkolo/Documents/WES/frontend
npm run build

cd /home/stirkolo/Documents/WES
docker compose config -q
```

The Docker stack was also started, the health endpoint was checked, a city was added, weather enrichment completed, and manual update was queued.
