FROM python:3.12
WORKDIR /usr/local/app

# Install the application dependencies
COPY requirements.txt ./
#RUN python -m venv .venv
#RUN source .venv/bin/activate
RUN pip install --no-cache-dir -r requirements.txt

# Copy in the source code
COPY source ./source
COPY evaluation ./evaluation
COPY run_destroy_problems.py ./run_destroy_problems.py
COPY run_evaluate.py ./run_evaluate.py
#EXPOSE 5000

# Setup an app user so the container doesn't run as the root user
#RUN useradd app
#USER app


CMD ["python", "run_destroy_problems.py"]
#CMD ["python", "run_evaluate.py"]