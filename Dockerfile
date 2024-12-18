FROM python:3.10-slim

# Install dependencies
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    ffmpeg git sqlite3 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/
WORKDIR /app/

# Install Python dependencies
RUN pip3 install -U pip && \
    pip3 install --no-cache-dir -r req.txt

# Make the start script executable
RUN ["chmod", "+x", "/app/start"]

# Default command
CMD ["bash", "start"]