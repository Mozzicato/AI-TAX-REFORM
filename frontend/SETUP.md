# Frontend Setup Guide

## Prerequisites

Before setting up the frontend, you need to install Node.js:

### Install Node.js (Windows)

1. **Download Node.js**:
   - Go to https://nodejs.org/
   - Download the LTS version (recommended: v18.x or v20.x)
   - Run the installer

2. **Verify Installation**:
   ```powershell
   node --version
   npm --version
   ```

## Setup Steps

Once Node.js is installed:

```powershell
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# This will install:
# - next (14.0.4)
# - react (18.2.0)
# - typescript (5.3.3)
# - tailwindcss (3.4.0)
# - lucide-react (0.298.0)
# - react-markdown (9.0.1)
# - and all other dependencies from package.json

# Configure environment
cp .env.example .env.local
# Edit .env.local and set NEXT_PUBLIC_API_URL=http://localhost:7860

# Run development server
npm run dev
```

The frontend will be available at http://localhost:3000

## Production Build

```powershell
npm run build
npm start
```

## Alternative: Skip Frontend Setup (Backend Only)

If you only want to test the backend API, you can skip frontend setup and use:

- **curl** for testing endpoints
- **Postman** for API testing
- **PowerShell's Invoke-WebRequest** (as you've been doing)

The backend API is fully functional on its own at http://localhost:7860

## Troubleshooting

**npm not found after install**:
- Restart PowerShell after installing Node.js
- Or add Node.js to PATH manually: `C:\Program Files\nodejs\`

**Permission errors**:
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Port already in use**:
```powershell
# Check what's using port 3000
netstat -ano | findstr :3000
# Kill the process if needed
```
