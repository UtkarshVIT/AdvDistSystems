#!/bin/bash -       
#title           :reconfigure.sh
#author		     :Utkarsh Sharma
#usage		     :sh reconfigure.sh
#description     :This script will reconfigure the system to default State
#==============================================================================

node1="3.16.111.212:80"
node2="3.21.171.240:80"
node3="3.15.191.148:80"
loadbalancer="152.46.19.77:80"

curl $node1/clear_cache
curl $node2/clear_cache
curl $node3/clear_cache

curl --data 'data={"nodes":[{"ip":"'$node1'","key":3000},{"ip":"'$node2'","key":8000}]}' $node2/hash_ring
curl --data 'data={"nodes":[{"ip":"'$node1'","key":3000},{"ip":"'$node2'","key":8000}]}' $node1/hash_ring
curl --data 'data={"nodes":[{"ip":"'$node1'","key":3000},{"ip":"'$node2'","key":8000}]}' $node3/hash_ring