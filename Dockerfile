# Multi-stage Dockerfile for Telegram Bot with FastAPI + React UI

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build for production
RUN npm run build

# Stage 2: Python Backend + Bot
FROM python:3.11-slim

LABEL maintainer=cyb3rgh05t
LABEL org.opencontainers.image.source=https://github.com/cyb3rgh05t/telegram-bot

# working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Copy built frontend from Stage 1
COPY --from=frontend-builder /frontend/dist ./frontend/dist

# Expose API port (if web UI is enabled)
EXPOSE 5000

# Run the bot
CMD ["python", "bot.py"]

