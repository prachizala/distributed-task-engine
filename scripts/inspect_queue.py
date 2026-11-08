import redis


def inspect_celery_queues(redis_host: str = "localhost", redis_port: int = 6379):
    try:
        r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        r.ping()
        print("Connected to Redis broker.")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")
        return

    queues = ["default", "celery", "dead_letter"]
    for q in queues:
        length = r.llen(q)
        print(f"Queue '{q}': {length} pending messages")


if __name__ == "__main__":
    inspect_celery_queues()
