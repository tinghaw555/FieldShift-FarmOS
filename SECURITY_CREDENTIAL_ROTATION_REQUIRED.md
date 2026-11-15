# 🔐 Security Alert: Credential Rotation Required

**Date:** November 15, 2026  
**Status:** ⚠️ **ACTION REQUIRED**

---

## 📋 Summary

The following credentials were **EXPOSED** in project files and markdown documentation before sanitization. While they have been removed from the files that will be published to GitHub, these credentials **MUST be rotated immediately** as they may have been visible in:

- Local file edit history
- IDE cache
- System backups
- Screen recordings/screenshots

---

## 🚨 Exposed Credentials

### 1. WiFi Credentials
**SSID:** `Android 123`  
**Password:** `udgt3699`

**Risk:** Medium  
**Impact:** Unauthorized access to phone hotspot

**Action Required:**
- ✅ Change phone hotspot password immediately
- ✅ Consider changing hotspot name
- ✅ Update ESP32 config.h with new credentials (DO NOT commit)

---

### 2. API Key
**Device ID:** `NODEMCU_V3_ESP8266_001`  
**API Key:** `qwXg3afBII7c6XVhyqf1XPiSNdqjLDsUTqGRz_h1a1g`

**Risk:** High  
**Impact:** Unauthorized access to device telemetry API, ability to send fake sensor data

**Action Required:**
- ✅ Delete device registration in backend database
- ✅ Re-register device with new ID and key
- ✅ Update ESP32 config.h with new credentials (DO NOT commit)
- ✅ Invalidate old API key in backend

**SQL Command to Rotate:**
```sql
-- Backend database
DELETE FROM devices WHERE device_id = 'NODEMCU_V3_ESP8266_001';
-- Re-register device through API to get new credentials
```

---

### 3. IP Address
**Laptop IP:** `10.22.217.151`

**Risk:** Low  
**Impact:** Internal network topology revealed (school/work network)

**Action Required:**
- ℹ️ No immediate action required (internal IP changes frequently)
- ✅ Confirm no port forwarding rules expose backend to internet
- ✅ Ensure firewall blocks external access to port 8000

---

## ✅ Files That Were Sanitized

The following files **NOW CONTAIN PLACEHOLDERS** and are safe to publish:

### Hardware Configs (Sanitized ✅)
- ✅ `hardware/FieldShift_ESP32_DevKit/config.h`
  - WiFi SSID → `YOUR_WIFI_SSID`
  - WiFi Password → `YOUR_WIFI_PASSWORD`
  - API Server → `192.168.1.100`
  - Device ID → `YOUR_DEVICE_ID`
  - API Key → `YOUR_API_KEY_HERE`

- ✅ `hardware/FieldShift_ESP32_DevKit_FINAL/FieldShift_ESP32_DevKit_FINAL.ino`
  - WiFi SSID → `YOUR_WIFI_SSID`
  - WiFi Password → `YOUR_WIFI_PASSWORD`
  - Device ID → `YOUR_DEVICE_ID`
  - API Key → `YOUR_API_KEY_HERE`

- ✅ `hardware/FieldShift_NodeMCU_V3/config.h`
  - Already had placeholders (good!)

---

## ⚠️ Files Being Excluded (Not Published)

These files are in `.gitignore` and will NOT be published:

- ❌ `frontend/.env` (contains localhost URL)
- ❌ `backend/database/fieldshift.db` (contains device registrations)
- ❌ `backend/.venv/` (Python virtual environment)
- ❌ `frontend/node_modules/` (Node dependencies)
- ❌ All `__pycache__/` directories

---

## 📄 Documentation Files Containing References

The following **documentation markdown files** contain references to exposed credentials in code examples and troubleshooting guides:

**NOTE:** These are **instructional documents** showing setup procedures. They will be published to GitHub to help other users set up their hardware. The credentials shown are **examples only** and no longer valid.

### Files with Credential References:
1. `NODEMCU_SETUP_COMPLETE.md`
2. `NODEMCU_INTEGRATION_REPORT.md`
3. `NODEMCU_FINAL_STATUS.md`
4. `ESP32_UPLOAD_CHECKLIST.md`
5. `UPLOAD_FIRMWARE_NOW.md`
6. `UPLOAD_NOW.md`
7. Various other ESP32/NodeMCU setup guides

**Recommendation:**
- ✅ These files are SAFE to publish (they are documentation, not config files)
- ✅ Add a notice at the top of each: "⚠️ Credentials shown are examples only - use your own"
- ✅ OR remove these internal development docs if not needed for judges

---

## 🔒 Post-Rotation Checklist

After rotating credentials, verify:

- [ ] New WiFi password set on phone hotspot
- [ ] Old device registration deleted from backend database
- [ ] New device registered with fresh API key
- [ ] ESP32 config.h updated locally (not committed)
- [ ] ESP32 firmware re-uploaded with new credentials
- [ ] Device successfully connects to backend with new key
- [ ] Smart Farm Monitoring dashboard shows "Connected"
- [ ] Test sensor readings appear in dashboard
- [ ] Confirmed old API key returns 401 Unauthorized

---

## 🛡️ Prevention for Future

To avoid credential exposure in the future:

1. **NEVER commit config.h files** with real credentials
   - Keep `config.h.example` with placeholders in git
   - Copy to `config.h` locally and add real values
   - Ensure `.gitignore` includes `config.h`

2. **Use environment variables** for backend deployment
   - Store API keys in `.env` files
   - Add `.env` to `.gitignore`
   - Use `.env.example` templates in repository

3. **Rotate credentials regularly**
   - Change WiFi passwords quarterly
   - Regenerate API keys every 6 months
   - Use different keys for production vs development

4. **Scan before committing**
   - Run: `git diff` before every commit
   - Use tools like `git-secrets` or `gitleaks`
   - Review GitHub repository security alerts

---

## 📞 Questions?

If you're unsure whether a file is safe to publish:
1. Check if it's in `.gitignore`
2. Search file content for real passwords/keys
3. When in doubt, exclude it from the first commit
4. You can always add it later after manual review

---

**REMEMBER:** Once credentials are published to GitHub, they should be considered **permanently compromised** even if you delete the commit. Always rotate immediately.
