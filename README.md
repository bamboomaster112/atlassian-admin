# Atlassian Admin Tracker

A standalone administration governance and usage tracking application for **Jira**, **Confluence**, and **Jira Service Management** (Cloud).

## Features

### Jira Tracking
- **User Activity** — track who creates, resolves, and updates issues; identify inactive users
- **Custom Fields** — audit all custom fields, find unused/low-usage fields, get cleanup recommendations
- **Workflows & Schemes** — view all workflows, permission schemes, notification schemes, issue type schemes
- **Projects** — project-level analytics, active user counts, last activity dates

### Confluence Tracking
- **Space Analytics** — page counts, blog posts, attachment sizes, permissions per space
- **Content Analytics** — recently updated pages, stale content (1yr+), top contributors, label usage

### Jira Service Management
- **Service Desk Overview** — all desks with request type counts, queues, and customer counts
- **Request Types & Queues** — per-desk breakdown of request types with field mappings and queue depths

### Admin Governance
- **License Usage** — active vs inactive users across all products
- **Permissions Audit** — cross-product review of Jira global/project and Confluence space permissions
- **Cleanup Recommendations** — unused custom fields, stale Confluence pages, inactive projects, empty spaces

## Architecture

```
backend/          Python FastAPI backend
  app/
    api/routes/   REST API endpoints
    services/     Business logic (jira/, confluence/, jsm/, governance/)
    models/       Pydantic schemas
    core/         Config, Atlassian HTTP client, database

frontend/         React (Vite) dashboard
  src/
    pages/        Route-level page components
    components/   Shared UI (sidebar, metrics, tables)
    services/     API client
    hooks/        React hooks

docker/           Docker configuration
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- An Atlassian Cloud site with an API token ([create one here](https://id.atlassian.com/manage-profile/security/api-tokens))

### 1. Configure credentials

```bash
cp .env.example .env
# Edit .env with your Atlassian domain, email, and API token
```

### 2. Run the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. Interactive docs at `/docs`.

### 3. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

The dashboard is available at `http://localhost:3000`.

### Docker Compose (alternative)

```bash
cp .env.example .env    # configure credentials
docker compose up --build
```

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## API Endpoints

| Category | Endpoint | Description |
|---|---|---|
| Dashboard | `GET /api/dashboard/` | Top-level metrics |
| Jira Users | `GET /api/jira/users` | All users |
| | `GET /api/jira/users/activity-summary?days=30` | Activity summary |
| | `GET /api/jira/users/inactive?days=90` | Inactive users |
| Custom Fields | `GET /api/jira/custom-fields` | All custom fields |
| | `GET /api/jira/custom-fields/unused` | Unused fields |
| | `GET /api/jira/custom-fields/{id}/usage` | Field usage detail |
| Schemes | `GET /api/jira/schemes` | All workflows & schemes |
| Projects | `GET /api/jira/projects` | All projects |
| | `GET /api/jira/projects/{key}` | Project detail |
| Confluence | `GET /api/confluence/spaces` | All spaces |
| | `GET /api/confluence/spaces/growth-summary` | Space growth |
| | `GET /api/confluence/content/recent` | Recent updates |
| | `GET /api/confluence/content/stale` | Stale pages |
| | `GET /api/confluence/content/top-contributors` | Contributors |
| | `GET /api/confluence/content/labels` | Label usage |
| JSM | `GET /api/jsm/overview` | All desks overview |
| | `GET /api/jsm/service-desks/{id}` | Desk detail |
| | `GET /api/jsm/service-desks/{id}/request-types` | Request types |
| | `GET /api/jsm/service-desks/{id}/queues` | Queues |
| Governance | `GET /api/governance/licenses` | License summary |
| | `GET /api/governance/permissions/audit` | Full audit |
| | `GET /api/governance/cleanup` | Recommendations |

## License

MIT
