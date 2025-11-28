$ErrorActionPreference = 'Stop'

Write-Host "[+] Verificando/criando venv..."
if (-not (Test-Path -Path .venv)) {
  python -m venv .venv
}

Write-Host "[+] Instalando dependências..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt

Write-Host "[+] Iniciando servidor Flask (t1.py) em background..."
Start-Process -NoNewWindow -FilePath (Resolve-Path .\.venv\Scripts\python.exe) -ArgumentList '.\t1.py'

Write-Host "[+] Servidor iniciado. Acesse http://localhost:8000"

if (Test-Path -Path .\ngrok.exe) {
  Write-Host "[+] ngrok.exe encontrado no diretório. Deseja iniciar um túnel ngrok agora? (s/n)"
  $r = Read-Host
  if ($r -eq 's' -or $r -eq 'S') {
    Write-Host "Iniciando ngrok http 8000..."
    Start-Process -NoNewWindow -FilePath (Resolve-Path .\ngrok.exe) -ArgumentList 'http 8000'
    Write-Host "ngrok iniciado (ver saída do processo ngrok para o URL público)."
  }
} else {
  Write-Host "ngrok.exe não encontrado neste diretório. Para usar ngrok, baixe de https://ngrok.com e coloque o executável aqui ou no PATH."
}

Write-Host "Se precisar abrir a porta no firewall para LAN, execute (como Administrador):"
Write-Host "  New-NetFirewallRule -DisplayName 'Flask 8000' -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow"
