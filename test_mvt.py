import json
from shapely.geometry import shape, mapping, box
import mercantile
from shapely.ops import clip_by_rect
import mapbox_vector_tile


def tile_to_box(z, x, y):
    """Convert tile coordinates to a bounding box"""
    tile_bounds = mercantile.bounds(mercantile.Tile(x=x, y=y, z=z))
    return (tile_bounds.west, tile_bounds.south, tile_bounds.east, tile_bounds.north)

def cut_polygon_by_xyz(source_geojson_path, z, x, y, output_geojson_path='output.geojson'):
    # Load the source GeoJSON file
    with open(source_geojson_path) as f:
        source_data = json.load(f)
    
    # Convert GeoJSON features to Shapely geometries
    source_geometries = [shape(feature['geometry']) for feature in source_data['features']]
    
    # Create the clipping box
    clipping_box = tile_to_box(z, x, y)
    
    # Clip the geometries
    clipped_geometries = [clip_by_rect(geom,*clipping_box) for geom in source_geometries if not geom.is_empty]
    
    # Create the output GeoJSON
    clipped_features = [{
        "type": "Feature",
        "geometry": mapping(geom),
        "properties": source_data['features'][i]['properties']
    } for i, geom in enumerate(clipped_geometries) if not geom.is_empty]
    
    clipped_data = {
        "type": "FeatureCollection",
        "features": clipped_features
    }
    
    # Save the clipped geometries to a GeoJSON file
    with open(output_geojson_path, 'w') as f:
        json.dump(clipped_data, f)

    return clipped_data

def generate_mvt(clipped_data, output_mvt_path='output_file.pbf'):
    from mapbox_vector_tile import encode
    
    records = clipped_data['features']

    print(records)
    
    layer = {
        "name": "your_layer_name",
        "features": records
    }
    
    mvt_data = mapbox_vector_tile.encode([layer])
    decoded_mvt_data = mapbox_vector_tile.decode(mvt_data)
    print(decoded_mvt_data)
    
    with open(output_mvt_path, 'wb') as f:
        f.write(mvt_data)

# Example tile coordinates
z, x, y = 10, 706, 366

clipped_data = cut_polygon_by_xyz('central_asia_boundary.geojson', z, x, y)
generate_mvt(clipped_data)
