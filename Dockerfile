FROM python:3.11-slim

WORKDIR /app

# Install Python packages (no build tools needed now!)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY . .

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
