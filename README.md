# StoreCheck API

StoreCheck API is a backend REST API for store inspections, checklist-based reports, defect tracking, and maintenance ticket management.

The project is based on a simplified real-world business process: an engineer inspects a store, submits a checklist report, marks each checklist item as OK or Problem, and the system automatically creates maintenance tickets for all detected problems.

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Docker
* Docker Compose
* drf-spectacular / OpenAPI / Swagger
* django-filter

## Main Features

* Company structure management:

  * employees
  * clusters
  * contractors
  * stores
* Inspection checklist management:

  * checklist sections
  * checklist items
  * active/inactive checklist items
* Inspection report submission endpoint
* Validation rules for inspection reports:

  * problem items require a description
  * OK items should not contain a description
  * all active checklist items must be submitted
* Automatic maintenance ticket creation from problem inspection results
* Ticket status tracking:

  * new
  * in progress
  * done
  * cancelled
* Ticket overdue detection
* API pagination
* Filtering, search, and ordering for list endpoints
* Basic API permissions:

  * public read access
  * authenticated write access
* OpenAPI documentation with Swagger UI and ReDoc
* Tests for the main inspection report submission flow

## Business Flow

```text
Engineer opens an inspection checklist
↓
Engineer checks each active checklist item
↓
Each item is marked as OK or Problem
↓
If the item is marked as Problem, description is required
↓
Engineer submits the report
↓
The backend creates:
    - Inspection
    - Inspection item results
    - Maintenance tickets for all problem items
```

## API Documentation

After running the project locally, API documentation is available at:

```text
http://127.0.0.1:8000/api/schema/swagger-ui/
```

ReDoc documentation:

```text
http://127.0.0.1:8000/api/schema/redoc/
```

Raw OpenAPI schema:

```text
http://127.0.0.1:8000/api/schema/
```

## Main API Endpoints

### Company

```text
GET /api/employees/
GET /api/clusters/
GET /api/contractors/
GET /api/stores/
```

### Checklist and Inspections

```text
GET /api/checklist-sections/
GET /api/checklist-items/
GET /api/inspections/
GET /api/inspection-results/
POST /api/inspections/submit-report/
```

### Tickets

```text
GET /api/tickets/
GET /api/tickets/{id}/
PATCH /api/tickets/{id}/
```

## Submit Inspection Report Example

```json
{
  "store": 1,
  "inspector": 3,
  "results": [
    {
      "checklist_item": 1,
      "status": "ok",
      "description": ""
    },
    {
      "checklist_item": 2,
      "status": "problem",
      "description": "Broken floor tiles near the entrance."
    }
  ]
}
```

Successful response example:

```json
{
  "inspection": {
    "id": 1,
    "store": 1,
    "store_number": 101,
    "inspector": 3,
    "inspector_name": "Mike Engineer",
    "submitted_at": "2026-06-15T12:00:00Z"
  },
  "tickets_created": 1,
  "tickets": [
    {
      "id": 1,
      "ticket_number": "000001",
      "title": "Sales floor / Floor",
      "due_date": "2026-06-18"
    }
  ]
}
```

## Filtering, Search, and Ordering Examples

Filter tickets by status:

```text
GET /api/tickets/?status=new
```

Search tickets by ticket number, title, description, or related data:

```text
GET /api/tickets/?search=floor
```

Order tickets by due date:

```text
GET /api/tickets/?ordering=due_date
```

Search stores by address or store number:

```text
GET /api/stores/?search=Chicago
```

Filter inspections by store:

```text
GET /api/inspections/?store=1
```

## Local Development

The project is intended to run with Docker Compose.

Clone the repository:

```bash
git clone https://github.com/maks-labx/storecheck-api.git
cd storecheck-api
```

Build and start containers:

```bash
docker compose up --build
```

Run migrations:

```bash
docker compose exec web python manage.py migrate
```

Create a superuser:

```bash
docker compose exec web python manage.py createsuperuser
```

Run the project:

```bash
docker compose up
```

The API will be available at:

```text
http://127.0.0.1:8000/api/
```

## Running Tests

Run all tests:

```bash
docker compose exec web python manage.py test
```

Or run tests in a temporary container:

```bash
docker compose run --rm web python manage.py test
```

## Project Structure

```text
apps/
  company/
    models.py
    serializers.py
    views.py
    urls.py
  inspections/
    models.py
    serializers.py
    views.py
    urls.py
  tickets/
    models.py
    serializers.py
    views.py
    urls.py
    services.py
config/
  settings.py
  urls.py
```

## Future Improvements

* Manual ticket creation by store directors and engineers
* JWT authentication
* Role-based permissions
* Photo attachments for inspection problems and tickets
* Ticket comments and history
* More detailed ticket lifecycle
* Production deployment
* Extended test coverage

## Author

Maks
