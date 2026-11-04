$ErrorActionPreference = 'Stop'
$careerRoot = Join-Path $PSScriptRoot 'app'
$careerPython = Join-Path $careerRoot 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $careerPython)) {
    throw 'Create the Python environment and install app/requirements.txt first. See README.md.'
}
Push-Location -LiteralPath $careerRoot
try {
    & $careerPython setup_local.py
    if ($LASTEXITCODE -ne 0) { throw 'Configuration setup failed.' }
    & $careerPython -m flask --app app init-db
    if ($LASTEXITCODE -ne 0) { throw 'Database initialization failed.' }
    & $careerPython -m flask --app app run --host 127.0.0.1 --port 5001
} finally {
    Pop-Location
}
