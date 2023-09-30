FROM python:3.11-slim-bullseye

# Set the working directory
WORKDIR /app

# Prevent Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE 1

# Prevent Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# Install project dependencies using pip
COPY ./requirements/. /app/
RUN pip install --no-cache-dir -r /app/production.txt

# Copy the rest of the application code
COPY . /app/

RUN mkdir -p /app/app/logs/
# Set the entry point
ENTRYPOINT ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]
