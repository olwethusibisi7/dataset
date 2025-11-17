# Use Python 3.8 slim image
FROM python:3.8-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY recruitment_functions.py .
COPY dashboard.py .

# Create volume mount point for persistence
VOLUME /app/data

# Expose Streamlit port
EXPOSE 8501

# Set environment variable for database location
ENV RECRUITMENT_DB_PATH=/app/data/recruitment.db

# Run the Streamlit app
CMD ["streamlit", "run", "dashboard.py"]