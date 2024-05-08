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
async def single_thread(numbers: List[int] = Query(default=[1, 2, 3, 4, 5])):
    """
    リストのlengthだけ、3秒sleepをシングルスレッドで繰り返す関数です。

    パラメータ:
        - numbers (List[int]): 処理する整数のリスト。

    戻り値:
        dict: 経過時間(seconds)。
    """

    start = time.time()

    for _ in numbers:
        three_sleep()

    return {"elapsed_time": f"{time.time() - start:.2f}s"}


@app.post("/multi_thread")
async def multi_thread(numbers: List[int] = Query(default=[1, 2, 3, 4, 5])):
    """
    リストのlengthだけ、3秒sleepをマルチスレッドで繰り返す関数です。

    パラメータ:
        - numbers (List[int]): 処理する整数のリスト。

    戻り値:
        dict: 経過時間(seconds)。
    """

    start = time.time()
    # tasks: 並列処理するタスク（リスト）
    tasks = []

    # マルチスレッドで並列処理
    # max_workers: 並列処理する最大スレッド数（default: None）
    with ThreadPoolExecutor(max_workers=len(numbers)) as executor:
        for _ in numbers:
            # ThreadPoolExecutorで実行される非同期タスクを作成→tasksに追加
            tasks.append(
                asyncio.get_event_loop().run_in_executor(executor, three_sleep)
            )

    # すべての非同期タスクを同時実行→すべてのタスクが完了するまで待機
    await asyncio.gather(*tasks)

    return {"elapsed_time": f"{time.time() - start:.2f}s"}


def three_sleep():
    """
    Sleeps for 3 seconds.
    """

    time.sleep(3)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
