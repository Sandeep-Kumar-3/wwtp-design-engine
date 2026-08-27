# WWTP Design Studio — Professional Release 1.3

A preliminary wastewater-treatment-plant design and decision-support platform for municipal and industrial wastewater. The application combines a React/Vite engineering workspace with a FastAPI calculation engine.

## What this release provides

### User experience
- Clean, empty design-basis form on first launch — no hidden/default project values.
- Local Project Library using browser storage.
- Reopen previously generated projects and their results.
- Explicit Municipal and Industrial example templates.
- Import/export of design-basis JSON.
- Export of complete design JSON.
- Fixed header and sidebar with independent content scrolling.
- Backend health indicator in the application header.
- Print-friendly engineering report view.
- Responsive result tables, process flow, hydraulic profile and engineering-check views.

### Engineering engine
- Design-basis validation and cross-field checks.
- Municipal/industrial process selection.
- Flow and pollutant loading calculations.
- Screening and grit design.
- Primary clarification.
- Biological reactor sizing and F/M calculation.
- Aeration and oxygen-demand calculation.
- Secondary clarification.
- Tertiary filtration.
- Chlorination/disinfection.
- Sludge production and preliminary management.
- Pumps, blowers, chemicals and energy estimates.
- Equipment schedule.
- Preliminary hydraulic profile/headloss.
- BOD/COD/TSS plant-wide mass balance.
- Automated engineering checks and readiness status.
- Explicit preliminary-design limitations.

## Run on Windows

### Backend
From the project root:

```powershell
python -m pip install -r backend\requirements.txt
$env:PYTHONPATH="backend"
python -m uvicorn app.main:app --reload
```

Backend documentation:

`http://127.0.0.1:8000/docs`

### Frontend
In another terminal:

```powershell
cd frontend
npm.cmd install
npm.cmd run dev
```

Open the Vite URL shown in the terminal, normally:

`http://localhost:5173`

If PowerShell blocks `npm.ps1`, use `npm.cmd` as shown above.

## API configuration

The frontend defaults to:

`http://127.0.0.1:8000`

For another backend URL, create `frontend/.env`:

```text
VITE_API_URL=http://127.0.0.1:8000
```

## Testing

Backend regression and integration suite:

```powershell
python -m pytest -q
```

The release baseline has **81 passing backend tests**.

## Engineering status

This is a **preliminary engineering/design decision-support system**, not construction-ready design software. Final engineering requires project-specific design criteria, applicable Indian standards/guidelines, survey levels, geotechnical information, laboratory/pilot testing where applicable, detailed hydraulic calculations, equipment vendor data, electrical/instrumentation design, structural design and professional engineering review.
