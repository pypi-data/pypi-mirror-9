from credis.redis import Redis

client = Redis.connect(port=10000)
print client.info()
