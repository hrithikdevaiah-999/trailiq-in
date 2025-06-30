FROM python:3.11-slim

RUN apt-get update -qq && apt-get install -y --no-install-recommends \
        build-essential curl git  \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

ENV PORT=8050
EXPOSE ${PORT}

CMD ["gunicorn", "--chdir", "backend", "--bind", "0.0.0.0:${PORT}", "app:server"]