# AdvDistSystems
Creating a scalable key value store.

##### Running the system
docker-compose up [This shows the logs and attaches the host session to the logs of the spawned containers]

docker-compose up -d [This spawns the containers in detached mode. i.e. without attaching to logs]

##### Stopping the system
docker-compose down

##### How to send a request 
Steps:
1. Using a second terminal session, attach to any of the containers in the network
docker exec -it advdistsystems_app1_1 bash

2. Send Request to the load balancer
curl 172.23.0.6:8080/route?key=temp [Note, ip of load balancer: 172.23.0.6]

If running the system in attached mode, you should be able to see the output in logs.
