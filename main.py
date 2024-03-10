import json
import os

import fiona
import uvicorn
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers
from fastapi import FastAPI

from factories import TilerFactory

app = FastAPI(title="TiVeTiler")

cog = TilerFactory()
app.include_router(cog.router, tags=["Cloud Optimized GeoTIFF Router"])

add_exception_handlers(app, DEFAULT_STATUS_CODES)


@app.get("/healthz", description="Health Check", tags=["Health Check"])
def ping():
    """Health check."""
    return {"ping": "pong!"}


@app.get("/vector/bounds", description="Bounds of vector file")
def bounds(uri, security_params):
    """Health check."""
    security_params = json.loads(security_params)
    for k, v in security_params.items():
        os.environ[k] = v
    with fiona.open(uri) as dataset:
        return {"bounds": dataset.bounds}


@app.get("/vector/info", description="Bounds of vector file")
def info(uri, security_params):
    security_params = json.loads(security_params)
    for k, v in security_params.items():
        os.environ[k] = v
    with fiona.open(uri) as dataset:
        meta = dataset.meta
        meta.update(bounds=dataset.bounds)
        meta.update(count=len(dataset))
        meta["crs"] = dataset.crs.to_string()
        return meta


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
