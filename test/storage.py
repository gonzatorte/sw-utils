from sw_utils.profile import RedisStorage


import redis

cache_host = 'localhost'
cache_redis_db = 10
rediscli = redis.Redis(host=cache_host, db=cache_redis_db)
r_store = RedisStorage(rediscli)

r_store.keys()

print 'ada'