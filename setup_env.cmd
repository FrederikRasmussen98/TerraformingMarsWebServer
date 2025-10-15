@echo off
echo Setting up Python virtual environment and installing packages...

REM Step 1: Create virtual environment
python -m venv venv

REM Step 2: Activate virtual environment
call venv\Scripts\activate

REM Step 3: Upgrade pip
python -m pip install --upgrade pip

REM Step 4: Install requirements
pip install -r requirements.txt

echo.
echo ✅ Environment setup complete!
echo To activate it later, run: venv\Scripts\activate
pause
