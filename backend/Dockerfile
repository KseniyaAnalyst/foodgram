# backend/Dockerfile
FROM python:3.9
WORKDIR /app
RUN pip install gunicorn==20.1.0
COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi"]




# FROM python:3.12-slim

# ENV PYTHONDONTWRITEBYTECODE=1 \
#     PYTHONUNBUFFERED=1

# RUN apt-get update && apt-get install -y --no-install-recommends \
#     build-essential \
#     libjpeg62-turbo-dev \
#     zlib1g-dev \
#     libpng-dev \
#     libpq-dev \
#   && rm -rf /var/lib/apt/lists/*

# WORKDIR /app

# COPY requirements.txt ./
# RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# COPY . .

# CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]

