# Define the image
# Author: Chris Benfante

FROM ubuntu:latest
ENV MODE=DEV
RUN apt-get update -y
RUN apt-get install -y curl wget
RUN apt-get install -y python-pip python-dev build-essential
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
