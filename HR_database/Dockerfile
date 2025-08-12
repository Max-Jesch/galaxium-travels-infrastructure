FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install pandas
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p data
COPY ./data/*.md /data/*.md

# Expose the port the app runs on
EXPOSE 8081

# Command to run the application
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8081"] 