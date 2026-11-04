$ErrorActionPreference = 'Stop'

$containerName = 'e1-1-web'
$url = 'http://localhost:18080/'

Write-Host '== Docker version =='
docker --version

Write-Host "`n== Container state =="
docker ps -a --filter "name=$containerName"

Write-Host "`n== HTTP response: $url =="
(Invoke-WebRequest -UseBasicParsing -Uri $url -TimeoutSec 15).StatusCode

Write-Host "`n== Health response =="
Invoke-RestMethod -Uri 'http://localhost:18080/health' -TimeoutSec 15

Write-Host "`n== Resource snapshot =="
docker stats --no-stream $containerName
