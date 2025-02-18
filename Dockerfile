# Refer to a base image
FROM python:3.10-bookworm

# Create a new workspace to put the source code in and other stuff
WORKDIR /app

# Copy the source code into the workspace
COPY requirements.txt /app

# Install dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the workspace
COPY . /app

# Expose the port for the container to run on
EXPOSE 8000

ENV PYTHONUNBUFFERED = 1

# Provide instructions on how to run the image
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]