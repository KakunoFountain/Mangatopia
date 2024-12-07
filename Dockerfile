# Use the Python 3 official image
# https://hub.docker.com/_/python
FROM python:3

# Run in unbuffered mode
ENV PYTHONUNBUFFERED=1 

# Create and change to the app directory.
WORKDIR /app

# Copy local code to the container image.
COPY . ./

# Install project dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup.
ENTRYPOINT ["gunicorn", "-w", "2", "-b", "0.0.0.0", "src.app:app"]