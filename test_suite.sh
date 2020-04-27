#!/bin/bash
#Author: Chris Benfante

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
echo Starting set and get test...
curl -s --data "key=my_key&val=my_val" 0.0.0.0:8080/route
rep=$(curl 0.0.0.0:8080/route?key=my_key)
echo $rep
if [ "$rep" != 'my_val' ]
then
    echo TEST FAILURE: Value returned is not correct
    sudo docker-compose down
    exit 1
fi

echo Set and Get test successful!

# Verify that the node location is correct (node 3)
rep=$(curl 0.0.0.0:8080/route_test?key=my_key)
echo $rep
if [ "$rep" != '172.23.0.5:5000' ]
then
    echo TEST FAILURE: Wrong IP address was returned, possible mapping error
    sudo docker-compose down
    exit 1
fi

echo Routed to correct node!

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

sleep 5

# Verify that the node location is correct (node 4)
rep=$(curl 0.0.0.0:8080/route_test?key=my_key)
echo $rep
if [ "$rep" != '172.23.0.7:5000' ]
then
    echo TEST FAILURE: Incorrect route after adding node 4
    sudo docker-compose down
    exit 1
fi

echo Add node successful!

# Test: Remove Node
## Add a key between 9000 and 3000 (should reside in Node 1)
curl -s --data "key=test_key&val=value2" 0.0.0.0:8080/route
curl -s 0.0.0.0:8080/remove_node/172.23.0.7:5000
rep=$(curl 0.0.0.0:8080/route?key=test_key)
echo $rep
if [ "$rep" != 'value2' ]
then
    echo TEST_FAILURE: Value returned is not correct
    sudo docker-compose down
    exit 1
fi

rep=$(curl 0.0.0.0:8080/route_test?key=my_key)
echo $rep
if [ "$rep" != '172.23.0.5:5000' ]
then
    echo TEST FAILURE: Value returned is not correct
    sudo docker-compose down
    exit 1
fi

sudo docker-compose down
