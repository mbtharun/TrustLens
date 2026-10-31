# TrustLens React frontend

This is a separate Vite + React frontend. It does not replace or modify the existing FastAPI backend or the original `frontend/index.html`.

## Requirements
- Node.js 18+
- Existing FastAPI backend running on `http://127.0.0.1:8000`

## Run locally

Terminal 1 — from the TrustLens project root:

```powershell
uvicorn backend.main:app --reload
```

Terminal 2:

```powershell
cd frontend-react
npm install
npm run dev
```

Open http://127.0.0.1:5173

Vite proxies `/analyze` to the FastAPI server. The request uses multipart field `file`, matching the existing frontend integration.

## Production API
If the API is hosted on another origin, create `.env.production`:

```env
VITE_API_URL=https://your-api-host.example
```

The API host must allow browser requests from the frontend origin (CORS). Build with:

```powershell
npm run build
```

Output is written to `dist/`. The existing FastAPI homepage is not changed by this project.

## Notes
- The displayed score is a model ranking score, not a calibrated probability or authenticity verdict.
- The current API returns one composite score. No individual texture, frequency or boundary measurements are invented.
- The latest analysis is stored in this browser's IndexedDB so the results page can be refreshed locally.
