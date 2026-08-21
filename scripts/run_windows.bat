@echo off
setlocal
cd /d "%~dp0\.."
if not exist .venv\Scripts\python.exe py -3.13 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install -r requirements.txt
if not exist .env copy .env.example .env >nul
streamlit run app.py
endlocal
