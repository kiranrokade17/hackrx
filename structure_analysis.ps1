# Production Structure Summary for HackRX API

Write-Host "🧹 HackRX API - Production Structure Analysis" -ForegroundColor Green

Write-Host "`n📊 Current Structure Analysis:" -ForegroundColor Cyan
$AllFiles = Get-ChildItem -File
$AllDirs = Get-ChildItem -Directory

Write-Host "  Total Files: $($AllFiles.Count)" -ForegroundColor White
Write-Host "  Total Directories: $($AllDirs.Count)" -ForegroundColor White

Write-Host "`n✅ Essential Files (Keep):" -ForegroundColor Green
$EssentialFiles = @(
    "advanced_document_api_v2.py",
    "requirements.txt", 
    ".env",
    "README.md"
)

foreach ($file in $EssentialFiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file" -ForegroundColor Green
    }
}

Write-Host "`n🗑️ Unwanted Files (Remove):" -ForegroundColor Red

# Test files
$TestFiles = Get-ChildItem -File | Where-Object { $_.Name -match "^test_|_test\.py$|debug_|comprehensive_|final_|simple_|fresh_" }
Write-Host "  Test/Debug Files ($($TestFiles.Count)):" -ForegroundColor Yellow
foreach ($file in $TestFiles) {
    Write-Host "    ❌ $($file.Name)" -ForegroundColor Red
}

# PowerShell scripts
$PSFiles = Get-ChildItem -File | Where-Object { $_.Extension -eq ".ps1" }
Write-Host "  PowerShell Scripts ($($PSFiles.Count)):" -ForegroundColor Yellow
foreach ($file in $PSFiles) {
    Write-Host "    ❌ $($file.Name)" -ForegroundColor Red
}

# Documentation files
$DocFiles = Get-ChildItem -File | Where-Object { $_.Name -match "(GUIDE|EXPLANATION|SUMMARY|TEST|POSTMAN).*\.md$" }
Write-Host "  Extra Documentation ($($DocFiles.Count)):" -ForegroundColor Yellow
foreach ($file in $DocFiles) {
    Write-Host "    ❌ $($file.Name)" -ForegroundColor Red
}

# API versions
$APIFiles = Get-ChildItem -File | Where-Object { $_.Name -match "^(advanced_document_api\.py|advanced_document_api_v3\.py|simple_api\.py|main\.py|startup\.py)$" }
Write-Host "  Extra API Versions ($($APIFiles.Count)):" -ForegroundColor Yellow
foreach ($file in $APIFiles) {
    Write-Host "    ❌ $($file.Name)" -ForegroundColor Red
}

Write-Host "`n🎯 Recommended Production Structure:" -ForegroundColor Magenta
Write-Host @"
📁 hackrx-api/
├── 📄 main.py              # Rename from advanced_document_api_v2.py
├── 📄 requirements.txt     # Keep current (but clean it)
├── 📄 .env                # Keep your current config
├── 📄 .env.example        # Create template
├── 📄 .gitignore          # Add production rules
├── 📄 README.md           # Keep but simplify
├── 📄 Dockerfile          # Add for deployment
└── 📄 render.yaml         # Add for Render deployment
"@ -ForegroundColor White

$UnwantedCount = $TestFiles.Count + $PSFiles.Count + $DocFiles.Count + $APIFiles.Count
$CurrentTotal = $AllFiles.Count
$AfterCleanup = 8

Write-Host "`n📊 Cleanup Impact:" -ForegroundColor Cyan
Write-Host "  Files to remove: $UnwantedCount" -ForegroundColor Red
Write-Host "  Files after cleanup: $AfterCleanup" -ForegroundColor Green
Write-Host "  Space reduction: $([math]::Round((($CurrentTotal - $AfterCleanup) / $CurrentTotal) * 100))%" -ForegroundColor Green

Write-Host "`n🚀 Your API will have:" -ForegroundColor Green
Write-Host "  ✅ Single main.py file" -ForegroundColor White
Write-Host "  ✅ Clean dependencies" -ForegroundColor White  
Write-Host "  ✅ Production deployment configs" -ForegroundColor White
Write-Host "  ✅ Professional structure" -ForegroundColor White
Write-Host "  ✅ Easy maintenance" -ForegroundColor White

Write-Host "`n✨ Production Ready!" -ForegroundColor Green
