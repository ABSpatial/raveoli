import os
import sqlite3
import subprocess
import uuid

import mercantile
import pyogrio
import requests
from tqdm import tqdm


class TippecanoeWrapper:
    def __init__(self, input_file,
                 output, min_zoom=None,
                 max_zoom=None,
                 layer=None, bbox=None, output_to_directory=False):
        self.input_file = input_file
        self.output = output
        self.min_zoom = min_zoom
        self.max_zoom = max_zoom
        self.layer = layer
        self.bbox = bbox
        self.output_to_directory = output_to_directory

    def run(self):
        if not os.path.exists(self.input_file):
            raise FileNotFoundError(f"Input file {self.input_file} does not exist.")

        if self.output_to_directory:
            command = ["tippecanoe", "--output-to-directory", self.output]
        else:
            command = ["tippecanoe", "-o", self.output]

        if self.min_zoom is not None:
            command.extend(["--minimum-zoom", str(self.min_zoom)])

        if self.max_zoom is not None:
            command.extend(["--maximum-zoom", str(self.max_zoom)])

        if self.layer is not None:
            command.extend(["-l", self.layer])

        if self.bbox is not None:
            command.extend([f"--clip-bounding-box={self.bbox}"])

        if self.input_file is not None:
            command.extend([self.input_file])

        try:
            subprocess.run(command, check=True)
            return self.output
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running tippecanoe: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def tile_to_bbox(z, x, y):
    """
    Convert tile coordinates to a bounding box.
    """
    tile_bounds = mercantile.bounds(mercantile.Tile(x=x, y=y, z=z))
    return tile_bounds.west, tile_bounds.south, tile_bounds.east, tile_bounds.north


def tile_exists(layer, z, x, y):
    query = f"""
    SELECT zoom_level, tile_column, tile_row
    FROM main.tiles
    WHERE zoom_level = {z} AND tile_column = {x} AND tile_row = {y};
    """
    with sqlite3.connect(f"{layer}") as source_mbtiles:
        cursor = source_mbtiles.cursor()
        try:
            with source_mbtiles:
                cursor.execute(query)
        except Exception as e:
            raise e
        else:
            tiles = cursor.fetchall()
    if tiles:
        return True
    else:
        return False


def download(url: str, chunk_size=1024):
    resp = requests.get(url, stream=True)
    total = int(resp.headers.get('content-length', 0))
    fname = resp.headers.get('content-disposition', os.path.basename(url))
    if os.path.exists(fname):
        return fname
    with open(fname, 'wb') as file, tqdm(
            desc=fname,
            total=total,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
    ) as bar:
        for data in resp.iter_content(chunk_size=chunk_size):
            size = file.write(data)
            bar.update(size)
    return fname


def create_vector_tile(vector_path, z, x, y):
    layername = str(uuid.uuid4())

    bbox_bbox = tile_to_bbox(z, x, y)
    bbox = ",".join(map(str, bbox_bbox))

    fname = download(vector_path)

    mbtiles_output = layername + '.mbtiles'
    wrapper = TippecanoeWrapper(input_file=fname,
                                output=mbtiles_output,
                                output_to_directory=False,
                                min_zoom=z,
                                max_zoom=z,
                                layer=layername,
                                bbox=bbox)
    wrapper.run()
    if tile_exists(mbtiles_output, z, x, y):
        os.remove(fname)
        return mbtiles_output
    else:
        return False
