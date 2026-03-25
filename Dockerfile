FROM python:3.11-slim

WORKDIR /workspace/app

COPY requirements.txt /workspace/requirements.txt
RUN pip install --no-cache-dir -r /workspace/requirements.txt

COPY backend/ .

EXPOSE 5000
CMD ["python", "App.py"]
