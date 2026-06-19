# Expense Compliance Agent - Local Deployment Prep Script

Write-Host "--- Preparing local build for Google Cloud ---" -ForegroundColor Cyan

# 1. Frontend Build
Write-Host "1. Building Frontend..." -ForegroundColor Yellow
cd frontend
npm install
npm run build
cd ..

# 2. Local Docker Test (Optional)
Write-Host "2. Building Local Docker Image (Test)..." -ForegroundColor Yellow
docker build -t expense-agent-local .

Write-Host "--- Build Complete ---" -ForegroundColor Green
Write-Host "To deploy manually, run:"
Write-Host "gcloud run deploy expense-agent-backend --source ."
Write-Host "firebase deploy --only hosting"
