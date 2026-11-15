# FieldShift FarmOS - Quick Start Guide

## Starting the Application

### Method 1: Use Startup Script (Recommended)
```bash
# From project root
start-dev.bat
```

This will:
- Check for port conflicts
- Start backend on port 8000
- Start frontend on port 3000
- Open both in separate windows

### Method 2: Manual Startup
```bash
# Terminal 1 - Backend
cd "C:\Users\acer\Nasa challenge\backend"
python -m uvicorn main:app --reload --port 8000

# Terminal 2 - Frontend  
cd "C:\Users\acer\Nasa challenge\frontend"
npm run dev
```

## Stopping the Application

### Method 1: Use Stop Script (Recommended)
```bash
stop-dev.bat
```

### Method 2: Manual
- Close the terminal windows
- Or press Ctrl+C in each terminal

## Access Points

| Service | URL |
|---------|-----|
| **Dashboard** | http://localhost:3000 |
| **API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

## Common Issues

### "Styles are missing"
- Hard refresh: **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)

### "Port already in use"
```bash
stop-dev.bat
# Wait 5 seconds
start-dev.bat
```

### "Map doesn't load"
- Wait 10 seconds for tiles to download
- Check internet connection

## Project Structure

```
C:\Users\acer\Nasa challenge\
├── backend/              # FastAPI server
│   ├── main.py          # API entry point
│   ├── routers/         # API endpoints
│   └── services/        # Business logic (NASA POWER, water balance)
│
├── frontend/            # Next.js app
│   ├── src/app/         # App Router pages
│   ├── src/components/  # React components
│   └── src/lib/         # Config and utilities
│
├── start-dev.bat        # Start servers
├── stop-dev.bat         # Stop servers
└── VERIFICATION_COMPLETE.md  # Full documentation
```

## Key Features

1. **Farm Creation** - Click map to add farms
2. **NASA Climate Data** - Real historical weather analysis
3. **Calculate Water Needs** - Crop water balance model
4. **Compare 3 Crop Plans** - Rotation strategy comparison
5. **FlipPoint Analysis** - Sensitivity analysis tool
6. **Smart Farm Simulator** - ESP32 sensor simulation
7. **Ground Truth Lab** - Evidence collection and validation

## Need Help?

- Full documentation: `VERIFICATION_COMPLETE.md`
- Troubleshooting: `STARTUP_FIX_REPORT.md`
- API details: http://localhost:8000/docs (when running)
