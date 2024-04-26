FROM python:3.12-alpine

WORKDIR /usr/src/app

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

# Copy the rest of the app to the container
COPY . .

# Run the app
CMD ["python3", "-O", "run.py"]
