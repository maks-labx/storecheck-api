# StoreCheck API

StoreCheck API is a backend REST API for store inspections, defect tracking, and repair request management.

The project is based on a simplified real-world business process: an inspector checks a store, fills out inspection data, records detected defects, and managers can later create repair requests based on those defects.

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Docker
* Docker Compose

## Project Status

The project is currently in active development.

Planned core features:

* Store inspections
* Checklist items
* Inspection answers
* Defect tracking
* Repair requests
* JWT authentication
* Permissions
* Filtering, search, and ordering
* Swagger/OpenAPI documentation
* API tests

## Local Development

The project is intended to run with Docker Compose.

Build and start containers:

```bash
docker compose up --build
```

Run Django commands inside the web container:

```bash
docker compose exec web python manage.py migrate
```

```bash
docker compose exec web python manage.py createsuperuser
```

## Author

Maks
