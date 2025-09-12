FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080 \
    MODEL_DIR=/opt/ml/model \
    OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    libstdc++6 \
    libgfortran5 \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /opt/ml/model /opt/program
WORKDIR /opt/program

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn

COPY . /opt/program
ENV PYTHONPATH=/opt/program

COPY serve /usr/local/bin/serve
RUN chmod +x /usr/local/bin/serve

EXPOSE 8080
CMD ["serve"]
