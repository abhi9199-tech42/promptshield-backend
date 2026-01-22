@echo off
echo ========================================
echo PromptShield Deployment Script
echo ========================================
echo.
echo Stopping any running containers...
docker-compose down

echo.
echo Building and starting containers...
docker-compose up --build -d

echo.
echo Deployment started!
echo Frontend: http://localhost:3000 (Local)
echo Backend: http://localhost:8003 (Local)
echo.
echo If you configured Cloudflare Tunnel, check the logs for the URL:
echo docker-compose logs -f tunnel
echo.
echo To stop the server, run: docker-compose down
pause
