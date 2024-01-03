#!/bin/python3.12
import subprocess

run_docker = True

with open('version') as f:
  version = f.readline()
# Build Docker image
subprocess.run(["docker", "build", "-t", "youtube-downloader", "."])


if not run_docker:
# Tag Docker images
  subprocess.run(["docker", "tag", "youtube-downloader", "naterfute/youtube-downloader:latest"])
  subprocess.run(["docker", "tag", "youtube-downloader", f"naterfute/youtube-downloader:{version}"])
# Push Docker images to Docker Hub
  subprocess.run(["docker", "push", "naterfute/youtube-downloader:latest"])
  subprocess.run(["docker", "push", f"naterfute/youtube-downloader:{version}"])
else:
  subprocess.run(["docker", "run", "-p", "5000:5000", "youtube-downloader"])
