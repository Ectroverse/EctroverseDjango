FROM rappdw/docker-java-python:openjdk1.8.0_171-python3.6.6
RUN java -version
RUN apt-get update && apt-get install -y cron nano 
RUN apt-get install -y python-pip
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
RUN pip install --upgrade pip
ADD requirements.txt /code/
RUN pip install -r requirements.txt
ADD . /code/
