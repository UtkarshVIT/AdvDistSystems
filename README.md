# AdvDistSystems
Creating a scalable key value store based on Dynamo.

##### Running the system
`docker-compose up` [This shows the logs and attaches the host session to the logs of the spawned containers]

`docker-compose up -d` [This spawns the containers in detached mode. i.e. without attaching to logs]

##### Stopping the system
docker-compose down

##### How to send a request 

1. Adding a key-val pair [sending POST to LB]

`curl --data "key=my_key&val=my_val" 0.0.0.0:8080/route`

2. Fetching val for a key [sending GET to LB]

`curl 0.0.0.0:8080/route?key=my_key`

*Note:* If running the system in attached mode, you should be able to see the output in logs.

##### Some useful commands
1. Attaching to a container's bash
`docker exec -it [container_name] bash`

