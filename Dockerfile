# =============================================================================
# Multi-stage Dockerfile for FoodScanAI
# Build targets: backend, frontend
# =============================================================================

# -----------------------------------------------------------------------------
# Backend Target
# -----------------------------------------------------------------------------
FROM python:3.11-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# -----------------------------------------------------------------------------
# Frontend Target - BUILD REACT DI SINI
# -----------------------------------------------------------------------------
FROM node:18-alpine AS frontend-build

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install --legacy-peer-deps

# Copy source code
COPY frontend/ .

# Set memory limit
ENV NODE_OPTIONS=--max-old-space-size=4096

# Build React app
RUN npm run build

# -----------------------------------------------------------------------------
# Frontend Target - Serve with Nginx
# -----------------------------------------------------------------------------
FROM nginx:alpine AS frontend

# Copy built files from build stage
COPY --from=frontend-build /app/build /usr/share/nginx/html

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]