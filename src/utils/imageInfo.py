

import re
import subprocess
import utm
import exifread
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString
from pyproj import Transformer
import matplotlib.pyplot as plt




def getLasInfo(loc, file):
    result = subprocess.run([loc, file, "-stdout"], shell=True, capture_output=True, text=True)
    return result.stdout



def parse_lasinfo_report(report):

    min_pattern = re.compile(r'min x y z:\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)')
    max_pattern = re.compile(r'max x y z:\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)')


    min_match = min_pattern.search(report)
    max_match = max_pattern.search(report)


    if not min_match or not max_match:
        raise ValueError("Could not find min or max x y z values in the report.")


    min_values = list(map(float, min_match.groups()))
    max_values = list(map(float, max_match.groups()))

    return min_values, max_values


import exifread


# based on https://gist.github.com/erans/983821

def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


def _convert_to_degress(value):
    """
    Helper function to convert the GPS coordinates stored in the EXIF to degress in float format
    :param value:
    :type value: exifread.utils.Ratio
    :rtype: float
    """
    d = float(value.values[0].num) / float(value.values[0].den)
    m = float(value.values[1].num) / float(value.values[1].den)
    s = float(value.values[2].num) / float(value.values[2].den)

    return d + (m / 60.0) + (s / 3600.0)

def get_image_exif(imageLoc):
    f = open(imageLoc, 'rb')

    # Return Exif tags
    return exifread.process_file(f)

def get_image_location(filename):
    """
    Returns the latitude and longitude, if available, from the provided exif_data (obtained through get_exif_data above)
    """
    exif_data = get_image_exif(filename)

    lat = None
    lon = None

    gps_latitude = _get_if_exist(exif_data, 'GPS GPSLatitude')
    gps_latitude_ref = _get_if_exist(exif_data, 'GPS GPSLatitudeRef')
    gps_longitude = _get_if_exist(exif_data, 'GPS GPSLongitude')
    gps_longitude_ref = _get_if_exist(exif_data, 'GPS GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = _convert_to_degress(gps_latitude)
        if gps_latitude_ref.values[0] != 'N':
            lat = 0 - lat

        lon = _convert_to_degress(gps_longitude)
        if gps_longitude_ref.values[0] != 'E':
            lon = 0 - lon

    gps_altitude_ref = _get_if_exist(exif_data, 'GPS GPSAltitudeRef')
    gps_altitude = _get_if_exist(exif_data, 'GPS GPSAltitude')

    if gps_altitude and gps_altitude_ref:
        alt = gps_altitude.values[0]
        altitude = alt.num / alt.den
        if gps_altitude_ref.values[0] == 1: altitude *= -1

    return lat, lon, altitude

def getImgUTM(filename):
    loc = get_image_location(filename)
    return utm.from_latlon(loc[0], loc[1])

def isInside(box, img):
    utm_points = [
        (box[0][0], box[1][0]),
        (box[0][0], box[1][1]),


        (box[0][1], box[1][1]),
        (box[0][1], box[1][0])
    ]

    if img[0] > box[0][0] and img[0] < box[1][0]:
        if img[1] > box[0][1] and img[1] < box[1][1]:
            return "the photo is a part of the track!!"
    else:
        return "the photo is not a part of the track"




    # Define UTM coordinate for an additional point
    utm_point_additional = (img[0], img[1])



lasinfo = r"C:\Users\Alexander.Swann\.conda\envs\CloudComPy310\pkgs\lastools-20171231-h0e60522_1002\Library\bin\lasinfo.exe"
las_file = r"C:\Users\Alexander.Swann\Documents\GitHub\Benthic-LiDAR-Mapping\data\processed\project.las"
#las_file = r"B:\Xander\Raw Data\Dive013_LAS\laser\processed_LLS_2024-03-15T040816.010100_0_1.las"


#filename = r"Z:\NCCOS-temp\Swann\OR2401_DIVE014\Images\ESC_stills_processed_2024-03-15T060242.523586_12443.jpg"

filename = r"Z:\NCCOS-temp\Swann\OR2401_DIVE014\Images\ESC_stills_raw_2024-03-15T053046.023600_8846.tif"



imgUTM = getImgUTM(filename)
print(imgUTM)

#____
lasinfo_report = getLasInfo(lasinfo, las_file)

#print(lasinfo_report)

min_vals, max_vals = parse_lasinfo_report(lasinfo_report)

vals = [min_vals, max_vals]

print("Min values:", min_vals)
print("Max values:", max_vals)

print(isInside(vals, imgUTM))
