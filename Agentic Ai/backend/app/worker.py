from __future__ import annotations

import os
import time
from rq import Connection, Worker
import redis

from .config import settings


def run_worker() -> None:
    redis_url = settings.REDIS_URL
    conn = redis.from_url(redis_url)
    queues = ["default"]
    with Connection(conn):
        worker = Worker(queues)
        worker.work(with_scheduler=True)


if __name__ == "__main__":
    run_worker()


