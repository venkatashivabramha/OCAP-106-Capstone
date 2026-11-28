@echo off
echo Starting ISL Chat...
start cmd /k "cd /d d:\Cap\backend && python manage.py runserver 127.0.0.1:8000"
timeout /t 4 /nobreak >nul
start cmd /k "cd /d d:\Cap\frontend\isl-chat-ui && npm run dev"
echo.
echo Both servers started!
echo Open: http://localhost:5173
