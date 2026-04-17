# Script para ejecutar tests de API
# Ejecutar desde: C:\Users\avali\Desktop\Proyectos\whatsapp_sales_bot

Write-Host "=== Ejecutando Tests de API ===" -ForegroundColor Green
Write-Host ""

# Cambiar a directorio de API
Set-Location apps\api

Write-Host "Ejecutando tests unitarios..." -ForegroundColor Yellow
pytest tests/unit/ -v

Write-Host ""
Write-Host "Ejecutando tests de integración..." -ForegroundColor Yellow
pytest tests/integration/ -v

Write-Host ""
Write-Host "=== Tests completados ===" -ForegroundColor Green

# Volver a raíz
Set-Location ..\..
