var1="3.16.111.212:80"
var2="3.21.171.240:80"
var3="3.15.191.148:80"
loadbalancer="152.46.19.77:80"

curl $var1/clear_cache
curl $var2/clear_cache
curl $var3/clear_cache

curl --data 'data={"nodes":[{"ip":"'$var1'","key":3000},{"ip":"'$var2'","key":8000}]}' $var2/hash_ring
curl --data 'data={"nodes":[{"ip":"'$var1'","key":3000},{"ip":"'$var2'","key":8000}]}' $var1/hash_ring
curl --data 'data={"nodes":[{"ip":"'$var1'","key":3000},{"ip":"'$var2'","key":8000}]}' $var3/hash_ring