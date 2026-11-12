@echo off
setlocal
cd /d "%~dp0"
if not exist capture.js goto missing
if not exist tools mkdir tools
if errorlevel 1 goto failed
echo Downloading official portable tools; no installation or certificate changes.
curl.exe --fail --location --proto "=https" --proto-redir "=https" --output "tools\7zr.exe" "https://github.com/ip7z/7zip/releases/download/26.06/7zr.exe"
if errorlevel 1 goto failed
powershell.exe -NoProfile -NonInteractive -Command "if ((Get-FileHash -LiteralPath 'tools\7zr.exe' -Algorithm SHA256).Hash -ne 'e80db2dad715a6c5adabe292d31ed54e11f4e9b99ca349827b50573b175891bc') { exit 1 }"
if errorlevel 1 goto failed
curl.exe --fail --location --proto "=https" --proto-redir "=https" --output "tools\7z-extra.7z" "https://github.com/ip7z/7zip/releases/download/26.06/7z2606-extra.7z"
if errorlevel 1 goto failed
powershell.exe -NoProfile -NonInteractive -Command "if ((Get-FileHash -LiteralPath 'tools\7z-extra.7z' -Algorithm SHA256).Hash -ne '396c180f12d2247c24b0b1fcd482c6fc2a2700f61211ffede1061dd971f5e104') { exit 1 }"
if errorlevel 1 goto failed
curl.exe --fail --location --proto "=https" --proto-redir "=https" --output "tools\frida.exe.xz" "https://github.com/frida/frida/releases/download/17.26.2/frida-inject-17.26.2-windows-x86.exe.xz"
if errorlevel 1 goto failed
powershell.exe -NoProfile -NonInteractive -Command "if ((Get-FileHash -LiteralPath 'tools\frida.exe.xz' -Algorithm SHA256).Hash -ne '5088690d9b861187d7d7086e8ee9a4133b5abab76ae66e05cef4fd204f157f41') { exit 1 }"
if errorlevel 1 goto failed
tools\7zr.exe x "tools\7z-extra.7z" -otools\7zip -y >nul
if errorlevel 1 goto failed
tools\7zip\7za.exe e "tools\frida.exe.xz" -otools -y >nul
if errorlevel 1 goto failed
powershell.exe -NoProfile -NonInteractive -Command "if ((Get-FileHash -LiteralPath 'tools\frida.exe' -Algorithm SHA256).Hash -ne '35b78cedc42c536350a364b2d44d17067d8b179d7d1fb922c9f889a45fd23514') { exit 1 }"
if errorlevel 1 goto failed
echo Open HiSuite 14 normally, connect the phone and wait for its home screen.
echo Only view available versions. Do not start Update, Restore or Rollback.
echo The observer removes its hooks after five minutes. Close HiSuite to finish.
pause
tools\frida.exe --name HiSuite.exe --script capture.js
exit /b %errorlevel%
:missing
echo Missing capture.js beside run.cmd. Download both files into the same folder.
exit /b 1
:failed
echo Setup stopped: a download, checksum or extraction failed. Do not bypass it.
exit /b 1
