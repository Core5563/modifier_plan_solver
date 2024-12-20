FROM python:3.12
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
#RUN python -m venv .venv
#RUN source .venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY source ./source
#EXPOSE 5000

# Setup an app user so the container doesn't run as the root user
RUN useradd app
USER app

#CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]