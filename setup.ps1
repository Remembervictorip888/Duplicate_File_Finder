# Duplicate Image Finder - Automated Setup Script for Windows

Write-Host "🔍 Checking system prerequisites..." -ForegroundColor Yellow

# Check Node.js
try {
    $nodeVersion = node --version
    Write-Host "✓ Node.js version: $nodeVersion" -ForegroundColor Green
    $versionNum = [float]($nodeVersion -replace 'v','' -replace '\..*','')
    if ($versionNum -lt 16) {
        Write-Host "✗ Node.js version must be 16.0 or higher" -ForegroundColor Red
        exit 1
    }
} 
catch {
    Write-Host "✗ Node.js is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Check npm
try {
    $npmVersion = npm --version
    Write-Host "✓ npm version: $npmVersion" -ForegroundColor Green
}
catch {
    Write-Host "✗ npm is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

Write-Host "`n✓ All prerequisites are met" -ForegroundColor Green

# Check if node_modules exists
if (Test-Path "node_modules") {
    Write-Host "✓ Dependencies already installed" -ForegroundColor Green
} else {
    Write-Host "📦 Installing dependencies..." -ForegroundColor Yellow
    npm install
    # cSpell:ignore LASTEXITCODE
    if ($LASTEXITCODE -ne 0) {
        Write-Host "✗ Failed to install dependencies" -ForegroundColor Red
        exit 1
    }
    Write-Host "✓ Dependencies installed successfully" -ForegroundColor Green
}

Write-Host "`n🚀 Starting the application..." -ForegroundColor Cyan

# Start the development server in a new process
Start-Process powershell -ArgumentList "-Command", "npm run dev"

Write-Host "`nApplication is starting. Check your console for the URL." -ForegroundColor Green
Write-Host "It will typically be available at http://localhost:5173 (or another available port)" -ForegroundColor Green