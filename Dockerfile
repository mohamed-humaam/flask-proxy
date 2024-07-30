# Use the official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file to the working directory
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code to the working directory
COPY . .

# Set environment variables
ENV DESTINATION_URL=https://example.com
ENV DEBUG=False

# Expose the port Flask is running on
EXPOSE 5001

# Command to run the application
CMD ["python", "app.py"]
