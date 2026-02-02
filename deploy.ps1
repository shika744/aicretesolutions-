# Copyright 2025 Shiksha Seechurn / AIcrete
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# AIcrete Deployment Script for Windows
Write-Host "🚀 Deploying AIcrete UHPC Analysis Platform..." -ForegroundColor Green

# Check if Git is initialized
if (-not (Test-Path ".git")) {
    Write-Host "📦 Initializing Git repository..." -ForegroundColor Yellow
    git init
    git add .
    git commit -m "Initial AIcrete deployment - Professional UHPC Analysis Platform"
}

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "🐍 Python version: $pythonVersion" -ForegroundColor Cyan

# Install dependencies
Write-Host "📋 Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Test the application locally
Write-Host "🧪 Testing application..." -ForegroundColor Yellow
$streamlitJob = Start-Job -ScriptBlock {
    streamlit run aicrete_app.py --server.headless=true --server.port=8502
}
Start-Sleep -Seconds 8

# Check if app is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8502" -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Application test successful!" -ForegroundColor Green
    Stop-Job $streamlitJob
    Remove-Job $streamlitJob
} catch {
    Write-Host "❌ Application test failed!" -ForegroundColor Red
    Stop-Job $streamlitJob
    Remove-Job $streamlitJob
    exit 1
}

Write-Host ""
Write-Host "🎉 AIcrete is ready for deployment!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Yellow
Write-Host "1. Push to GitHub: git push origin main"
Write-Host "2. Deploy on Streamlit Cloud: https://share.streamlit.io"
Write-Host "3. Or run locally: streamlit run aicrete_app.py"
Write-Host ""
Write-Host "🔗 Features available:" -ForegroundColor Cyan
Write-Host "   ✅ Property Prediction (5 properties)"
Write-Host "   ✅ Target-Based Design"
Write-Host "   ✅ Interactive Charts & Heatmaps"
Write-Host "   ✅ Project Management"
Write-Host "   ✅ Professional Reports"
Write-Host "   ✅ Multi-Currency Support"
