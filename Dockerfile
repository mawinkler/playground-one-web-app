# Step 1: Build React frontend
FROM node:22 AS build-frontend

WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build 

# Step 2: Build Flask backend
FROM python:3.12
WORKDIR /app

# Install Python dependencies
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./

# Copy React build files into Flask static folder
COPY --from=build-frontend /app/dist ./static

# Expose the Flask port
EXPOSE 5000

# Run Flask application
CMD ["python", "app.py"]
