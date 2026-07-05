# StoreCheck API

StoreCheck API is a backend REST API for store inspections, checklist-based reports, defect tracking, and maintenance ticket management.

The project is based on a simplified real-world business process: an engineer inspects a store, submits a checklist report, marks each checklist item as OK or Problem, and the system automatically creates maintenance tickets for all detected problems. Store directors can also create manual maintenance tickets for their own stores.

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* Docker
* Docker Compose
* drf-spectacular / OpenAPI / Swagger
* django-filter
* djangorestframework-simplejwt

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
* JWT authentication
* Employee accounts linked to Django users
* Role-based access control:

  * authenticated users can access internal API data
  * only engineers can submit inspection reports
  * store directors can create manual tickets for their own stores
  * store directors can close tickets for their own stores
  * admin/staff users can manage reference data and tickets
* Inspection report submission endpoint
* Validation rules for inspection reports:

  * problem items require a description
  * OK items should not contain a description
  * all active checklist items must be submitted
* Automatic maintenance ticket creation from problem inspection results
* Manual maintenance ticket creation by store directors and admin/staff users
* Ticket status tracking:

  * open
  * closed
* Ticket overdue detection based on due date
* API pagination
* Filtering, search, and ordering for list endpoints
* OpenAPI documentation with Swagger UI and ReDoc
* Tests for the main inspection report submission flow, authentication, permissions, reference data access rules, ticket status permissions, and manual ticket creation

## Business Flow

### Inspection-based ticket creation

```text
Engineer authenticates with JWT
↓
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
The backend determines the inspector from the authenticated user
↓
The backend creates:
    - Inspection
    - Inspection item results
    - Maintenance tickets for all problem items
```

### Manual ticket creation

```text
Store director authenticates with JWT
↓
Store director creates a manual maintenance ticket for their own store
↓
The backend determines the creator from the authenticated user
↓
The backend automatically assigns:
    - responsible engineer from the store
    - contractor from the store
    - open ticket status
↓
Manual tickets are created without an inspection result
```

## Authentication and Permissions

The API uses JWT authentication.

Token endpoints:

```text
POST /api/token/
POST /api/token/refresh/
```

Example token request:

```json
{
  "username": "engineer",
  "password": "your-password"
}
```

Use the returned access token in the Authorization header:

```text
Authorization: Bearer <access_token>
```

Permission rules:

```text
Anonymous users:
    - cannot access internal API endpoints

Authenticated users:
    - can view internal API data

Engineers:
    - can submit inspection reports
    - cannot create manual tickets
    - cannot close tickets

Store directors:
    - can create manual tickets for their own store
    - can close tickets for their own store

Admin/staff users:
    - can create, update, and delete reference data
    - can create manual tickets for any store
    - can update ticket status
```

The inspector is not submitted by the client. It is automatically determined from the authenticated Django user linked to an Employee record.

For manual tickets, the creator is also determined from the authenticated Django user linked to an Employee record.

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

### Authentication

```text
POST /api/token/
POST /api/token/refresh/
```

### Company

```text
GET /api/employees/
GET /api/clusters/
GET /api/contractors/
GET /api/stores/
```

Admin/staff users can also create, update, and delete company reference data.

### Checklist and Inspections

```text
GET /api/checklist-sections/
GET /api/checklist-items/
GET /api/inspections/
GET /api/inspection-results/
POST /api/inspections/submit-report/
```

Admin/staff users can create, update, and delete checklist sections and checklist items.

Only engineers can submit inspection reports.

### Tickets

```text
GET /api/tickets/
POST /api/tickets/
GET /api/tickets/{id}/
PATCH /api/tickets/{id}/
```

Store directors can create manual tickets only for their own store. Admin/staff users can create manual tickets for any store.

Store directors can close tickets only for their own store. Admin/staff users can update ticket status for any store.

## Submit Inspection Report Example

The inspector is determined automatically from the authenticated user.

```json
{
  "store": 1,
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

## Manual Ticket Creation Example

Manual tickets are created without an inspection result. The client sends only the store, title, description, and due date.

```json
{
  "store": 1,
  "title": "Broken entrance door",
  "description": "The entrance door does not close properly.",
  "due_date": "2026-07-10"
}
```

Successful response example:

```json
{
  "id": 2,
  "ticket_number": "000002",
  "source_result": null,
  "title": "Broken entrance door",
  "description": "The entrance door does not close properly.",
  "store": 1,
  "store_number": 101,
  "created_by": 4,
  "created_by_name": "John Director",
  "responsible_engineer": 3,
  "responsible_engineer_name": "Mike Engineer",
  "contractor": 1,
  "contractor_name": "FixIt Ltd",
  "status": "open",
  "created_at": "2026-07-05T12:00:00Z",
  "due_date": "2026-07-10",
  "is_overdue": false
}
```

For manually created tickets, `source_result` is `null`.

The backend automatically sets:

```text
created_by = authenticated user's employee
responsible_engineer = store.responsible_engineer
contractor = store.contractor
status = open
```

## Ticket Statuses

Tickets use a simplified status workflow:

```text
open
closed
```

A new ticket is created with the `open` status.

Tickets can be created in two ways:

```text
1. Automatically from problem inspection results
2. Manually by store directors or admin/staff users
```

Inspection-based tickets have a linked `source_result`.

Manual tickets have:

```text
source_result = null
```

A ticket is considered overdue when:

```text
status is not closed
and
current date is later than due_date
```

Overdue state is calculated automatically and is not stored as a separate status.

## Filtering, Search, and Ordering Examples

Filter tickets by status:

```text
GET /api/tickets/?status=open
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

Run Django system checks:

```bash
docker compose run --rm web python manage.py check
```

## Project Structure

```text
apps/
  common/
    permissions.py
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
    permissions.py
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

* Photo attachments for inspection problems and tickets
* Ticket comments and history
* Demo data management command
* Production deployment
* Extended test coverage

## Author

Maks
