FROM python:3.12 AS base
# Set the working directory in the container
WORKDIR /app
# Copy the dependencies file and install them
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy the rest of the application code to the container
COPY . .
# Expose port 8080
EXPOSE 8080
# Command to run the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]