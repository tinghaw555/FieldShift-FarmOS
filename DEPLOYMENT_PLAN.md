# FieldShift FarmOS - Public Deployment Plan

**Date:** November 15, 2026  
**Target:** NASA Space Apps Challenge 2026 Submission  
**Status:** PLANNING PHASE

---

## CRITICAL DECISIONS REQUIRED BEFORE PROCEEDING

### 1. **Git Repository Status**
- ❌ **No git repository initialized**
- **Action Required:** Initialize git before any commits
- **Decision:** Start fresh or import existing history?

### 2. **Next.js Deployment Strategy**

**Analysis of Current Setup:**
- Next.js 14.0.4 with App Router
- Dynamic features detected:
  - Server-side API routes (requires Node.js runtime)
  - Dynamic imports and routing
  - No static export configuration

**Options:**

**Option A: Vercel (RECOMMENDED)**
- ✅ Native Next.js 14 support
- ✅ Automatic deployment from GitHub
- ✅ Free tier for personal projects
- ✅ All dynamic features supported
- ✅ HTTPS by default
- ✅ Global CDN
- ❌ Custom domain: vercel.app (not github.io)

**Option B: GitHub Pages**
- ❌ Requires static export (`output: 'export'`)
- ❌ Would break dynamic features:
  - Dynamic API routes in app directory
  - Server components
  - Real-time GPS features
- ❌ Requires significant refactoring
- ❌ May lose functionality
- ⚠️ NOT RECOMMENDED for this application

**RECOMMENDATION:** Use Vercel for frontend hosting

### 3. **Backend Hosting Strategy**

**Current Backend:**
- FastAPI (Python 3.11+)
- SQLite database (local file)
- Requires persistent storage

**Options:**

**Option A: Render.com (RECOMMENDED)**
- ✅ Free tier for personal projects
- ✅ Automatic deployment from GitHub
- ✅ Built-in database backup options
- ✅ PostgreSQL included (free tier)
- ✅ HTTPS by default
- ⚠️ Requires SQLite → PostgreSQL migration
- ⚠️ Cold starts on free tier (first request slow)

**Option B: Railway.app**
- ✅ $5/month credit (free for small projects)
- ✅ PostgreSQL included
- ✅ Good for hobby projects
- ⚠️ May require payment after trial

**Option C: PythonAnywhere**
- ✅ Free tier available
- ✅ SQLite persistence
- ❌ Limited to specific Python versions
- ❌ More complex setup

**RECOMMENDATION:** Use Render.com with PostgreSQL

### 4. **Database Migration Required**

**Current:** SQLite (file-based, not suitable for cloud hosting)  
**Target:** PostgreSQL (cloud-native, persistent)

**Migration Tasks:**
- Update backend dependencies (add `psycopg2`, `sqlalchemy`)
- Convert async SQLite queries to async PostgreSQL
- Update connection strings
- Test all CRUD operations
- Verify data integrity

**Important:** Existing local SQLite data will need manual export/import

---

##Phase 1: PROJECT INSPECTION ✅ COMPLETE

### Current State Analysis

**Structure:**
```
C:\Users\acer\Nasa challenge\
├── frontend/          # Next.js 14 application
├── backend/           # FastAPI application
├── hardware/          # ESP32/NodeMCU firmware
├── Documentation/     # 70+ markdown files
└── Test scripts/      # Python test files
```

**Key Files:**
- `frontend/.env` - **CONTAINS LOCALHOST URLs** (needs production config)
- `backend/database/fieldshift.db` - **LOCAL DATABASE** (needs cloud migration)
- `hardware/*/config.h` - **CONTAINS CREDENTIALS** (needs sanitization)

**Concerns:**
1. No git repository (must init before commits)
2. Many development reports (should move to `/docs` or exclude)
3. SQLite database with user data (cannot deploy to cloud as-is)
4. Hardcoded localhost URLs in frontend
5. ESP32 credentials in firmware files

---

## PHASE 2: SMART FARM MONITORING BEHAVIOR

### Current Behavior Analysis

**From recent fix:**
- Farm 1: 480 records (120 readings × 4 sensors)
- Farm 11: 576 records (144 readings × 4 sensors)
- Other farms: Fall back to shared demonstration data

**Public Deployment Behavior:**

**Requirement:** Must NOT show Farm 1's data as if it belongs to other farms

**Options:**

**A. Remove Shared Fallback (RECOMMENDED)**
```typescript
// Show empty state for farms without data
if (no farm-specific data) {
  show "No Sensor Data Available"
  show "Preview Example" button
}
```

**B. Keep Shared Fallback with Clear Labels**
- Keep current purple "Example Readings" labels
- Ensure note is always visible
- Risk: Users might misunderstand

**RECOMMENDATION:** Option A - Remove automatic fallback, add explicit preview button

---

## PHASE 3: CREDENTIAL AUDIT

### Files Requiring Sanitization

1. **hardware/FieldShift_NodeMCU_V3/config.h**
   - WiFi SSID
   - WiFi Password
   - Backend Server IP
   - Device ID
   - API Key

2. **hardware/FieldShift_ESP32_DevKit/config.h**
   - Same credentials as above

3. **frontend/.env**
   - API base URL (localhost → production)

4. **backend/.env** (if exists)
   - Database connection string
   - Any API keys

5. **Git History**
   - No history yet (clean start)

### Credentials That Need Rotation

⚠️ **SECURITY ALERT:** If any of these were committed to a public repo before, they must be rotated:
- ESP32 API keys
- Device registration tokens
- Any backend authentication secrets

---

## PHASE 4: HOSTING COST SUMMARY

### Projected Costs

**Free Tier (Recommended for Judges):**
- Vercel (Frontend): **$0/month**
- Render.com (Backend + PostgreSQL): **$0/month**
- **Total: $0/month**

**Limitations on Free Tier:**
- Backend cold starts (first request may take 30-60 seconds)
- Limited concurrent connections
- Limited storage (10GB on Render)
- Bandwidth limits (100GB/month on Vercel)

**Paid Options (If Needed):**
- Vercel Pro: $20/month (custom domains, more bandwidth)
- Render Starter: $7/month (faster cold starts, more resources)

**For NASA Space Apps Submission:** Free tier is sufficient

---

## PHASE 5: NEXT STEPS

### Before I Proceed, I Need Your Approval On:

1. **Git Initialization**
   - Initialize new git repository
   - Create initial commit
   - NO previous git history to preserve

2. **Deployment Platform**
   - Frontend: Vercel (vercel.app domain)
   - Backend: Render.com (render.com domain)
   - Database: PostgreSQL on Render

3. **Smart Farm Monitoring**
   - Remove automatic fallback to shared demo data
   - Add explicit "Preview Example Readings" button
   - Show empty state for farms without data

4. **Database Migration**
   - SQLite → PostgreSQL migration required
   - Export existing local data for manual re-import if needed
   - Test all database operations

5. **Credential Handling**
   - Sanitize all firmware files
   - Create template config files
   - Add .env.example files
   - Document credential setup

6. **Documentation Cleanup**
   - Move implementation reports to `/docs/development/`
   - Keep essential docs in root
   - Create clean README.md for judges

---

## ESTIMATED TIMELINE

**If approved to proceed:**

- **Phase 1-4:** Preparation (1-2 hours)
  - Git initialization
  - Credential sanitization
  - Documentation cleanup

- **Phase 5-7:** Database Migration (2-3 hours)
  - PostgreSQL setup
  - Schema migration
  - Testing

- **Phase 8-9:** Deployment (2-3 hours)
  - Render backend deployment
  - Vercel frontend deployment
  - Environment configuration

- **Phase 10-11:** Testing & Documentation (1-2 hours)
  - Integration testing
  - README creation
  - Deployment guide

**Total:** 6-10 hours of work

---

## BLOCKERS AND RISKS

### Cannot Proceed Without:

1. **Your approval** of deployment strategy
2. **Database migration** (SQLite → PostgreSQL)
3. **Manual testing** after each major step
4. **Your GitHub credentials** (you'll need to authenticate)
5. **Your Vercel/Render accounts** (you'll need to create/authorize)

### Risks:

1. **Data Loss:** Local SQLite data may not transfer perfectly
2. **API Compatibility:** Backend changes may require frontend updates
3. **ESP32 Connectivity:** Firmware may need updates for HTTPS backend
4. **External APIs:** NASA POWER and Open-Meteo must work from cloud
5. **Performance:** Free tier may be slow for judges

---

## RECOMMENDED APPROACH

**Step 1: Quick Prototype Deployment**
- Deploy backend with empty database
- Deploy frontend with production API URL
- Verify basic functionality
- Test GPS, NASA POWER, planting analysis

**Step 2: Full Data Migration**
- Migrate database schema
- Import critical demonstration data
- Test all CRUD operations

**Step 3: Final Polish**
- Update README
- Create demo farm
- Test complete user journey

---

## YOUR DECISION REQUIRED

**Please confirm:**

1. ✅ Proceed with Vercel (frontend) + Render (backend)?
2. ✅ Accept PostgreSQL migration requirement?
3. ✅ Accept free tier limitations (cold starts)?
4. ✅ Remove automatic shared demo fallback?
5. ✅ Start with clean git history?

**Once confirmed, I'll proceed with the detailed implementation.**

---

**Next Document:** `DEPLOYMENT_EXECUTION.md` (after approval)

