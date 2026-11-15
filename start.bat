@echo off
echo ==================================================
echo   Football Prediction Model - Startup Sequence
echo ==================================================
echo.

echo Activating Python Virtual Environment...
call venv\Scripts\activate
if %ERRORLEVEL% neq 0 (
    echo Error: Could not activate virtual environment!
    pause
    exit /b %ERRORLEVEL%
)
echo.

echo [1/4] Updating Match and Injury Data...
python data_ingestion.py
if %ERRORLEVEL% neq 0 (
    echo Error during data ingestion!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [2/4] Recalculating Elo and Form Features...
python feature_engineering.py
if %ERRORLEVEL% neq 0 (
    echo Error during feature engineering!
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [3/4] Starting Flask API Backend...
start cmd /k "python api.py"

echo.
echo [4/4] Starting React Frontend...
cd frontend
start cmd /k "npm run dev"

echo.
echo ==================================================
echo   System is fully updated and running!
echo   Close this window when you are done.
echo ==================================================
pause
