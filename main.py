import json
import os
import mercantile
import tempfile
import pyogrio
from fastapi.responses import FileResponse
from fastapi.openapi.models import Response
from pyogrio import read_info, read_dataframe
import uvicorn
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers
from fastapi import FastAPI
from mapbox_vector_tile import encode as mvt_encode

from factories import TilerFactory
from utils import create_vector_tile

app = FastAPI(title="TiVeTiler")

cog = TilerFactory()
app.include_router(cog.router, tags=["Cloud Optimized GeoTIFF Router"])

add_exception_handlers(app, DEFAULT_STATUS_CODES)


@app.get("/healthz", description="Health Check", tags=["Health Check"])
def ping():
    """Health check."""
    return {"ping": "pong!"}


@app.get("/vector/bounds", description="Bounds of vector file")
def bounds(uri, security_params=None):
    """Health check."""
    if security_params is not None:
        security_params = json.loads(security_params)
        for k, v in security_params.items():
            os.environ[k] = v
    print(f'URI: {uri}')
    return read_info(uri)['total_bounds']


@app.get("/vector/crs", description="Bounds of vector file")
def crs(uri, security_params=None):
    """Health check."""
    if security_params is not None:
        security_params = json.loads(security_params)
        for k, v in security_params.items():
            os.environ[k] = v
    return read_info(uri)['crs']


@app.get("/vector/geometry_type", description="Bounds of vector file")
def crs(uri, security_params=None):
    """Health check."""
    if security_params is not None:
        security_params = json.loads(security_params)
        for k, v in security_params.items():
            os.environ[k] = v
    return read_info(uri)['geometry_type']


@app.get("/vector/fields", description="Bounds of vector file")
def fields(uri, security_params=None):
    """Health check."""
    if security_params is not None:
        security_params = json.loads(security_params)
        for k, v in security_params.items():
            os.environ[k] = v
    return list(read_info(uri)['fields'])


@app.get("/vector/info", description="Bounds of vector file")
def info(uri, security_params=None):
    if security_params is not None:
        security_params = json.loads(security_params)
        for k, v in security_params.items():
            os.environ[k] = v
    return str(read_info(uri))


@app.get("/vector/driver", description="Bounds of vector file")
def driver(uri, security_params=None):
    """Health check."""
    if security_params is not None:
        security_params = json.loads(security_params)
        for k, v in security_params.items():
            os.environ[k] = v
    return read_info(uri)['driver']


@app.get('/vector/tiles')
def vector_tile(uri:str, z:int, x:int, y:int):
    print('Creating vector tile...')
    created_vector_tile = create_vector_tile(uri, z, x, y)
    if created_vector_tile:
        print('Successfully created vector tile, now sending to user...')
    else:
        return Response(status_code=404)
    return FileResponse(path=created_vector_tile, filename=f'{z}_{x}_{y}.pbf')

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
