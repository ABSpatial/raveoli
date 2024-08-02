import os

import pyogrio
import requests
import subprocess
import uuid
import sqlite3
import mercantile
from shapely.geometry import box
from geojson2vt.geojson2vt import geojson2vt


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

        print(" ".join(command))
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
            print("Tiles", tiles)
    if tiles:
        return True
    else:
        return False

def create_vector_tile(vector_path, z, x, y):
    layername = str(uuid.uuid4())
    source_df = pyogrio.read_dataframe(vector_path, bbox=tile_to_bbox(z,x,y))

    source_df.to_parquet(f"{layername}.parquet")

    mbtiles_output = layername + '.mbtiles'
    wrapper = TippecanoeWrapper(input_file=layername + '.parquet',
                                output=mbtiles_output,
                                output_to_directory=False,
                                min_zoom=z,
                                max_zoom=z,
                                layer=layername)
    wrapper.run()
    if tile_exists(mbtiles_output, z, x, y):
        os.remove(layername)
        os.remove(f"{layername}.parquet")
        return mbtiles_output
    else:
        return False

print(create_vector_tile('lithotype.fgb', 0,0,0))