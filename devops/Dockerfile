
FROM python:3.11-slim

# set production env
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app

# system deps for some libraries (add extras you need)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /app/requirements.txt

# copy project
COPY  ../app /app/app
COPY ../requirements.txt /app/

# expose internal port used by Hypercorn
EXPOSE 8000

# user for safety
RUN groupadd -r app && useradd -r -g app app
RUN chown -R app:app /app
USER app

# production command uses hypercorn; asgi:asgi_app points to your asgi.py -> asgi_app
CMD ["hypercorn", "asgi:asgi_app", "-b", "0.0.0.0:8000", "--workers", "3", "--access-logfile", "-", "--error-logfile", "-"]

