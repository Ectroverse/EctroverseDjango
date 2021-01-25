FROM python:3.6
RUN apt-get update && apt-get install -y cron nano
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
pip install --upgrade pip
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
