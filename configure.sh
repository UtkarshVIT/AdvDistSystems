var1="152.7.99.216:80"
var2="152.7.99.95:80"
var3="152.7.99.108:80"
loadbalancer="152.46.19.77:80"
curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":6000}]}' $var1/hash_ring
curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":6000}]}' $var2/hash_ring
curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":6000}]}' $var3/hash_ring

curl --data "key=space&val=my_val_space" $loadbalancer/route
curl --data "key=prison&val=my_val_prison" $loadbalancer/route
curl --data "key=fan&val=my_val_fan" $loadbalancer/route
curl --data "key=vaccum&val=my_val_vaccum" $loadbalancer/route
curl --data "key=toilet&val=my_val_toilet" $loadbalancer/route
curl --data "key=wepon&val=my_val_wepon" $loadbalancer/route