#!/bin/bash

route_url='0.0.0.0:8080/route'
#route_query = "?key=my_key"
#add_node_url = "0.0.0.0:8080/add_node/8000/172.23.0.7"

# Start docker
sudo docker-compose up -d

# Wait for the service to be up and responsive
rep=$(curl --data "key=my_key&val=my_val" --connect-timeout 5 --retry 5 --retry-delay 15 -s -o /dev/null -w "%{http_code}" $route_url)
echo $rep
if [ "$rep" != '200' ]
then
    echo ERROR: Failed to contact Docker endpoint, did Docker start correctly?
    sudo docker-compose down # Clean up
    exit 1 # Exit with error
fi

# Test: Set and Get Key/Value pair
curl -s --data "key=my_key&val=my_val" 0.0.0.0:8080/route
rep=$(curl 0.0.0.0:8080/route?key=my_key)
echo $rep
if [ "$rep" != 'my_val' ]
then
    echo TEST FAILURE: Value returned is not correct
    sudo docker-compose down
    exit 1
fi

# Test: Add Node
curl -s 0.0.0.0:8080/add_node/8000/172.23.0.7:5000
rep=$(curl 0.0.0.0:8080/route?key=my_key)
echo $rep
if [ "$rep" != 'my_val' ]
then
    echo TEST FAILURE: Value returned is not correct, migration error
    sudo docker-compose down
    exit 1
fi

sudo docker-compose down
