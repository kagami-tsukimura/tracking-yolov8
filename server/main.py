import uvicorn
from fastapi import FastAPI
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
