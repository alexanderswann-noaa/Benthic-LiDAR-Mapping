import time

import numpy as np

import argparse
import os
import traceback
import utm
import exifread

from common import announce

import pandas as pd


def getImgUTM(filename):
    loc = get_image_location(filename)
    return utm.from_latlon(loc[0], loc[1]), loc[2]


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

def _get_if_exist(data, key):
    if key in data:
        return data[key]

    return None


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
    print("altitude: " + str(gps_altitude))

    if gps_altitude and gps_altitude_ref:
        alt = gps_altitude.values[0]
        altitude = alt.num / alt.den
        if gps_altitude_ref.values[0] == 1: altitude *= -1

    #print("altitude" + altitude)
    return lat, lon, altitude







# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class imageLocation:
    def __init__(self, input_dir,  output_dir):
        self.imagesDf = None
        print("\n\n")
        announce("Start of New Object")
        self.input_dir = input_dir
        self.output_dir = output_dir


    @classmethod #https://www.programiz.com/python-programming/methods/built-in/classmethod
    def fromArgs(cls, args):

        my_path = args.img_path
        output_directory = args.output_dir


        return cls(input_dir=my_path,
                               output_dir=output_directory)

    def add(self):
        announce("Input DIR: " + self.input_dir)

    def processIMGdir(self):
        imgdirectory = self.input_dir
        outputDirectory = self.output_dir

        imagesData = []
        imgfileList = os.listdir(imgdirectory)
        output_base_dir = outputDirectory
        os.makedirs(output_base_dir, exist_ok=True)

        img_csv = True

        if img_csv == True:
            for file in imgfileList:
                if file.endswith(".jpg") or file.endswith(".tif"):
                    print("Processing file:", file)

                    valTime = getImgUTM((os.path.join(imgdirectory, file)))

                    #print(valTime)

                    imagesData.append([valTime[0], (os.path.join(imgdirectory, file)), file, valTime[1]])

                    # new_row = pd.DataFrame(
                    # {'x': [vals[0]], 'y': [vals[1]],
                    #   'file_path': [(os.path.join(imgdirectory, file))], 'file_name': [file]})

                    # pd.concat([imagesDf, new_row], ignore_index=False)
            imagesDf = pd.DataFrame(imagesData, columns=['location', 'file_path', 'file_name', 'm_above_sealevel'])

            imagesDf.to_csv(os.path.join(output_base_dir, "images.csv"))
        else:
            # imagesDf = pd.read_csv(os.path.join(output_base_dir, "images.csv"))
            csv_path = r"Z:\NCCOS-temp\Swann\data\experimental\output\images.csv"
            imagesDf = pd.read_csv(csv_path)

            print("00803409324")
            print(imagesDf.head(5))
            imagesDf.to_csv(os.path.join(output_base_dir, "images1.csv"))

        self.imagesDf = imagesDf





    def run(self):
        """

                    """
        announce("Template Workflow")
        t0 = time.time()

        self.processIMGdir()

        announce("Workflow Completed")

        print(f"NOTE: Completed in {np.around(((time.time() - t0) / 60), 2)} minutes")

def main():
    """

    """

    parser = argparse.ArgumentParser(description='extract all of the times from specific las files.')
    parser.add_argument('--img_path', type=str, help='Directory containing the image files.')
    parser.add_argument('--output_dir', type=str, help='Directory to save the processed files.')

    args = parser.parse_args()
    print(args)
    print(type(args))

    try:

        # Run the workflow


        #python "C:\Users\Alexander.Swann\PycharmProjects\pythonProject\src\classTemplate.py" "hello" --output_dir "hello again" --file "my_files yay"
        # workflow = myClass.fromArgs(args = args)
        #
        # workflow.run()




        workflow2 = imageLocation(input_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                            output_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput")

        workflow2.run()

        print(workflow2.imagesDf)

        print("All Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())







if __name__ == '__main__':

    main()