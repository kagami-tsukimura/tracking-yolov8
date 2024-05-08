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
    """
    A function that performs a single-threaded operation with a list of numbers.

    Parameters:
        - numbers (List[int]): A list of integers to process.

    Returns:
        dict: A dictionary containing the elapsed time in string format.
    """

    start = time.time()

    for _ in numbers:
        three_sleep()

    return {"elapsed_time": f"{time.time() - start:.2f}s"}


@app.post("/multi_thread")
async def multi_thread(numbers: List[int] = Query(default=[])):

    start = time.time()
    tasks = []

    # マルチスレッドで並列処理
    with ThreadPoolExecutor() as executor:
        for _ in numbers:
            tasks.append(
                asyncio.get_event_loop().run_in_executor(executor, three_sleep)
            )

    # すべてのタスクが完了するのを待つ
    await asyncio.gather(*tasks)

    return {"elapsed_time": f"{time.time() - start:.2f}s"}


def three_sleep():
    time.sleep(3)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
