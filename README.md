# Project: Image Pipeline (AI + Feed + React Dashboard)

Containerized, end-to-end image classification pipeline composed of three services:

- AI Classification Service (Python): accepts an image, preprocesses it, and returns a predicted class and confidence.
- Feed Service (Python): selects source images, calls the AI service, and stores the latest results.
- Dashboard Web (React): displays the latest classified image and prediction via a simple web UI.

All components run with Docker Compose; runtime artifacts are shared through a Docker volume.

---

## Architecture

Data flow:
1) Feed Service selects a random image from `images/`.
2) Sends the image to AI Classification Service via `POST /predict`.
3) AI responds with `{ "class": "<label>", "confidence": 0.92 }`.
4) Feed Service writes `latest.jpg` and `latest.json` into `shared/`.
5) React dashboard fetches results from the Feed Service and updates the UI.

Notes:
- The dashboard retrieves data via HTTP only; it does not access the shared volume directly.
- The shared volume provides a consistent “latest result” for backend coordination.

---

## Services

### 1) AI Classification Service
- Endpoint: `POST /predict`
- Responsibilities:
	- Validate input; return clear errors for invalid files
	- Preprocess (resize, normalization, tensor creation)
	- Execute a pre-trained model (e.g., ResNet18)
	- Return classification results as JSON

### 2) Feed Service
- Responsibilities:
	- Simulate ingestion by selecting random files from `images/`
	- Send images to the AI Classification Service
	- Persist results in `shared/` as `latest.jpg` and `latest.json`
- Suggested endpoints:
	- `POST /trigger` — classify a new random image
	- `GET /latest` — latest prediction metadata
	- `GET /image/latest` — retrieve the latest processed image

### 3) Dashboard Web (React)
- Displays: most recent image, predicted class, confidence score
- Interactions: a button to trigger a new classification via the Feed Service
- Data access: communicates exclusively via HTTP to the Feed Service
- Packaging: built and served as its own Docker container

---

## Project Structure

```text
project4-image-pipeline/
│
├── docker-compose.yml          # Orchestrates all containers
│
├── ai_service/                 # AI/ML microservice (Python)
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
├── feed_service/               # Image ingestion + orchestration (Python)
│   ├── Dockerfile
│   ├── app.py
│   └── requirements.txt
│
├── dashboard_web/              # React-based dashboard
│   ├── Dockerfile
│   ├── package.json
│   ├── src/
│   └── public/
│
├── images/                     # Input images for classification
│   └── (sample .jpg/.png files)
│
└── shared/                     # Runtime output storage (mounted volume)
```

If migrating from a Flask dashboard, `dashboard_web/` replaces that component.

---

## API Contracts (summary)

### AI Classification Service
- `POST /predict`
	- Request: multipart form-data with an image file
	- Response example:
		```json
		{ "class": "<label>", "confidence": 0.92 }
		```
	- Errors: clear JSON messages for invalid inputs

### Feed Service
- `POST /trigger`
	- Processes a new image and updates shared artifacts
- `GET /latest`
	- Returns metadata describing the latest classification
- `GET /image/latest`
	- Returns the associated image for dashboard rendering

### Dashboard Web (React)
- Issues HTTP requests to the Feed Service
- No direct access to the shared volume

---

## Running the Project

### Prerequisites
- Docker Desktop (required)
- Node.js (optional, for local dashboard development)

### Execution
Start all services:

```powershell
docker compose up --build
```

The dashboard becomes available at:

```
http://localhost:<dashboard_port>
```

### Behavior
- Latest artifacts appear in the `shared/` volume
- The dashboard updates results each time the user triggers a classification

---

## Configuration
- Services communicate using container DNS names defined in `docker-compose.yml`
- Place image files inside `images/` before running
- Environment variables (paths, ports, service URLs) are defined per service