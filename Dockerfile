# Production Container for SSC CGL Examination Platform
FROM python:3.9-slim

WORKDIR /app

# Copy application files
COPY . .

# Expose server port (default 3000, customizable via PORT env)
EXPOSE 3000
ENV PORT=3000
ENV PYTHONUNBUFFERED=1

# Start the multi-threaded HTTP platform
CMD ["python3", "app/server.py"]
