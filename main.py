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
    """Serve vector tiles."""
    tile_bounds = tile_to_bounds(x, y, z)

    tile_data = pyogrio.read_dataframe(uri, bbox=(tile_bounds.west, tile_bounds.south, tile_bounds.east, tile_bounds.north))
    tile_geojson = json.loads(tile_data.to_json())

    tile_geojson['name'] = 'default'

    # Create a single layer with all the features
    mvt_data = mvt_encode(tile_geojson, quantize_bounds=None)

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(mvt_data)
        temp_file_path = temp_file.name

        # Serve the MVT data as a file using FileResponse
    return FileResponse(path=temp_file_path, media_type='application/x-protobuf', filename=f'{z}_{x}_{y}.pbf')


def tile_to_bounds(x, y, z):
    return mercantile.bounds(mercantile.Tile(x=x, y=y, z=z))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
