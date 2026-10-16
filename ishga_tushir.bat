@echo off
rem ishga_tushir.bat - loyihani BIR BOSISH bilan ishga tushiradi (Windows).
rem Nima qiladi: 1) kutubxonalarni ornatadi  2) backend serverni (8000) yoqadi  3) sayt serverini (5500) yoqadi  4) brauzerda saytni ochadi.
rem Toxtatish: ochilgan ikkita qora oynani yoping.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo .venv topilmadi. PyCharm'da loyiha interpreterini tekshiring.
  pause
  exit /b 1
)
echo [1/3] Kutubxonalar ornatilmoqda (birinchi marta bir necha daqiqa oladi)...
".venv\Scripts\python.exe" -m pip install -r backend\requirements.txt
if errorlevel 1 (
  echo Kutubxonalarni ornatishda xato chiqdi. Xatoni nusxalab yuboring.
  pause
  exit /b 1
)
echo [2/3] Backend va sayt serverlari yoqilmoqda...
start "Backend (8000)" /d "%~dp0backend" "%~dp0.venv\Scripts\python.exe" -m uvicorn main:app
start "Sayt (5500)" /d "%~dp0frontend" "%~dp0.venv\Scripts\python.exe" -m http.server 5500
echo [3/3] Brauzer ochilmoqda...
timeout /t 6 >nul
start http://localhost:5500
echo.
echo Tayyor! Sayt: http://localhost:5500   Admin: http://localhost:5500/admin.html   API hujjati: http://127.0.0.1:8000/docs
pause
