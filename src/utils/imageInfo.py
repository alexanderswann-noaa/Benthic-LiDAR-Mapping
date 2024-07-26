


import subprocess
import utm
import exifread
from gooey import Gooey, GooeyParser
import os
import shutil
import pandas as pd
from astropy.time import Time
import re




















def processIMGdir(imgdirectory, outputDirectory):
    imagesData = []
    imgfileList = os.listdir(imgdirectory)
    output_base_dir = outputDirectory
    os.makedirs(output_base_dir, exist_ok=True)

    img_csv = True

    if img_csv == True:
        for file in imgfileList:
            if file.endswith(".jpg") or file.endswith(".tif"):
                print("Processing file:", file)

                valTime = getImgTIME((os.path.join(imgdirectory, file)))

                imagesData.append([valTime, (os.path.join(imgdirectory, file)), file])

                # new_row = pd.DataFrame(
                # {'x': [vals[0]], 'y': [vals[1]],
                #   'file_path': [(os.path.join(imgdirectory, file))], 'file_name': [file]})

                # pd.concat([imagesDf, new_row], ignore_index=False)
        imagesDf = pd.DataFrame(imagesData, columns=['time', 'file_path', 'file_name'])

        imagesDf.to_csv(os.path.join(output_base_dir, "images.csv"))
    else:
        # imagesDf = pd.read_csv(os.path.join(output_base_dir, "images.csv"))
        csv_path = r"Z:\NCCOS-temp\Swann\data\experimental\output\images.csv"
        imagesDf = pd.read_csv(csv_path)

        print("00803409324")
        print(imagesDf.head(5))
        imagesDf.to_csv(os.path.join(output_base_dir, "images1.csv"))

    return imagesDf


def getImgTIME(filename):
    exif_data = get_image_exif(filename)

    dateOriginal = str(_get_if_exist(exif_data, 'EXIF DateTimeOriginal'))
    secOriginal = str(_get_if_exist(exif_data, 'EXIF SubSecTimeOriginal'))

    date_sec_og = dateOriginal + secOriginal[1:]

    imgTime = replace_date_colons(date_sec_og)

    img_t_in = Time(imgTime, format='iso', scale='utc')
    img_t_out = Time(img_t_in, format='unix')


    return img_t_out.to_value('unix', subfmt='float')

def get_image_exif(imageLoc):
    f = open(imageLoc, 'rb')

    # Return Exif tags
    return exifread.process_file(f)

def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None

def replace_date_colons(date_time_str):
    # Check if the date is already in the correct format (YYYY-MM-DD)
    if re.match(r'\d{4}-\d{2}-\d{2}', date_time_str[:10]):
        return date_time_str

    # If not, replace the colons in the date part with hyphens
    modified_date_time_str = re.sub(r'(\d{4}):(\d{2}):(\d{2})', r'\1-\2-\3', date_time_str)
    return modified_date_time_str

















lasinfo = r"C:\Users\Alexander.Swann\.conda\envs\CloudComPy310\pkgs\lastools-20171231-h0e60522_1002\Library\bin\lasinfo.exe"
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
def is_within_box(image_x, image_y, box):
    return box['min_x'] <= image_x <= box['max_x'] and box['min_y'] <= image_y <= box['max_y']
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
    print("altitude" + str(gps_altitude))

    if gps_altitude and gps_altitude_ref:
        alt = gps_altitude.values[0]
        altitude = alt.num / alt.den
        if gps_altitude_ref.values[0] == 1: altitude *= -1

    #print("altitude" + altitude)
    return lat, lon, altitude

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

def getImgUTM(filename):
    loc = get_image_location(filename)
    return utm.from_latlon(loc[0], loc[1])


#
# #
# #
# # las_file = r"C:\Users\Alexander.Swann\Documents\GitHub\Benthic-LiDAR-Mapping\data\processed\project.las"
# # #las_file = r"B:\Xander\Raw Data\Dive013_LAS\laser\processed_LLS_2024-03-15T040816.010100_0_1.las"
# # #las_file = r"B:\Xander\Raw Data\Dive013_LAS\laser\processed_LLS_2024-03-15T042110.010100_1_1.las"
#
# las_file = r"Z:\NCCOS-temp\Swann\data\processed\all14processed\lasFiles\SMALLprocessed_LLS_2024-03-15T052913.010100_0_3.las"
# las_file = r"B:\Xander\outputs\dive07\images\bad\BADprocessed_LLS_2024-06-29T041621.007600_1_2.las\BADprocessed_LLS_2024-06-29T041621.007600_1_2.las"
#
# las_file = r"Z:\NCCOS-temp\Swann\data\output\SMALLprocessed_LLS_2024-03-15T052240.010100_0_2.las\SMALLprocessed_LLS_2024-03-15T052240.010100_0_2.las"
# #
# #
# # #filename = r"Z:\NCCOS-temp\Swann\OR2401_DIVE014\Images\ESC_stills_processed_2024-03-15T060242.523586_12443.jpg"
# # filename = r"Z:\NCCOS-temp\Swann\OR2401_DIVE014\Images\ESC_stills_raw_2024-03-15T053046.023600_8846.tif"
# #
# #
# #
# #
#
# filename = r"Z:\NCCOS-temp\Swann\data\output\SMALLprocessed_LLS_2024-03-15T052240.010100_0_2.las\ESC_stills_processed_2024-03-15T052337.523586_8034.jpg"
# # imgUTM = getImgUTM(filename)
# # print(imgUTM)
# #
# # #____
# exif_data = get_image_exif(filename)
#
#
#
#
#
# dateOriginal = str(_get_if_exist(exif_data, 'EXIF DateTimeOriginal'))
# secOriginal = str(_get_if_exist(exif_data, 'EXIF SubSecTimeOriginal'))
#
# print(dateOriginal)
# print(secOriginal)
#
# print(dateOriginal + secOriginal[1:])
#
# date_sec_og = dateOriginal + secOriginal[1:]
#
# imgTime = replace_date_colons(date_sec_og)
#
#
# date_time_str1 = "2024:03:15 05:23:38"
#
# print(replace_date_colons(date_time_str1))  # Output: 2024-03-15 05:23:38
#
#
#
#
#
#
# lasinfo_report = getLasInfo(lasinfo, las_file)
# min_pattern = re.compile(r'gps_time\s+([\d\.]+)\s+([\d\.]+)')
# min_match = min_pattern.search(lasinfo_report)
# min_values = list(map(float, min_match.groups()))
#
# startTime = min_values[0] + 1000000000
# endTime = min_values[1] + 1000000000
#
#
# sec = [startTime, endTime]
# las_t_in = Time(sec, format='gps')
# las_t_out = Time(las_t_in, format='iso', scale='utc')
# print(las_t_out)
#
#
# las_t_out2 = Time(las_t_out, format='unix').to_value('unix', subfmt='float')
#
#
# print("Time 1")
# print(las_t_out2[0], las_t_out2[1])
#
#
# img_t_in = Time(imgTime, format = 'iso', scale='utc')
# img_t_out = Time(img_t_in, format = 'unix').to_value('unix', subfmt='float')
# print("Time 2")
#
# print(img_t_out)
#
#
# print(min_values)
#
# secsOffset = 4
# result = las_t_out2[0] - secsOffset <= img_t_out <= las_t_out2[1] + secsOffset
# print(result)
# #
#
# # print(exif_data)
# # print(lasinfo_report)
# #
# # min_vals, max_vals = parse_lasinfo_report(lasinfo_report)
# #
# # vals = [min_vals, max_vals]
# #
# # print("Min values:", min_vals)
# # print("Max values:", max_vals)
# #
# # print(isInside(vals, imgUTM))



@Gooey
def main():
    """
    Main function to parse arguments and initiate processing.
    """
    parser = GooeyParser(description='Process and classify point clouds.')
    parser.add_argument('directory', type=str, help='Directory containing the LAS files.', widget='DirChooser')
    parser.add_argument('imgdirectory', type=str, help='Directory containing the image files.', widget='DirChooser')
    parser.add_argument('outputDirectory', type=str, help='Directory to save the processed files.', widget='DirChooser')

    # parser.add_argument('--exportOption', type=str, choices=["all", "large_output", "small_output"], default='all',
    #                     help='Choose which output files to export (all, output, small_output). Default is all.')
    # parser.add_argument('--processingOption', type=str, choices=["all", "data cleaning", "aligning"], default='all',
    #                     help='Choose which output files to export (all, output, small_output). Default is all.')

    args = parser.parse_args()

    directory = args.directory
    imgdirectory = args.imgdirectory
    outputDirectory = args.outputDirectory
    # exportOption = args.exportOption
    # processingOption = args.processingOption


    # Process each LAS file in the directory

    tracksDf = processLASdir(directory, outputDirectory )
    imagesDf = processIMGdir(imgdirectory, outputDirectory )

    #sort Images
    IMGsort(tracksDf, imagesDf, outputDirectory)



if __name__ == "__main__":
    main()

