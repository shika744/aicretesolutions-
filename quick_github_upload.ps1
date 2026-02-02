# Quick GitHub Upload Script
# Copyright 2025 Shiksha Seechurn / AIcrete

Write-Host "🚀 AIcrete GitHub Upload Script" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

# Step 1: Check if we're in the right directory
if (-not (Test-Path "aicrete_app.py")) {
    Write-Host "❌ Error: aicrete_app.py not found!" -ForegroundColor Red
    Write-Host "Please run this script from the AIcrete_GitHub_Deploy folder" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Found aicrete_app.py - we're in the right place!" -ForegroundColor Green

# Step 2: Check if Git is installed
try {
    git --version | Out-Null
    Write-Host "✅ Git is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Git not found! Please install Git first:" -ForegroundColor Red
    Write-Host "   Download from: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Step 3: Get GitHub repository URL from user
Write-Host ""
Write-Host "📋 GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "1. Go to https://github.com" -ForegroundColor White
Write-Host "2. Click 'New Repository'" -ForegroundColor White
Write-Host "3. Name: AIcrete-UHPC-Analysis" -ForegroundColor White
Write-Host "4. Make it Public" -ForegroundColor White
Write-Host "5. DON'T initialize with README" -ForegroundColor White
Write-Host "6. Copy the repository URL" -ForegroundColor White
Write-Host ""

$repoUrl = Read-Host "Enter your GitHub repository URL (e.g., https://github.com/username/AIcrete-UHPC-Analysis.git)"

if ([string]::IsNullOrEmpty($repoUrl)) {
    Write-Host "❌ Repository URL is required!" -ForegroundColor Red
    exit 1
}

# Step 4: Initialize Git and upload
Write-Host ""
Write-Host "🔄 Initializing Git repository..." -ForegroundColor Cyan

try {
    # Initialize Git
    if (-not (Test-Path ".git")) {
        git init
        Write-Host "✅ Git repository initialized" -ForegroundColor Green
    } else {
        Write-Host "✅ Git repository already exists" -ForegroundColor Green
    }

    # Add files
    git add .
    Write-Host "✅ Files staged for commit" -ForegroundColor Green

    # Commit
    git commit -m "AIcrete UHPC Analysis Platform - Professional ML Application with Overfitting Analysis"
    Write-Host "✅ Files committed" -ForegroundColor Green

    # Add remote origin
    try {
        git remote add origin $repoUrl
    } catch {
        Write-Host "ℹ️ Remote origin already exists, updating..." -ForegroundColor Yellow
        git remote set-url origin $repoUrl
    }

    # Push to GitHub
    git branch -M main
    git push -u origin main

    Write-Host ""
    Write-Host "🎉 SUCCESS! Your code is now on GitHub!" -ForegroundColor Green
    Write-Host "Repository URL: $repoUrl" -ForegroundColor Cyan

} catch {
    Write-Host ""
    Write-Host "❌ Error during Git operations:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Common solutions:" -ForegroundColor Yellow
    Write-Host "   • Make sure you have write access to the repository" -ForegroundColor White
    Write-Host "   • Check if you need to authenticate with GitHub" -ForegroundColor White
    Write-Host "   • Verify the repository URL is correct" -ForegroundColor White
    exit 1
}

# Step 5: Next steps
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Cyan
Write-Host "1. Go to https://share.streamlit.io" -ForegroundColor White
Write-Host "2. Sign in with GitHub" -ForegroundColor White
Write-Host "3. Click 'New app'" -ForegroundColor White
Write-Host "4. Select your repository: AIcrete-UHPC-Analysis" -ForegroundColor White
Write-Host "5. Main file: aicrete_app.py" -ForegroundColor White
Write-Host "6. Click 'Deploy!'" -ForegroundColor White
Write-Host ""
Write-Host "🚀 Your app will be live at: https://your-app-name.streamlit.app" -ForegroundColor Green
Write-Host ""
Write-Host "Press any key to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
