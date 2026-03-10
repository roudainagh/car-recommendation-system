FROM python:3.9-slim

WORKDIR /app

# Install system dependencies for some ML libraries
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


# Copy requirements and install
COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the code and data----------------------------
COPY backend/ ./backend/
COPY data/ ./data/


# Expose the API port
EXPOSE 8000

# Command to run the application
#CMD ["python", "backend/api/main.py"]
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]