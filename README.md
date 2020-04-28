# Scalable Key Value Store
This is the project source code for a scalable key value store based on Dynamo Db's consistent hashing policy for data partitioning. This system was created as part of the corsework for  CSC 724 (Advanced Distributed Systems). 

##### Authors
1. Utkarsh Sharma (usharma2@ncsu.edu)
2. Chris Benfante (cabenfan@ncsu.edu)

##### System Overview

###### Imp Note
The source code in the master branch is for running the system on a single host docker environment. For knowing how to run the system on [VCL](https://vcl.ncsu.edu/) or other cloud services please refer to the [production branch] (https://github.com/UtkarshVIT/AdvDistSystems/tree/production) of this repository.

###### Architechture
Each node in the system is a Ubuntu 18 image running a Flask application on the Python development server and storing the key value in the node itself using [Simple Cache](https://werkzeug.palletsprojects.com/en/0.16.x/contrib/cache/). The nodes communicate with each other via HTTP GET and POST.

###### Experimental Setup
Our present system is based on the following setup. You can modify the system based on your preferences by editing the docker-compose.yml file. We have two nodes in the default state. These two nodes are Ubuntu containers running a Flask app communicating with each other via HTTP in a docker network. There is a load balancer which uses round robin algorithm to distribute load between these two nodes. We also have a standby container running the sample Flask app which we will use later for scaling up. The fourth container is a client which will interact with the system and run the test cases.
<pre>
        (3000)                               
      ____n1___   ⇦┅┅┓      n3 (standby)       |    n1     = 172.23.0.3
     |        |      ┃                         |    n2     = 172.23.0.4
     |        |      LB  <---- client          |    n3     =  172.23.0.5
     |___n2___|   (load balancer)              |    LB     = 172.23.0.6
       (8000)                                  |  client    = 172.23.0.7 
</pre>

##### Deployment
1. Running the containers
Run the following command to deploy the system and attach the host session to the logs of the spawned containers
`$docker-compose up` 

##### Running Test Cases
1. Attach to the console of the client 
```$docker container exec -it advdistsystems_client_1 /bin/bash``` 
 
2. Reconfigure the system
Reconfigure the system to clear cache and update routing information. The [reconfigure.sh](https://github.com/UtkarshVIT/AdvDistSystems/blob/master/tests/reconfigure.sh) file in the root directory is updated with the information of the experimental setup. Update the file iff you are using a custom setup. Run the following command from the client's shell
```$sh reconfigure.sh```

3. Execute test cases.
The following command will simulate four scenarios and exectute the test cases. For detailed information on the test cases see [pytest.py](https://github.com/UtkarshVIT/AdvDistSystems/blob/master/tests/pytest.py)
```$python pytest.py```

##### Running Custom Test Cases
Repeat step 1 and 2 from the **'Running Test Cases'** section above and then proceed as follows
1. Set a env variable for the load balancer
```$lb="172.23.0.6:5000"```
1. Adding a key-val pair [sending POST to LB]
```$curl --data "key=<custom-key>&val=<custom-val>" $lb/route```

2. Fetching val for a key [sending GET to LB]
```$curl $lb/route?key=<custom-key>```

1. Adding a node to the system
```$curl --data $lb/add_node/<key-of-new-node>/<ip:port-of-new-node>```

2. Removing a node from the system
```$curl $lb/remove_node/<ip:port-of-target-node>```

##### Some useful commands
1. Attaching to a container's bash
`docker exec -it [container_name] bash`
