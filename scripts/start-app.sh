#!/bin/bash

# Development App Starter with File Watching
# This script starts your Docker containers in development mode with hot reload

echo "🚀 Starting SIH Health Chatbot (Development Mode)"
echo "================================================"

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please copy env.example to .env and update with your values"
    echo ""
fi

# Start Docker containers in development mode
echo "🐳 Starting Docker containers with file watching..."
docker-compose -f docker-compose.dev.yml up --build

echo ""
echo "🎉 Application started in development mode!"
echo ""
echo "🔍 To check logs:"
echo "   docker logs sih-backend-dev"
echo "   docker logs cloudflared-dev"
echo ""
echo "🛑 To stop the application:"
echo "   docker-compose -f docker-compose.dev.yml down"
echo ""
echo "📋 Your tunnel URL will be shown in the cloudflared logs above"
echo "💡 Copy the URL and manually update your WhatsApp webhook in Meta Developer Console"
echo ""
echo "🔄 File watching is enabled - changes to src/ will automatically reload!"
echo ""