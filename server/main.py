import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List

import uvicorn
from fastapi import FastAPI, Query
from routers import alert, picture

app = FastAPI()

app.include_router(alert.router)
app.include_router(picture.router)


@app.get("/")
async def root():
    """
    A function that serves as the root endpoint for the API.

    Returns:
        dict: A dictionary containing the message "Hello World".
    """
    return {"message": "Hello World"}


@app.post("/single_thread")
async def single_thread(numbers: List[int] = Query(default=[])):

    print(numbers)
    start = time.time()

    for _ in numbers:
        three_sleep()

    return {"elapsed_time": f"{time.time() - start:.2f}s"}


def three_sleep():
    time.sleep(3)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
