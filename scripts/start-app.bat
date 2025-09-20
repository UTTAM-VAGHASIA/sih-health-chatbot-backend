@echo off
REM Simple App Starter
REM This script starts your Docker containers

echo 🚀 Starting SIH Health Chatbot
echo =============================

REM Start Docker containers
echo 🐳 Starting Docker containers...
docker-compose up --build

echo.
echo 🎉 Application started!
echo.
echo 🔍 To check logs:
echo    docker logs sih-backend
echo    docker logs cloudflared
echo.
echo 🛑 To stop the application:
echo    docker-compose down
echo.
echo 📋 Your tunnel URL will be shown in the cloudflared logs above
echo 💡 Copy the URL and manually update your WhatsApp webhook in Meta Developer Console
echo.
pause