FROM python:3.11-bullseye

RUN apt-get update -y
ADD . /tivetiler
WORKDIR /tivetiler
RUN pip install -r requirements.txt
CMD python main.py