@echo off
setlocal

echo Checking for Python installation...
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found. Downloading and installing...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
)

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r dependencies.txt

echo Running ArcadeHubDB.Base.py...
python ArcadeHubDB.Base.py

pause
