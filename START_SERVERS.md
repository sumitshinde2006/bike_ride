# How to Start RideWise Application

## Quick Start

### Option 1: Use the Start Script (Easiest)

**Windows PowerShell:**
```powershell
.\start-all.ps1
```

**Windows Command Prompt:**
```cmd
start-all.bat
```

### Option 2: Start Manually

#### Step 1: Start Backend Server

Open a **new terminal/command prompt** and run:

**Windows PowerShell:**
```powershell
cd backend
.\start.ps1
```

**Windows Command Prompt:**
```cmd
cd backend
start.bat
```

You should see:
```
Starting Flask server...
============================================================
RideWise Backend Server Starting
============================================================
Server: http://0.0.0.0:5000
```

**Leave this terminal window open** - the backend must keep running.

#### Step 2: Start Frontend Server

Open a **second terminal/command prompt** and run:

```cmd
npm run dev
```

or if using PowerShell:
```powershell
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
```

## Access the Application

Once both servers are running:

1. **Frontend (Main App)**: Open http://localhost:3000 in your browser
2. **Backend API**: http://localhost:5000/health (for testing)

## Test the Chatbot

1. Navigate to the Chatbot page in the application
2. Type a question like: "What factors affect bike demand?"
3. The chatbot will use Google Gemini AI to respond

## Troubleshooting

### "localhost refused to connect" Error

If you see this error:

1. **Check if servers are running:**
   - Backend should show "Server: http://0.0.0.0:5000"
   - Frontend should show "Local: http://localhost:3000"

2. **Check for port conflicts:**
   - Make sure ports 5000 and 3000 are not already in use
   - Close any other applications using these ports

3. **Try using 127.0.0.1 instead of localhost:**
   - Open: http://127.0.0.1:3000

4. **Check firewall settings:**
   - Temporarily disable firewall to test
   - Add exceptions for Python and Node.js

5. **Verify dependencies are installed:**
   ```cmd
   cd backend
   pip install -r requirements.txt
   ```

### Backend Won't Start

- Make sure Python 3.8+ is installed: `python --version`
- Install dependencies: `pip install -r backend/requirements.txt`
- Check for error messages in the terminal

### Frontend Won't Start

- Make sure Node.js is installed: `node --version`
- Install dependencies: `npm install`
- Check for error messages in the terminal
