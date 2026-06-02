# Weather Enrichment Service — Beginner Study Guide

This file explains the whole project slowly and in plain language.

It is written for someone who is new to backend development, frontend development, Docker, Celery, Redis, databases, APIs, and full-stack applications.

You do not need to memorize everything at once. Read it in layers:

1. First understand the story of what the app does.
2. Then understand the big pieces: frontend, backend, database, worker.
3. Then read the file-by-file explanation.
4. Then run the app and compare what you see with what this guide says.

Project folder:

```text
/home/stirkolo/Documents/WES
```

---

# 1. The app in one sentence

The Weather Enrichment Service lets a user add a city, then the backend saves the city and asks a background worker to fetch weather data for that city.

Example:

```text
User types: Rome
App saves: Rome
Celery worker fetches: temperature, humidity, description
App displays: Rome, 27.4 °C, 53% humidity, overcast
```

The important idea is this:

```text
Adding the city is immediate.
Fetching weather happens in the background.
```

That is what “asynchronously” means in this project.

---

# 2. Why the project has several parts

A full-stack app usually has multiple responsibilities.

This app has these parts:

```text
Frontend       The web page the user sees
Backend        The API that receives requests
Database       Stores cities and weather data
Redis          A queue/broker for background jobs
Celery worker  Runs slow background work
Weather API    External service that gives weather data
Docker         Runs all the pieces together
```

Think of it like a small restaurant:

```text
Customer        = browser user
Waiter          = frontend
Kitchen counter = backend API
Notebook        = database
Order ticket    = Redis queue
Cook            = Celery worker
Supplier        = external weather API
Building setup  = Docker Compose
```

When the customer orders food, the waiter does not cook it. The waiter sends the order to the kitchen. The cook works separately. That is similar to FastAPI + Celery.

---

# 3. The simplest mental model

When you open the web page:

```text
Browser -> Angular frontend
```

When you add a city:

```text
Angular -> FastAPI -> PostgreSQL
                 |
                 v
               Redis -> Celery worker -> Open-Meteo -> PostgreSQL
```

When you refresh the city list:

```text
Angular -> FastAPI -> PostgreSQL -> FastAPI -> Angular
```

The database is the shared memory. FastAPI writes cities. Celery writes weather. FastAPI reads both.

---

# 4. What each technology means

## 4.1 Frontend

The frontend is the part of the app that runs in the browser.

In this project the frontend is Angular.

It shows:

- a city input form
- an Add city button
- a city list
- weather values
- an Update Weather button
- loading and error messages

The frontend does not talk directly to the database. It talks to the backend using HTTP requests.

## 4.2 Backend

The backend is the server-side part of the app.

In this project the backend is FastAPI.

It provides URLs like:

```text
GET  /health
POST /cities
GET  /cities
POST /cities/{city_id}/update-weather
```

The frontend calls those URLs.

The backend is responsible for:

- validating input
- saving cities
- reading cities
- starting background tasks
- returning JSON responses

## 4.3 API

API means Application Programming Interface.

In this project, API means “HTTP endpoints that the frontend can call.”

Example:

```text
POST /cities
```

This means:

```text
Send data to the backend to create a city.
```

## 4.4 HTTP

HTTP is the protocol browsers use to talk to servers.

Common HTTP methods:

```text
GET     read something
POST    create something or trigger an action
PUT     replace something
PATCH   update part of something
DELETE  delete something
```

This project uses:

```text
GET  /cities                         read cities
POST /cities                         create city
POST /cities/{city_id}/update-weather trigger weather update
```

## 4.5 JSON

JSON is a text format for sending structured data.

Example JSON:

```json
{
  "name": "Rome"
}
```

The frontend sends JSON to the backend. The backend returns JSON to the frontend.

## 4.6 Database

A database stores data permanently.

If the app shuts down and restarts, the database still remembers the cities and weather records.

This project uses PostgreSQL.

## 4.7 PostgreSQL

PostgreSQL is a real production-grade relational database.

Relational means data is stored in tables.

This app has two main tables:

```text
cities
weather_data
```

## 4.8 SQLAlchemy

SQLAlchemy is a Python library that lets Python code work with database tables.

Instead of writing raw SQL everywhere, we define Python classes:

```python
class City(Base):
    ...

class WeatherData(Base):
    ...
```

SQLAlchemy maps those Python classes to database tables.

This is called ORM: Object Relational Mapping.

## 4.9 Redis

Redis is an in-memory data store.

In this project Redis is used as a message broker.

That means Redis is like a queue of jobs.

FastAPI says:

```text
Please update weather for city 2.
```

Redis holds that message until Celery picks it up.

## 4.10 Celery

Celery is a background task system for Python.

A background task is work that should happen outside the normal web request.

Why use background tasks?

Because some work is slow or unreliable:

- calling an external weather API
- sending emails
- processing images
- generating reports
- importing large files

If FastAPI waited for all that inside the user request, the app would feel slow.

So FastAPI queues work, returns quickly, and Celery does the work separately.

In this app:

```text
FastAPI saves city
FastAPI queues Celery task
Celery fetches weather
Celery saves weather
```

## 4.11 Docker

Docker packages an application and its dependencies into containers.

A container is like a small isolated computer process with everything it needs.

This matters because this project needs several services:

- Python backend
- Angular frontend
- PostgreSQL database
- Redis server
- Celery worker

Without Docker, you would need to install and configure all of those manually.

With Docker Compose, you run:

```bash
docker compose up --build
```

and it starts everything.

## 4.12 Docker Compose

Docker Compose runs multiple Docker containers together.

This project's `docker-compose.yml` says:

```text
start PostgreSQL
start Redis
start backend
start Celery worker
start frontend
connect them on the same network
open ports 4200 and 8000
```

## 4.13 FastAPI

FastAPI is a Python web framework.

It is used to build APIs.

Why it is nice:

- simple route definitions
- automatic JSON handling
- automatic API docs at `/docs`
- good type support
- works well with Pydantic schemas

## 4.14 Angular

Angular is a frontend framework.

It helps build browser apps with:

- components
- HTML templates
- TypeScript code
- forms
- HTTP services

In this project Angular is kept simple: one main component and one service.

## 4.15 Open-Meteo

Open-Meteo is the external weather API used by the project.

It is used instead of OpenWeather because it does not require an API key.

That makes the app easier to run for study and testing.

---

# 5. The project structure

Here is the simplified project tree:

```text
WES/
  README.md
  study.md
  docker-compose.yml
  .env.example
  .gitignore

  backend/
    Dockerfile
    pyproject.toml
    app/
      __init__.py
      config.py
      database.py
      models.py
      schemas.py
      main.py
      celery_app.py
      tasks.py
      weather_client.py
      create_db.py
    tests/
      test_cities_api.py

  frontend/
    Dockerfile
    nginx.conf
    package.json
    package-lock.json
    angular.json
    tsconfig.json
    tsconfig.app.json
    src/
      index.html
      main.ts
      styles.css
      environments/
        environment.ts
      app/
        app.component.ts
        app.component.html
        app.component.css
        city.service.ts
        city.model.ts
```

The most important files for studying are:

```text
backend/app/main.py            API endpoints
backend/app/models.py          database tables
backend/app/tasks.py           Celery background job
backend/app/weather_client.py  external weather API call
frontend/src/app/app.component.html  UI template
frontend/src/app/app.component.ts    UI behavior
frontend/src/app/city.service.ts     frontend REST calls
docker-compose.yml             how everything runs together
```

---

# 6. End-to-end flow: adding a city

Let us walk through exactly what happens when you add a city from the browser.

## Step 1: You open the frontend

You visit:

```text
http://localhost:4200
```

That is the Angular frontend.

The frontend is served by Nginx inside the frontend Docker container.

## Step 2: Angular loads the city list

When the Angular component starts, this function runs:

```typescript
ngOnInit(): void {
  this.loadCities();
}
```

That means:

```text
When page opens, ask backend for the current list of cities.
```

## Step 3: Angular calls the backend

In `city.service.ts`, this function calls the backend:

```typescript
listCities(): Observable<City[]> {
  return this.http.get<City[]>(`${this.apiBaseUrl}/cities`);
}
```

The backend URL is configured in:

```text
frontend/src/environments/environment.ts
```

It points to:

```text
http://localhost:8000
```

So Angular calls:

```text
GET http://localhost:8000/cities
```

## Step 4: You type a city name

You type something like:

```text
Paris
```

and click Add city.

The Angular form is in:

```text
frontend/src/app/app.component.html
```

The submit action calls:

```typescript
addCity()
```

## Step 5: Angular sends POST /cities

The frontend service runs:

```typescript
addCity(name: string): Observable<CreateCityResponse> {
  return this.http.post<CreateCityResponse>(`${this.apiBaseUrl}/cities`, { name });
}
```

That sends JSON:

```json
{
  "name": "Paris"
}
```

to:

```text
POST http://localhost:8000/cities
```

## Step 6: FastAPI receives the request

In `backend/app/main.py`, this function handles the request:

```python
@app.post("/cities", response_model=CityCreateResponse, status_code=status.HTTP_201_CREATED)
def create_city(payload: CityCreate, db: Session = Depends(get_db)) -> CityCreateResponse:
```

This means:

```text
When someone sends POST /cities, run create_city().
```

## Step 7: FastAPI validates the input

The input schema is in `schemas.py`:

```python
class CityCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
```

This means the city name must exist and cannot be too long.

Then the backend trims whitespace:

```python
city = City(name=payload.name.strip())
```

So if you type:

```text
   Paris   
```

it stores:

```text
Paris
```

## Step 8: FastAPI saves the city in the database

The backend creates a `City` object:

```python
city = City(name=payload.name.strip())
```

Then it adds it to the database session:

```python
db.add(city)
```

Then it commits:

```python
db.commit()
```

Commit means:

```text
Actually save this change in the database.
```

## Step 9: FastAPI starts a Celery task

After saving the city, this line runs:

```python
task = update_weather_for_city.delay(city.id)
```

This is very important.

`delay(...)` means:

```text
Do not run this function here right now.
Send a job message to Celery.
```

FastAPI is saying:

```text
Celery, please update weather for city with this id.
```

## Step 10: FastAPI returns quickly

FastAPI returns a response like:

```json
{
  "id": 2,
  "name": "Paris",
  "latest_weather": null,
  "task_id": "some-celery-task-id"
}
```

Why is `latest_weather` null?

Because the city was saved immediately, but the weather worker may not have finished yet.

This is normal.

---

# 7. End-to-end flow: background weather update

Now let us follow the Celery side.

## Step 1: Redis receives the job

When FastAPI calls:

```python
update_weather_for_city.delay(city.id)
```

a message goes to Redis.

Redis is acting like a queue.

A queue is like a line of tasks:

```text
Task 1: update city 2
Task 2: update city 3
Task 3: update city 4
```

## Step 2: Celery worker takes the job

The Celery worker is a separate process.

In Docker Compose it is called:

```text
celery_worker
```

The worker is started with:

```bash
celery -A app.celery_app.celery_app worker --loglevel=info
```

That means:

```text
Start Celery worker using the Celery app defined in backend/app/celery_app.py.
```

## Step 3: Celery runs update_weather_for_city

The task is in `backend/app/tasks.py`:

```python
@celery_app.task(name="app.tasks.update_weather_for_city", autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def update_weather_for_city(city_id: int) -> dict:
```

This means:

```text
This function can be run as a Celery background task.
```

The retry settings mean:

```text
If something fails, like the weather API is temporarily unavailable, retry up to 3 times.
```

## Step 4: The task opens a database session

Inside the task:

```python
db = SessionLocal()
```

The task needs its own database session because it is not running inside a FastAPI request.

## Step 5: The task loads the city

```python
city = db.get(City, city_id)
```

This asks the database:

```text
Find the city with this id.
```

If the city does not exist:

```python
return {"status": "not_found", "city_id": city_id}
```

## Step 6: The task calls the weather client

```python
weather = fetch_weather_for_city(city.name)
```

This function is in:

```text
backend/app/weather_client.py
```

## Step 7: The weather client geocodes the city

The app first calls Open-Meteo's geocoding API.

Why?

Weather APIs often need latitude and longitude, not just a city name.

So the app asks:

```text
What are the coordinates for Paris?
```

The result contains something like:

```text
latitude: 48.8534
longitude: 2.3488
```

## Step 8: The weather client fetches current weather

Then it calls Open-Meteo forecast API with:

```text
latitude
longitude
current temperature
current humidity
weather code
```

Open-Meteo returns machine-readable data.

For example:

```json
{
  "current": {
    "temperature_2m": 20.1,
    "relative_humidity_2m": 60,
    "weather_code": 2
  }
}
```

## Step 9: The app converts weather code to text

Weather APIs often use numeric codes.

The code has a dictionary:

```python
WEATHER_CODE_DESCRIPTIONS = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    ...
}
```

So if Open-Meteo returns:

```text
2
```

The app displays:

```text
partly cloudy
```

## Step 10: Celery saves a weather record

Back in `tasks.py`, Celery creates a `WeatherData` object:

```python
weather_record = WeatherData(
    city_id=city.id,
    temperature=weather.temperature,
    humidity=weather.humidity,
    description=weather.description,
    raw_payload=weather.raw_payload,
)
```

Then it saves it:

```python
db.add(weather_record)
db.commit()
```

Now the database has a weather snapshot.

---

# 8. End-to-end flow: listing cities

When the frontend wants to show cities, it calls:

```text
GET /cities
```

In `main.py`:

```python
@app.get("/cities", response_model=list[CityRead])
def list_cities(db: Session = Depends(get_db)) -> list[CityRead]:
    cities = db.query(City).order_by(City.name.asc()).all()
    return [_city_to_read(db, city) for city in cities]
```

This means:

1. Get all cities from the database.
2. Sort them by name.
3. For each city, attach the latest weather.
4. Return JSON to the frontend.

The helper function is:

```python
def _latest_weather(db: Session, city_id: int) -> WeatherSummary | None:
```

It queries `WeatherData` records for one city and sorts by newest first:

```python
.order_by(WeatherData.fetched_at.desc(), WeatherData.id.desc())
.first()
```

That means:

```text
Give me the most recent weather record for this city.
```

If no weather exists yet, return `None`.

In JSON, Python `None` becomes JSON `null`.

---

# 9. End-to-end flow: manual update

When the user clicks Update Weather, Angular calls:

```text
POST /cities/{city_id}/update-weather
```

The backend function is:

```python
@app.post("/cities/{city_id}/update-weather", response_model=WeatherUpdateResponse, status_code=status.HTTP_202_ACCEPTED)
def manual_update_weather(city_id: int, db: Session = Depends(get_db)) -> WeatherUpdateResponse:
```

It does this:

1. Check if the city exists.
2. If not, return 404.
3. If yes, queue a Celery task.
4. Return status `queued`.

It does not fetch the weather directly.

That is the whole point: weather fetching belongs to Celery.

---

# 10. Backend file-by-file explanation

## 10.1 backend/pyproject.toml

This file describes the Python backend package.

Important dependencies:

```text
fastapi              web API framework
uvicorn              server that runs FastAPI
sqlalchemy           database ORM
psycopg              PostgreSQL driver
celery               background task system
redis                Redis client for Celery
requests             HTTP client for Open-Meteo
pydantic-settings    environment variable configuration
pytest               test runner
httpx                needed by FastAPI TestClient
```

Think of `pyproject.toml` as Python's project recipe.

## 10.2 backend/app/config.py

This file reads configuration values.

Configuration means values that may change depending on where the app runs.

Examples:

```text
database URL
Redis URL
CORS origins
weather request timeout
```

Why not hardcode everything?

Because local development, Docker, staging, and production often use different databases or URLs.

This project uses Pydantic Settings:

```python
class Settings(BaseSettings):
```

That means settings can come from environment variables.

Example:

```text
DATABASE_URL=postgresql+psycopg://weather:weather@db:5432/weather
```

## 10.3 backend/app/database.py

This file connects SQLAlchemy to the database.

Important pieces:

```python
engine = create_engine(settings.database_url, ...)
```

The engine knows how to connect to PostgreSQL.

```python
SessionLocal = sessionmaker(...)
```

A session is like a conversation with the database.

```python
def get_db():
```

This is used by FastAPI endpoints. It gives each request a database session and closes it when done.

```python
def init_db():
```

This creates the database tables.

For a bigger production app, you would usually use migrations with Alembic. For this small study project, automatic table creation is simpler.

## 10.4 backend/app/models.py

This file defines database tables as Python classes.

### City model

```python
class City(Base):
    __tablename__ = "cities"
```

This creates a table called:

```text
cities
```

Important columns:

```text
id          unique number for each city
name        city name
created_at  when the city was created
```

The unique constraint:

```python
UniqueConstraint("name", name="uq_cities_name")
```

means you cannot add the exact same city name twice.

### WeatherData model

```python
class WeatherData(Base):
    __tablename__ = "weather_data"
```

This creates a table called:

```text
weather_data
```

Important columns:

```text
id            unique number for each weather record
city_id       points to the city this weather belongs to
temperature   temperature value
humidity      humidity percentage
description   text like clear sky, overcast, rain
raw_payload   original API response saved as JSON
fetched_at    when weather was fetched
```

### Relationship

A city can have many weather records.

```text
City 1 -> Weather record 1
City 1 -> Weather record 2
City 1 -> Weather record 3
```

That is why the app can store snapshots over time.

## 10.5 backend/app/schemas.py

Schemas define what data comes in and goes out of the API.

They are Pydantic models.

Why schemas matter:

- they validate input
- they document output
- they keep responses predictable
- FastAPI uses them for `/docs`

Important schemas:

```text
CityCreate             input when creating a city
WeatherSummary         output weather shown in city list
CityRead               output city shape
CityCreateResponse     output after creating city
WeatherUpdateResponse  output after manual update request
```

## 10.6 backend/app/main.py

This is the main FastAPI app.

It defines the API routes.

### App creation

```python
app = FastAPI(title="Weather Enrichment Service", version="0.1.0")
```

This creates the FastAPI application.

### CORS middleware

```python
app.add_middleware(CORSMiddleware, ...)
```

CORS is a browser security rule.

The frontend runs at:

```text
http://localhost:4200
```

The backend runs at:

```text
http://localhost:8000
```

Because these are different origins, the backend must allow the frontend to call it.

That is what CORS does here.

### Health endpoint

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

This is a simple endpoint used to check that the backend is alive.

### Create city endpoint

```python
@app.post("/cities")
```

Saves city and queues Celery task.

### List cities endpoint

```python
@app.get("/cities")
```

Returns all cities with latest weather.

### Manual update endpoint

```python
@app.post("/cities/{city_id}/update-weather")
```

Queues a new weather update for one city.

## 10.7 backend/app/celery_app.py

This file creates the Celery app.

Celery needs to know:

```text
broker URL: where jobs are sent
backend URL: where task results are stored
included task modules: where task functions are located
```

The broker is Redis.

The worker imports tasks from:

```text
app.tasks
```

## 10.8 backend/app/tasks.py

This file contains the background job.

The task is:

```python
update_weather_for_city(city_id: int)
```

It does exactly one job:

```text
Given a city id, fetch weather and save it.
```

That is a good design because it is small and easy to understand.

## 10.9 backend/app/weather_client.py

This file talks to the outside world.

It calls Open-Meteo.

It does not know about FastAPI.

It does not know about Angular.

It only knows:

```text
city name in -> weather result out
```

That makes it easy to understand and test later.

## 10.10 backend/app/create_db.py

This tiny file runs:

```python
init_db()
```

Docker Compose uses it before starting the backend server:

```bash
python -m app.create_db && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

That means:

```text
create tables first, then start API server
```

---

# 11. Frontend file-by-file explanation

## 11.1 frontend/package.json

This file describes the Angular project.

Important scripts:

```json
"start": "ng serve --host 0.0.0.0 --port 4200",
"build": "ng build"
```

`npm start` runs the development server.

`npm run build` creates production-ready frontend files.

## 11.2 frontend/src/main.ts

This is the frontend entry point.

It starts the Angular app:

```typescript
bootstrapApplication(AppComponent, {
  providers: [provideHttpClient()],
})
```

`provideHttpClient()` allows Angular to make HTTP calls.

## 11.3 frontend/src/environments/environment.ts

This file stores the backend URL:

```typescript
export const environment = {
  apiBaseUrl: 'http://localhost:8000',
};
```

The Angular service uses this when calling the backend.

## 11.4 frontend/src/app/city.model.ts

This file defines TypeScript interfaces.

Interfaces describe the shape of data.

Example:

```typescript
export interface City {
  id: number;
  name: string;
  latest_weather: WeatherSummary | null;
}
```

This tells TypeScript:

```text
A City has id, name, and maybe weather.
```

## 11.5 frontend/src/app/city.service.ts

This file is responsible for talking to the backend.

It has three methods:

```typescript
listCities()
addCity(name)
updateWeather(cityId)
```

This is good organization because the component does not need to know the exact URLs everywhere.

The component says:

```text
cityService.addCity(name)
```

The service knows:

```text
POST http://localhost:8000/cities
```

## 11.6 frontend/src/app/app.component.ts

This file contains the page behavior.

Important variables:

```typescript
cities: City[] = [];
isLoading = false;
isAdding = false;
errorMessage = '';
successMessage = '';
updatingCityIds = new Set<number>();
```

These variables control what the user sees.

Example:

```text
isLoading = true
```

means show loading state or disable button.

### loadCities()

Calls backend and fills the city list.

### addCity()

Validates the form, sends city name to backend, then reloads city list.

### updateWeather(city)

Calls manual update endpoint for one city.

## 11.7 frontend/src/app/app.component.html

This is the HTML template.

It contains:

- title
- add city form
- error message
- success message
- city list
- weather display
- update button

Angular template syntax examples:

```html
*ngIf="isLoading"
```

means:

```text
Only show this element if isLoading is true.
```

```html
*ngFor="let city of cities"
```

means:

```text
Repeat this HTML for every city.
```

```html
{{ city.name }}
```

means:

```text
Print the city name here.
```

## 11.8 frontend/src/app/app.component.css

This is basic styling.

It makes the UI readable but not complicated.

No complex design system. No component library. No unnecessary styling framework.

---

# 12. Docker Compose explained slowly

The file is:

```text
docker-compose.yml
```

It defines five services:

```text
db
redis
backend
celery_worker
frontend
```

## 12.1 db service

```yaml
db:
  image: postgres:16-alpine
```

This starts PostgreSQL.

`alpine` means a small Linux-based image.

Ports:

```yaml
ports:
  - "5432:5432"
```

This means:

```text
Your computer port 5432 -> container port 5432
```

PostgreSQL uses port 5432 by default.

Volume:

```yaml
volumes:
  - postgres_data:/var/lib/postgresql/data
```

This means database data is stored in a Docker volume, so it survives container restarts.

## 12.2 redis service

```yaml
redis:
  image: redis:7-alpine
```

This starts Redis.

Redis uses port 6379.

Celery uses Redis to send/receive jobs.

## 12.3 backend service

This builds from:

```text
backend/Dockerfile
```

It starts FastAPI with Uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Before that, it runs:

```bash
python -m app.create_db
```

So database tables are created before the server starts.

It exposes:

```text
http://localhost:8000
```

## 12.4 celery_worker service

This also builds from the backend Dockerfile because Celery uses the same Python code.

But it runs a different command:

```bash
celery -A app.celery_app.celery_app worker --loglevel=info
```

So backend and worker use the same codebase, but they are different running processes.

This is normal.

## 12.5 frontend service

This builds from:

```text
frontend/Dockerfile
```

It builds Angular, then serves the result with Nginx.

It exposes:

```text
http://localhost:4200
```

## 12.6 depends_on

Docker Compose uses `depends_on` so services start in a reasonable order.

Example:

```text
backend waits for db and redis
celery_worker waits for backend and redis
frontend waits for backend
```

This does not mean the app is perfect production orchestration. It is enough for a simple local full-stack project.

---

# 13. Dockerfiles explained

## 13.1 backend/Dockerfile

The backend Dockerfile starts from Python:

```dockerfile
FROM python:3.12-slim
```

Then it:

1. Sets Python environment options.
2. Sets working directory `/app`.
3. Installs system dependency `gcc`.
4. Copies `pyproject.toml`.
5. Copies app code.
6. Installs Python package.
7. Exposes port 8000.
8. Defines default command.

The default command is overridden in Docker Compose, but it is still useful.

## 13.2 frontend/Dockerfile

The frontend Dockerfile has two stages.

### Stage 1: build Angular

```dockerfile
FROM node:24-alpine AS build
```

This installs npm packages and runs:

```bash
npm run build
```

### Stage 2: serve with Nginx

```dockerfile
FROM nginx:1.27-alpine
```

This serves the built static files.

Why two stages?

Because the final container does not need Node.js or Angular CLI. It only needs the built HTML/CSS/JS files.

This keeps the final frontend container simpler.

---

# 14. Database explained with examples

Imagine you add Rome.

The `cities` table might look like:

```text
id | name | created_at
---+------+---------------------
2  | Rome | 2026-06-01 13:00:00
```

Then Celery fetches weather.

The `weather_data` table might look like:

```text
id | city_id | temperature | humidity | description | fetched_at
---+---------+-------------+----------+-------------+---------------------
1  | 2       | 27.4        | 53       | overcast    | 2026-06-01 13:00:05
```

The `city_id` connects the weather record to the city.

That is called a foreign key.

If you update weather again later, the app does not overwrite the old record. It creates another snapshot:

```text
id | city_id | temperature | humidity | description | fetched_at
---+---------+-------------+----------+-------------+---------------------
1  | 2       | 27.4        | 53       | overcast    | 13:00:05
2  | 2       | 28.1        | 51       | clear sky   | 14:00:05
```

When listing cities, the app chooses the latest one.

---

# 15. Tests explained

Tests are in:

```text
backend/tests/test_cities_api.py
```

The tests use SQLite in memory instead of PostgreSQL.

Why?

Because tests should be fast and isolated.

The app itself is designed for PostgreSQL in Docker, but the API logic can be tested with an in-memory database.

## 15.1 TestClient

FastAPI has a `TestClient` that can call the API without starting a real server.

Example:

```python
response = client.post("/cities", json={"name": "Kyiv"})
```

This behaves like an HTTP request, but inside the test process.

## 15.2 monkeypatch

The tests do not want to really call Celery.

So they replace:

```python
update_weather_for_city.delay
```

with a fake function.

This fake function records that a task would have been queued.

That lets the test prove:

```text
Creating a city queues a task.
```

without needing Redis or Celery during the test.

## 15.3 What the tests cover

The tests check:

1. Creating a city saves it and queues weather task.
2. Listing cities returns latest weather.
3. Manual update queues weather task.
4. Manual update returns 404 if city does not exist.

That covers the core backend behavior.

---

# 16. Why this is asynchronous

A normal synchronous flow would be:

```text
User clicks Add city
Backend saves city
Backend calls weather API
Backend waits
Backend saves weather
Backend responds
```

Problem:

```text
The user waits while the weather API responds.
```

If the weather API is slow, the app feels slow.

If the weather API is down, adding a city may fail.

The asynchronous flow is:

```text
User clicks Add city
Backend saves city
Backend queues task
Backend responds quickly
Celery fetches weather separately
```

This is better because:

- user gets quick response
- slow work happens separately
- Celery can retry failures
- backend stays focused on API requests

---

# 17. Important commands

## Start the whole app with the launcher scripts

The project now includes two start scripts in the root folder:

```text
start_wes.sh   for Linux/macOS
start_wes.bat  for Windows
```

These scripts are meant for portability. If you copy the whole `WES` folder to another computer that has Docker installed, you can start the project without remembering the Docker command.

Target computer requirements:

- Windows/macOS: Docker Desktop installed and running.
- Linux: Docker Engine and Docker Compose plugin installed and running.
- Ports `4200`, `8000`, `5432`, and `6379` should be free.

You do not need local Python, Node, Angular CLI, PostgreSQL, Redis, or Celery when using these scripts. Docker handles those inside containers.

Linux/macOS:

```bash
./start_wes.sh
```

Windows:

```text
Double-click start_wes.bat
```

What the scripts do:

1. Go to the project folder automatically.
2. Check that Docker exists.
3. Check that Docker is running.
4. Find Docker Compose.
5. Create `.env` from `.env.example` if `.env` does not exist.
6. Run `docker compose up -d --build`.
7. Wait for the backend health endpoint.
8. Open the frontend in your browser.

## Start the whole app manually

If you do not want to use the launcher scripts, run:
```bash
cd WES
cp .env.example .env

# On Windows PowerShell, use this instead of cp:
# Copy-Item .env.example .env

docker compose up --build
```

## Start in background

```bash
docker compose up -d --build
```

## See running services

```bash
docker compose ps
```

## See backend logs

```bash
docker compose logs -f backend
```

## See Celery logs

```bash
docker compose logs -f celery_worker
```

## Stop containers

```bash
docker compose down
```

## Stop containers and delete database data

```bash
docker compose down -v
```

## Open frontend

```text
http://localhost:4200
```

## Open API docs

```text
http://localhost:8000/docs
```

## Check backend health

```bash
curl http://localhost:8000/health
```

## List cities

```bash
curl http://localhost:8000/cities
```

## Add a city

```bash
curl -X POST http://localhost:8000/cities \
  -H 'Content-Type: application/json' \
  -d '{"name":"Paris"}'
```

## Manually update weather

```bash
curl -X POST http://localhost:8000/cities/1/update-weather
```

---

# 18. How to study the app in order

Recommended study order:

## Step 1: Run it

Open:

```text
http://localhost:4200
```

Add a city.

See what happens.

## Step 2: Watch logs

Open another terminal:

```bash
cd /home/stirkolo/Documents/WES
docker compose logs -f celery_worker
```

Add another city.

Watch Celery receive the job.

## Step 3: Read frontend service

Read:

```text
frontend/src/app/city.service.ts
```

Understand the three HTTP calls.

## Step 4: Read backend routes

Read:

```text
backend/app/main.py
```

Match each frontend call to a backend route.

## Step 5: Read the task

Read:

```text
backend/app/tasks.py
```

Understand how the weather update works.

## Step 6: Read the weather client

Read:

```text
backend/app/weather_client.py
```

Understand the two external API calls.

## Step 7: Read the models

Read:

```text
backend/app/models.py
```

Understand the two database tables.

## Step 8: Read Docker Compose

Read:

```text
docker-compose.yml
```

Understand how all processes connect.

---

# 19. Common beginner confusions

## 19.1 Why is latest_weather sometimes null?

Because the city is saved before weather is fetched.

The sequence is:

```text
save city -> return response -> worker fetches weather later
```

So for a few seconds, weather may not exist yet.

Click Refresh list after a short wait.

## 19.2 Why are there two backend-like containers?

There is:

```text
backend
celery_worker
```

They use the same code, but run different commands.

`backend` runs FastAPI.

`celery_worker` runs Celery.

They are separate because web requests and background jobs are different jobs.

## 19.3 Why does the frontend not call Open-Meteo directly?

It could, but that would be a different architecture.

This project is about backend enrichment.

The backend owns:

- data saving
- task queueing
- weather fetching
- data consistency

The frontend only displays and sends user actions.

## 19.4 Why use Redis if PostgreSQL already stores data?

PostgreSQL stores permanent data.

Redis is used as a temporary job queue.

They have different jobs:

```text
PostgreSQL = memory of the app
Redis      = task message queue
```

## 19.5 Why not just call the task function directly?

Because calling directly would run it inside the FastAPI request.

This:

```python
update_weather_for_city(city.id)
```

would be synchronous.

This:

```python
update_weather_for_city.delay(city.id)
```

queues it asynchronously.

## 19.6 Why does Docker Compose expose ports?

Containers are isolated.

Ports let your browser or terminal reach them.

```text
4200 -> frontend
8000 -> backend
5432 -> PostgreSQL
6379 -> Redis
```

## 19.7 What is Uvicorn?

Uvicorn is the server process that runs FastAPI.

FastAPI is the app framework.

Uvicorn is what listens on port 8000 and handles HTTP traffic.

## 19.8 What is Nginx?

Nginx is a web server.

In this project it serves the built Angular files.

The browser downloads HTML, CSS, and JavaScript from Nginx.

---

# 20. Limitations of this project

This project is intentionally simple.

It does not include:

- user login
- authentication
- authorization
- database migrations
- frontend polling
- WebSockets
- edit/delete city
- weather history charts
- production secrets management
- production deployment setup

These are not missing by accident. They are omitted to keep the assignment simple and explainable.

---

# 21. Possible improvements later

If you want to extend the project later, good next steps would be:

1. Add Alembic migrations.
2. Add delete city endpoint.
3. Add weather history page.
4. Add automatic frontend polling while weather is pending.
5. Add better duplicate city handling, maybe case-insensitive.
6. Add unit tests for `weather_client.py` with mocked API responses.
7. Add frontend tests.
8. Add pagination if many cities are stored.
9. Add authentication if multiple users use it.
10. Add production-ready environment/secrets handling.

Do not add these until you understand the current project.

---

# 22. Final simple summary

If you remember only one thing, remember this:

```text
Angular is the user interface.
FastAPI is the API.
PostgreSQL stores cities and weather.
Redis carries background job messages.
Celery performs background weather fetching.
Open-Meteo provides weather data.
Docker Compose starts everything together.
```

The main flow is:

```text
User adds city
-> Angular sends POST /cities
-> FastAPI saves City
-> FastAPI queues Celery task
-> Celery gets task from Redis
-> Celery calls Open-Meteo
-> Celery saves WeatherData
-> Angular refreshes GET /cities
-> User sees latest weather
```

That is the Weather Enrichment Service.
