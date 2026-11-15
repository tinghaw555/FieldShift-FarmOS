# Troubleshooting Guide

## Common Issues and Solutions

### Backend Issues

#### Error: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**:
```bash
cd backend
pip install -r requirements.txt
```

#### Error: "Address already in use" (Port 8000)

**Solution**:
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with actual number)
taskkill /PID [PID] /F

# Or use a different port
python -m uvicorn main:app --reload --port 8001
```

#### Error: "No module named 'routers'"

**Solution**: Make sure you're running from the `backend` directory:
```bash
cd backend
python -m uvicorn main:app --reload
```

#### Database Error: "table already exists"

**Solution**: Delete the database and restart:
```bash
cd backend/database
del fieldshift.db
cd ..
python -m uvicorn main:app --reload
```

---

### Frontend Issues

#### Error: "Module not found" or "Cannot find package"

**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

#### Error: "Port 3000 is already in use"

**Solution**:
```bash
# Kill process on port 3000
netstat -ano | findstr :3000
taskkill /PID [PID] /F

# Or set different port
set PORT=3001 && npm run dev
```

#### Map Not Displaying

**Possible causes**:
1. Leaflet CSS not loading
2. Browser blocking map tiles
3. Network issue

**Solution**:
- Check browser console for errors
- Clear browser cache
- Try different browser
- Check internet connection

#### Blank Screen / White Screen

**Solution**:
1. Check browser console for errors
2. Verify backend is running: http://localhost:8000
3. Clear browser cache and hard reload (Ctrl+F5)
4. Check CORS errors in console

---

### Integration Issues

#### Frontend Can't Connect to Backend

**Symptoms**: API calls fail, "Network Error" in console

**Solution**:
1. Verify backend is running: http://localhost:8000
2. Check API docs: http://localhost:8000/docs
3. Verify NEXT_PUBLIC_API_BASE in frontend/.env
4. Check CORS configuration in backend/main.py

#### NASA POWER API Timeout

**Symptoms**: Climate data fails to load

**Solution**:
1. Check internet connection
2. Verify NASA POWER is accessible: https://power.larc.nasa.gov/
3. Try different location (some coordinates may have issues)
4. Increase timeout in backend/services/nasa_power.py

#### Weather Forecast Not Loading

**Symptoms**: Forecast section shows error

**Solution**:
1. Check Open-Meteo status: https://open-meteo.com/
2. Verify coordinates are valid (-90 to 90, -180 to 180)
3. Check browser console for API errors

---

### Development Issues

#### TypeScript Errors

**Solution**:
```bash
cd frontend
npm run build
# Fix any TypeScript errors shown
```

#### ESLint Warnings

Most warnings can be ignored for demo purposes. To fix:
```bash
cd frontend
npm run lint
```

#### Python Import Errors

**Solution**: Ensure you're in the correct directory and Python path is set:
```bash
cd backend
set PYTHONPATH=%CD%
python -m uvicorn main:app --reload
```

---

### Browser Issues

#### Cookies/Session Issues

**Solution**:
- Clear browser cookies
- Use incognito/private mode
- Try different browser

#### Slow Performance

**Solutions**:
1. Close other browser tabs
2. Disable browser extensions
3. Clear browser cache
4. Check system resources

#### Map Tiles Not Loading

**Solution**:
- Check browser console for 403/404 errors
- Verify internet connection
- Try different browser
- Check if corporate firewall blocks OpenStreetMap

---

### Testing Issues

#### Tests Fail to Run

**Solution**:
```bash
cd backend
pip install pytest pytest-asyncio
pytest tests/ -v
```

#### Import Errors in Tests

**Solution**: Add backend to Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
```

---

### Database Issues

#### Database Locked Error

**Solution**:
1. Close all connections to database
2. Restart backend
3. If persistent, delete database and restart

#### Database Schema Mismatch

**Solution**:
```bash
cd backend/database
del fieldshift.db
# Restart backend to recreate schema
```

---

### Deployment Issues

#### Environment Variables Not Loading

**Solution**:
1. Create `.env` file from `.env.example`
2. Verify variable names match exactly
3. Restart server after changing .env

#### CORS Errors in Production

**Solution**: Update CORS origins in backend/main.py:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    ...
)
```

---

## Debug Mode

### Enable Backend Debug Logging

Edit `backend/main.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Enable Frontend Debug Mode

Check browser console (F12) for detailed errors.

### Test API Directly

Use FastAPI docs interface:
1. Open http://localhost:8000/docs
2. Try individual endpoints
3. Check request/response

---

## Performance Issues

### Backend Slow

**Possible causes**:
- NASA POWER API slow (normal 2-5 seconds)
- Large date ranges
- No caching

**Solutions**:
- Use smaller date ranges
- Implement request caching
- Use asynchronous requests

### Frontend Slow

**Possible causes**:
- Large bundle size
- Too many re-renders
- Memory leaks

**Solutions**:
- Use React.memo for expensive components
- Optimize images
- Use lazy loading

---

## Getting Help

### Check Documentation

1. **README.md** - Overview and quick start
2. **DEMO_GUIDE.md** - Complete walkthrough
3. **MODEL_LIMITATIONS.md** - Scientific details
4. **PROJECT_STATUS.md** - Implementation status

### Check Logs

**Backend logs**: Look at terminal running uvicorn  
**Frontend logs**: Browser console (F12)

### Common Error Messages

| Error | Meaning | Solution |
|-------|---------|----------|
| ECONNREFUSED | Can't connect to backend | Start backend server |
| Module not found | Missing dependency | npm install or pip install |
| CORS error | Cross-origin blocked | Check CORS config |
| 404 Not Found | Wrong API endpoint | Check API URL |
| 500 Internal Server | Backend crash | Check backend logs |

---

## System Requirements

### Minimum

- **CPU**: Dual-core 2GHz
- **RAM**: 4GB
- **Storage**: 500MB free
- **Internet**: Broadband (for NASA APIs)
- **Browser**: Chrome/Firefox/Edge (latest)
- **Python**: 3.11+
- **Node.js**: 18+

### Recommended

- **CPU**: Quad-core 3GHz+
- **RAM**: 8GB+
- **Storage**: 2GB free
- **Internet**: Fast broadband
- **Browser**: Chrome (latest)
- **Python**: 3.11+
- **Node.js**: 20+

---

## Clean Install

If all else fails, start fresh:

### Backend
```bash
cd backend
del /q database\fieldshift.db
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
rmdir /s /q node_modules
rmdir /s /q .next
del package-lock.json
npm install
npm run dev
```

---

## Still Having Issues?

1. Check PROJECT_STATUS.md for known issues
2. Verify all prerequisites installed
3. Try on different machine/browser
4. Check GitHub issues (if public)
5. Review error messages carefully
6. Use browser incognito mode

---

**Most Common Fix**: Restart both backend and frontend servers! 🔄

---

_Last Updated: November 14, 2026_
