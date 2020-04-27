#!/bin/bash -       
#title           :reconfigure.sh
#author		     :Utkarsh Sharma
#usage		     :sh reconfigure.sh
#description     :This script will reconfigure the system to default State
#==============================================================================

node1="172.23.0.3:5000"
node2="172.23.0.4:5000"
node3="172.23.0.5:5000"
loadbalancer="172.23.0.6:5000"

curl $node1/clear_cache
curl $node2/clear_cache
curl $node3/clear_cache

curl --data 'data={"nodes":[{"ip":"'$node1'","key":3000},{"ip":"'$node2'","key":8000}]}' $node2/hash_ring
curl --data 'data={"nodes":[{"ip":"'$node1'","key":3000},{"ip":"'$node2'","key":8000}]}' $node1/hash_ring
curl --data 'data={"nodes":[{"ip":"'$node1'","key":3000},{"ip":"'$node2'","key":8000}]}' $node3/hash_ring