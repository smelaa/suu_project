from fastapi import FastAPI, Request
import socket

app = FastAPI()

@app.get("/ip")
async def get_ip(request: Request):
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    return {"ip": ip_address}