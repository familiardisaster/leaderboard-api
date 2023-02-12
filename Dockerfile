# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

# Expose 8080 for gunicorn
EXPOSE 8080

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
WORKDIR /app
COPY . .
RUN python -m pip install -r requirements.txt

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "api:app"]