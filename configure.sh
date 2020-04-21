var1="152.7.99.216"
var2="152.7.99.95"
var3="152.7.99.108"
loadbalancer="152.46.19.77:80"

echo 'flush_all' | nc $var1 11211
echo 'flush_all' | nc $var2 11211
echo 'flush_all' | nc $var3 11211

curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":6000}]}' $var1":80"/hash_ring
curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":6000}]}' $var2":80"/hash_ring
curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":6000}]}' $var3":80"/hash_ring

curl --data "key=space&val=my_val_space" $loadbalancer/route
curl --data "key=prison&val=my_val_prison" $loadbalancer/route
curl --data "key=fan&val=my_val_fan" $loadbalancer/route
curl --data "key=vacuum&val=my_val_vacuum" $loadbalancer/route
curl --data "key=toilet&val=my_val_toilet" $loadbalancer/route
curl --data "key=weapon&val=my_val_weapon" $loadbalancer/route

curl $loadbalancer/route?key=space
curl $loadbalancer/route?key=prison
curl $loadbalancer/route?key=fan
curl $loadbalancer/route?key=vacuum
curl $loadbalancer/route?key=toilet
curl $loadbalancer/route?key=weapon