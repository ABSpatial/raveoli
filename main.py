import json
import os

import pyogrio
from fastapi.openapi.models import Response
from pyogrio import read_info, read_dataframe
import uvicorn
from titiler.core.errors import DEFAULT_STATUS_CODES, add_exception_handlers
from fastapi import FastAPI
from mapbox_vector_tile import encode as mvt_encode

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
def vector_tile(uri, z, x, y, security_params=None):
    """Serve vector tiles."""
    if security_params is not None:
        security_params = json.loads(security_params)
        for k, v in security_params.items():
            os.environ[k] = v
    z,x,y = int(z), int(x), int(y)
    tile_bounds = tile_to_bounds(x, y, z)

    tile_data = pyogrio.read_dataframe(uri, bbox=tile_bounds)
    tile_geojson = json.loads(tile_data.to_json())
    print(tile_geojson)

    mvt_data = mvt_encode(tile_geojson, quantize_bounds=None)

    # Serve the MVT data as PBF
    return Response(content=mvt_data, media_type='application/x-protobuf')


def tile_to_bounds(x, y, z):
    # Convert tile coordinates to web mercator bounds
    tile_size = 256
    max_resolution = 156543.03392804097
    origin_shift = 20037508.342789244
    res = max_resolution / (2 ** z)
    x_min = -origin_shift + x * tile_size * res
    y_max = origin_shift - y * tile_size * res
    x_max = -origin_shift + (x + 1) * tile_size * res
    y_min = origin_shift - (y + 1) * tile_size * res
    return (x_min, y_min, x_max, y_max)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
