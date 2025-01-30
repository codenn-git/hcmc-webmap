import os
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import geopandas as gpd
from shapely.geometry import Point
import pandas as pd
import pillow_heif  # Ensures HEIC support in Pillow


# Function to extract EXIF data
def extract_exif(image_path):
    image = Image.open(image_path)
    exif_data = image._getexif()  # Access EXIF metadata
    if not exif_data:
        return None

    # Map and parse tags
    exif = {TAGS.get(tag, tag): value for tag, value in exif_data.items()}
    gps_info = exif.get("GPSInfo")
    if gps_info:
        gps_data = {GPSTAGS.get(tag, tag): value for tag, value in gps_info.items()}
        exif["GPSInfo"] = gps_data

    return exif

# Function to get GPS coordinates from EXIF
def get_coordinates(gps_info):
    def convert_to_degrees(value):
        d, m, s = value
        return d + (m / 60.0) + (s / 3600.0)

    if gps_info and "GPSLatitude" in gps_info and "GPSLongitude" in gps_info:
        lat = convert_to_degrees(gps_info["GPSLatitude"])
        lon = convert_to_degrees(gps_info["GPSLongitude"])
        if gps_info["GPSLatitudeRef"] == "S":
            lat = -lat
        if gps_info["GPSLongitudeRef"] == "W":
            lon = -lon
        return lat, lon
    return None, None

# Main function to create GeoDataFrame
def create_geodataframe(base_folder):
    data = {}
    for root, dirs, files in os.walk(base_folder):
        sidewalk_use = os.path.basename(root)
        for file in files:
            if file.lower().endswith(".heic"):
                file_path = os.path.join(root, file)
                exif_data = extract_exif(file_path)
                if exif_data:
                    gps_info = exif_data.get("GPSInfo")
                    lat, lon = get_coordinates(gps_info)
                    date_time = exif_data.get("DateTime")
                    if lat and lon:
                        # If the image already exists, append the sidewalk use
                        if file in data:
                            data[file]["sidewalk_use"].append(sidewalk_use)
                        else:
                            data[file] = {
                                "image_name": file,
                                "latitude": lat,
                                "longitude": lon,
                                "datetime": date_time,
                                "sidewalk_use": [sidewalk_use],  # Start as a list
                            }

    # Convert dictionary to DataFrame
    rows = []
    for key, value in data.items():
        # Join sidewalk_use into a comma-separated string
        value["sidewalk_use"] = ", ".join(value["sidewalk_use"])
        rows.append(value)

    df = pd.DataFrame(rows)
    geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
    return gdf

def main():
    # Define the base folder path
    base_folder = input("Enter the path to the folder: ").strip()
    
    # Generate the GeoDataFrame
    print("Processing images and creating GeoDataFrame...")
    gdf = create_geodataframe(base_folder)

    # Output file path
    output_path = input("Enter the output file path (e.g., output.geojson): ").strip()
    print("Saving GeoDataFrame to:", output_path)
    gdf.to_file(output_path, driver="GeoJSON")

    # Print a preview
    print("GeoDataFrame created:")
    print(gdf.head())

# Entry point of the script
if __name__ == "__main__":
    main()