var1="3.16.111.212"
var2="3.21.171.240"
var3="3.15.191.148"
loadbalancer="152.46.19.77:80"

echo 'flush_all' | nc $var1 11211
echo 'flush_all' | nc $var2 11211
echo 'flush_all' | nc $var3 11211

curl --data 'data={"nodes":[{"ip":"3.16.111.212:80","key":3000},{"ip":"3.21.171.240:80","key":8000}]}' $var1":80"/hash_ring
curl --data 'data={"nodes":[{"ip":"3.16.111.212:80","key":3000},{"ip":"3.21.171.240:80","key":8000}]}' $var2":80"/hash_ring
curl --data 'data={"nodes":[{"ip":"3.16.111.212:80","key":3000},{"ip":"3.21.171.240:80","key":8000}]}' $var3":80"/hash_ring