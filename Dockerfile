# Start with a minimal Python base image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /workspace

# Install necessary dependencies and clean up in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
	ffmpeg && \
	apt-get clean && \
	rm -rf /var/lib/apt/lists/*

# Copy application files to the container
COPY . .

# Upgrade pip and install required Python packages in one step to minimize layers
RUN pip install --no-cache-dir --upgrade pip && \
	pip install --no-cache-dir --upgrade -r server-requirements.txt

# Expose the required port
EXPOSE 8080

# Command to run the application
CMD ["python3", "app.py", "--log-level=DEBUG"]

