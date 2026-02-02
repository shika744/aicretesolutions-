#!/bin/bash
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
# AIcrete Deployment Script
echo "🚀 Deploying AIcrete UHPC Analysis Platform..."

# Check if Git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial AIcrete deployment - Professional UHPC Analysis Platform"
fi

# Check Python version
python_version=$(python --version 2>&1)
echo "🐍 Python version: $python_version"

# Install dependencies
echo "📋 Installing dependencies..."
pip install -r requirements.txt

# Test the application locally
echo "🧪 Testing application..."
timeout 10s streamlit run aicrete_app.py --server.headless=true --server.port=8502 &
sleep 5

# Check if app is running
if curl -s http://localhost:8502 > /dev/null; then
    echo "✅ Application test successful!"
    pkill -f "streamlit run aicrete_app.py"
else
    echo "❌ Application test failed!"
    pkill -f "streamlit run aicrete_app.py"
    exit 1
fi

echo "🎉 AIcrete is ready for deployment!"
echo ""
echo "📋 Next steps:"
echo "1. Push to GitHub: git push origin main"
echo "2. Deploy on Streamlit Cloud: https://share.streamlit.io"
echo "3. Or run locally: streamlit run aicrete_app.py"
echo ""
echo "🔗 Features available:"
echo "   ✅ Property Prediction (5 properties)"
echo "   ✅ Target-Based Design"
echo "   ✅ Interactive Charts & Heatmaps" 
echo "   ✅ Project Management"
echo "   ✅ Professional Reports"
echo "   ✅ Multi-Currency Support"
