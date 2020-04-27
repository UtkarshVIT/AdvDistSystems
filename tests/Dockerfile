# Define the image
# Author: Utkarsh Sharma

FROM ubuntu:latest
RUN apt-get update -y
RUN apt-get install -y curl wget
RUN apt-get install -y python-pip python-dev build-essential
COPY . /tests
WORKDIR /tests
RUN pip install -r requirements.txt
