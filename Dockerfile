# Slim for only what pyton needs
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download model weights 
# This is done at build time to ensure the model is ready when the container starts.
COPY download_models.py . 
RUN python download_models.py

# Copy application code
COPY app/ ./app/

# Expose the port FastAPI will run on
EXPOSE 8000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]