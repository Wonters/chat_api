import redis.asyncio as redis
import asyncio
async def main():
    m = []
    redis_client1 = await redis.Redis(host="127.0.0.1", port=6379)
    redis_client2 = await redis.Redis(host="127.0.0.1", port=6379)
    await redis_client1.xadd(f"client:1", {"t":3})
    m.append(await redis_client1.xread({f"client:1": "0"}))
    await redis_client2.xadd(f"client:1", {"t":3})
    m.append(await redis_client2.xread({f"client:1": "0"}))
    print(m)

asyncio.run(main())