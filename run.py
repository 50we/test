import uvicorn

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=False,
                host="127.0.0.1", workers=4)
