FROM python:3.11-bookworm

RUN echo "deb http://deb.debian.org/debian bookworm-backports main contrib non-free-firmware" | tee -a /etc/apt/sources.list
RUN apt-get update -y
RUN apt-get install -y tippecanoe
ADD . /raveoli
WORKDIR /raveoli
RUN pip install -r requirements.txt
CMD python main.py
