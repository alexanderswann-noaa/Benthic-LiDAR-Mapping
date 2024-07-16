

import re
import subprocess
import utm
import exifread
import pandas as pd
from gooey import Gooey, GooeyParser
import os
import shutil
import pandas as pd





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




def is_within_box(image_x, image_y, box):
    return box['min_x'] <= image_x <= box['max_x'] and box['min_y'] <= image_y <= box['max_y']



lasinfo = r"C:\Users\Alexander.Swann\.conda\envs\CloudComPy310\pkgs\lastools-20171231-h0e60522_1002\Library\bin\lasinfo.exe"
#
#
# las_file = r"C:\Users\Alexander.Swann\Documents\GitHub\Benthic-LiDAR-Mapping\data\processed\project.las"
# #las_file = r"B:\Xander\Raw Data\Dive013_LAS\laser\processed_LLS_2024-03-15T040816.010100_0_1.las"
# #las_file = r"B:\Xander\Raw Data\Dive013_LAS\laser\processed_LLS_2024-03-15T042110.010100_1_1.las"
#
#
# #filename = r"Z:\NCCOS-temp\Swann\OR2401_DIVE014\Images\ESC_stills_processed_2024-03-15T060242.523586_12443.jpg"
# filename = r"Z:\NCCOS-temp\Swann\OR2401_DIVE014\Images\ESC_stills_raw_2024-03-15T053046.023600_8846.tif"
#
#
#
#
# imgUTM = getImgUTM(filename)
# print(imgUTM)
#
# #____
# lasinfo_report = getLasInfo(lasinfo, las_file)
#
# print(lasinfo_report)
#
# min_vals, max_vals = parse_lasinfo_report(lasinfo_report)
#
# vals = [min_vals, max_vals]
#
# print("Min values:", min_vals)
# print("Max values:", max_vals)
#
# print(isInside(vals, imgUTM))




@Gooey
def main():
    """
    Main function to parse arguments and initiate processing.
    """
    parser = GooeyParser(description='Process and classify point clouds.')
    parser.add_argument('directory', type=str, help='Directory containing the LAS files.', widget='DirChooser')
    parser.add_argument('imgdirectory', type=str, help='Directory containing the image files.', widget='DirChooser')
    parser.add_argument('outputDirectory', type=str, help='Directory to save the processed files.', widget='DirChooser')
    parser.add_argument('--exportOption', type=str, choices=["all", "large_output", "small_output"], default='all',
                        help='Choose which output files to export (all, output, small_output). Default is all.')
    parser.add_argument('--processingOption', type=str, choices=["all", "data cleaning", "aligning"], default='all',
                        help='Choose which output files to export (all, output, small_output). Default is all.')

    args = parser.parse_args()

    directory = args.directory
    imgdirectory = args.imgdirectory
    outputDirectory = args.outputDirectory
    exportOption = args.exportOption
    processingOption = args.processingOption


    tracksData = []
    imagesData = []







    fileList = os.listdir(directory)
    imgfileList = os.listdir(imgdirectory)
    print("Files and directories in '", directory, "' :")
    print(fileList)

    # Process each LAS file in the directory

    for file in fileList:
        if file.endswith(".las"):
            print("Processing file:", file)

            lasinfo_report = getLasInfo(lasinfo, (os.path.join(directory, file)))

            print(lasinfo_report)


            min_vals, max_vals = parse_lasinfo_report(lasinfo_report)
            print(min_vals)

            # #new_row = pd.DataFrame(
            #     {'min_x': [min_vals[0]], 'min_y': [min_vals[1]], 'max_x': [max_vals[0]], 'max_y': [max_vals[1]],
            #      'box_file_name': [file], 'box_file_path': [(os.path.join(directory, file))]})
            tracksData.append([ min_vals[0], min_vals[1],  max_vals[0], max_vals[1], file, (os.path.join(directory, file))   ])
            #print(new_row)

            #pd.concat([tracksDf, new_row], ignore_index=False)

    tracksDf = pd.DataFrame(tracksData, columns=['min_x', 'min_y', 'max_x', 'max_y', 'box_file_name', 'box_file_path'])
    output_base_dir = outputDirectory
    os.makedirs(output_base_dir, exist_ok=True)

    tracksDf.to_csv(os.path.join(output_base_dir, "tracks.csv"))

    img_csv = False

    if img_csv == True:
        for file in imgfileList:
            if file.endswith(".jpg") or file.endswith(".tif"):
                print("Processing file:", file)


                vals = getImgUTM((os.path.join(imgdirectory, file)))

                imagesData.append([ vals[0], vals[1], (os.path.join(imgdirectory, file)), file ])

                #new_row = pd.DataFrame(
                    # {'x': [vals[0]], 'y': [vals[1]],
                    #   'file_path': [(os.path.join(imgdirectory, file))], 'file_name': [file]})

                #pd.concat([imagesDf, new_row], ignore_index=False)
        imagesDf = pd.DataFrame(imagesData, columns=['x', 'y', 'file_path', 'file_name'])

        imagesDf.to_csv(os.path.join(output_base_dir, "images.csv"))
    else:
        #imagesDf = pd.read_csv(os.path.join(output_base_dir, "images.csv"))
        imagesDf = pd.read_csv(r"Z:\NCCOS-temp\Swann\data\experimental\output\images.csv")

        print("00803409324")
        print(imagesDf.head(5))
        imagesDf.to_csv(os.path.join(output_base_dir, "images1.csv"))




    # Load data into pandas DataFrames





    boxes_df = tracksDf
    images_df = imagesDf








    for _, box in boxes_df.iterrows():
        box_file_name = box['box_file_name']
        box_dir = os.path.join(output_base_dir, box_file_name)

        os.makedirs(box_dir, exist_ok=True)

        shutil.copy(box['box_file_path'], os.path.join(box_dir, box_file_name))

    for _, box in boxes_df.iterrows():
        box_file_name = box['box_file_name']
        box_dir = os.path.join(output_base_dir, box_file_name)

        images_in_box = images_df[images_df.apply(lambda img: is_within_box(img['x'], img['y'], box), axis=1)]

        for _, image in images_in_box.iterrows():
            shutil.copy(image['file_path'], os.path.join(box_dir, image['file_name']))
    print(tracksDf)

if __name__ == "__main__":
    main()

