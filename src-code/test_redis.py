import redis

# Create a redis client

redisClient = redis.StrictRedis(host='localhost',

                                port=6379,

                                db=0)

# Add key value pairs to the Redis hash

redisClient.hset("NumberVsString", "1", "One")

redisClient.hset("NumberVsString", "2", "Two")

redisClient.hset("NumberVsString", "3", "Three")

# Retrieve the value for a specific key

print("Value for the key 3 is")

print(redisClient.hget("NumberVsString", "3"))

print("The keys present in the Redis hash:");

print(redisClient.hkeys("NumberVsString"))

print("The values present in the Redis hash:");

print(redisClient.hvals("NumberVsString"))

print("The keys and values present in the Redis hash are:")

print(redisClient.hgetall("NumberVsString"))