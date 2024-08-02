FROM python:3.11-bookworm

RUN apt-get update -y
RUN apt-get install -y tippecanoe
ADD . /raveoli
WORKDIR /raveoli
RUN pip install -r requirements.txt
CMD python main.py