FROM python:3.8

WORKDIR /usr/src/app
COPY Code/requirements.txt .
RUN pip install -r requirements.txt