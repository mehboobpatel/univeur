# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy and install pip requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade pip

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    unixodbc-dev \
    gcc \
    g++ \
    curl \
    gnupg2 \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft ODBC Driver for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . /app
EXPOSE 5000

# Set the default command to run the application
CMD ["python", "app.py"]
