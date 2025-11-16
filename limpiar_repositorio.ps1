# Script para limpiar archivos sensibles del repositorio Git
# Ejecuta este script con: .\limpiar_repositorio.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Limpieza de Archivos Sensibles en Git" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en un repositorio Git
if (-not (Test-Path .git)) {
    Write-Host "ERROR: No estás en un repositorio Git" -ForegroundColor Red
    exit 1
}

Write-Host "Paso 1: Verificando archivos sensibles en el repositorio..." -ForegroundColor Yellow

# Verificar si .env está en el historial
$envInHistory = git log --all --full-history --oneline --name-only | Select-String -Pattern "^\.env$"
if ($envInHistory) {
    Write-Host "  ⚠️  Archivo .env encontrado en el historial" -ForegroundColor Red
} else {
    Write-Host "  ✅ Archivo .env no encontrado en el historial" -ForegroundColor Green
}

# Verificar si venv/ está siendo rastreado
$venvTracked = git ls-files | Select-String -Pattern "^venv/"
if ($venvTracked) {
    Write-Host "  ⚠️  Carpeta venv/ está siendo rastreada" -ForegroundColor Red
    $venvCount = ($venvTracked | Measure-Object).Count
    Write-Host "     ($venvCount archivos encontrados)" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ Carpeta venv/ no está siendo rastreada" -ForegroundColor Green
}

# Verificar si models/*.pkl está siendo rastreado
$modelsTracked = git ls-files | Select-String -Pattern "^models/.*\.pkl$"
if ($modelsTracked) {
    Write-Host "  ⚠️  Modelos .pkl encontrados en el repositorio" -ForegroundColor Red
} else {
    Write-Host "  ✅ Modelos .pkl no están siendo rastreados" -ForegroundColor Green
}

Write-Host ""
Write-Host "Paso 2: Instalando git-filter-repo (si es necesario)..." -ForegroundColor Yellow

# Verificar si git-filter-repo está instalado
$filterRepoInstalled = Get-Command git-filter-repo -ErrorAction SilentlyContinue
if (-not $filterRepoInstalled) {
    Write-Host "  Instalando git-filter-repo..." -ForegroundColor Yellow
    pip install git-filter-repo
    if ($LASTEXITCODE -ne 0) {
        Write-Host "  ⚠️  Error al instalar git-filter-repo" -ForegroundColor Red
        Write-Host "  Puedes instalarlo manualmente con: pip install git-filter-repo" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ git-filter-repo instalado correctamente" -ForegroundColor Green
    }
} else {
    Write-Host "  ✅ git-filter-repo ya está instalado" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "INSTRUCCIONES MANUALES:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para eliminar archivos del historial, ejecuta estos comandos:" -ForegroundColor Yellow
Write-Host ""

if ($envInHistory) {
    Write-Host "1. Eliminar .env del historial:" -ForegroundColor Cyan
    Write-Host "   git filter-repo --path .env --invert-paths" -ForegroundColor White
    Write-Host ""
}

if ($venvTracked) {
    Write-Host "2. Eliminar venv/ del historial:" -ForegroundColor Cyan
    Write-Host "   git filter-repo --path venv/ --invert-paths" -ForegroundColor White
    Write-Host ""
}

if ($modelsTracked) {
    Write-Host "3. Eliminar models/*.pkl del historial:" -ForegroundColor Cyan
    Write-Host "   git filter-repo --path-glob 'models/*.pkl' --invert-paths" -ForegroundColor White
    Write-Host ""
}

Write-Host "4. Después de eliminar, fuerza el push (¡CUIDADO!):" -ForegroundColor Cyan
Write-Host "   git push origin --force --all" -ForegroundColor White
Write-Host "   git push origin --force --tags" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  ADVERTENCIA: Esto reescribirá el historial de Git" -ForegroundColor Red
Write-Host "   Asegúrate de hacer un backup antes de continuar" -ForegroundColor Red
Write-Host ""

