var1="152.7.99.216"
var2="152.7.99.95"
var3="152.7.99.108"
loadbalancer="152.46.19.77:80"

echo 'flush_all' | nc $var1 11211
echo 'flush_all' | nc $var2 11211
echo 'flush_all' | nc $var3 11211

curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":8000}]}' $var1":80"/hash_ring
curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":8000}]}' $var2":80"/hash_ring
curl --data 'data={"nodes":[{"ip":"152.7.99.216:80","key":3000},{"ip":"152.7.99.95:80","key":8000}]}' $var3":80"/hash_ring