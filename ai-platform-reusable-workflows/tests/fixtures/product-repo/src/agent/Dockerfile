# Pin the base image to an organization-approved digest before production.
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONNOUSERSITE=1
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt \
    && useradd --uid 10001 --create-home appuser
COPY main.py prompt.py /app/
USER 10001
EXPOSE 8088
CMD ["python", "main.py"]
