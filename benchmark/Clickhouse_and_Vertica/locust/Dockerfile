FROM locustio/locust
COPY . /locust
RUN python -m pip install --upgrade pip
RUN pip install -r /locust/requirements.txt
CMD apt-get update