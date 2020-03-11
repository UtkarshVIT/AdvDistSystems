#stop containers if running
#docker stop cont1 || true && docker rm cont1 || true
#docker stop cont2 || true && docker rm cont2 || true
docker stop cont1
docker stop cont2

#rebuild the image
docker build -t flask-sample:latest .

#deploy the containers
docker run -d --name cont1 -p 8000:8000 flask-sample
docker run -d --name cont2 -p 8001:8001 flask-sample


#docker network create myNet
docker network connect myNet cont1
docker network connect myNet cont2