# Use a small official Python image
FROM python:3.12-slim

# Create a working directory inside the container
WORKDIR /app

# Install system dependencies (optional but handy for many Python libs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
&& rm -rf /var/lib/apt/lists/*

# Copy requirements first so Docker can cache dependencies if code changes
COPY requirements.txt .

# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src ./src

# Make sure Python can import the "app" package from /app/src
ENV PYTHONPATH=/app/src

# Cloud Run expects the container to listen on port 8080
EXPOSE 8080

# Start the FastAPI app with Uvicorn when the container runs
CMD ["python", "-m", "uvicorn", "app.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8080"]
