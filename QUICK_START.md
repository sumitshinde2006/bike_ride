# Quick Start Guide - RideWise Application

## ⚠️ Important: Which URL to Use

**Use one of these URLs (NOT the IP address 10.103.105.68):**

- ✅ **http://localhost:3000** (recommended)
- ✅ **http://127.0.0.1:3000** (alternative)
- ❌ **http://10.103.105.68:3000** (may not work unless specifically configured)

## Step 1: Start Backend Server

Open **Terminal/Command Prompt** and run:

```powershell
cd backend
python app.py
```

**Wait for this message:**
```
Server: http://0.0.0.0:5000
```

**Keep this terminal open!** ⚠️ Don't close it.

## Step 2: Start Frontend Server

Open a **NEW Terminal/Command Prompt** (keep the backend running) and run:

```powershell
npm run dev
```

**Wait for this message:**
```
➜  Local:   http://localhost:3000/
```

## Step 3: Open in Browser

Open your browser and go to:
```
http://localhost:3000
```

## If You Need Network Access (10.103.105.68)

If you need to access from other devices on your network:

1. Make sure Windows Firewall allows connections on ports 3000 and 5000
2. Use your machine's IP address: `http://10.103.105.68:3000`
3. The servers are already configured to accept network connections (`host: 0.0.0.0`)

## Troubleshooting

### "Connection Refused" Error

1. **Check if servers are running:**
   - Backend should show: "Server: http://0.0.0.0:5000"
   - Frontend should show: "Local: http://localhost:3000/"

2. **Check ports are in use:**
   ```powershell
   netstat -ano | findstr ":3000"
   netstat -ano | findstr ":5000"
   ```

3. **Use localhost instead of IP:**
   - Try: `http://localhost:3000` or `http://127.0.0.1:3000`

4. **Check firewall:**
   - Windows Firewall may be blocking connections
   - Temporarily disable to test

### Frontend Can't Connect to Backend

- Make sure backend is running on port 5000
- Check browser console for errors (F12)
- Verify backend responds: `http://localhost:5000/health`
