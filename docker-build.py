#!/bin/python3.12
import subprocess

run_docker = False

with open('version') as f:
  version = f.readline()
# Build Docker image
subprocess.run(["docker", "build", "-t", "youtube-downloader", "."])

# Tag Docker images
subprocess.run(["docker", "tag", "youtube-downloader", "naterfute/youtube-downloader:latest"])
subprocess.run(["docker", "tag", "youtube-downloader", f"naterfute/youtube-downloader:{version}"])

# Push Docker images to Docker Hub
if not run_docker:
  subprocess.run(["docker", "push", "naterfute/youtube-downloader:latest"])
  subprocess.run(["docker", "push", f"naterfute/youtube-downloader:{version}"])
else:
  subprocess.run(["docker", "run", "-p", "5000:5000", "naterfute/youtube-downloader:latest"])
