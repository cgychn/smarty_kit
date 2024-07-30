import uvicorn

if __name__ == '__main__':
    uvicorn.run("LanceDBServerRestful:app", host="0.0.0.0", port=8169, log_level="info")