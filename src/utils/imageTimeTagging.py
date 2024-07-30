# -----------------------------------------------------------------------------------------------------------
# Import Statements
# -----------------------------------------------------------------------------------------------------------

import time

import exifread
import os
import pandas as pd
import subprocess
import traceback
import argparse

from astropy.time import Time
import re

import numpy as np

# -----------------------------------------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------------------------------------

def announce(announcement: str):
    """
    Print whatever you would like with formatting.
    """
    print("\n###############################################")
    print(announcement)
    print("###############################################\n")

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


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class processIMGdir:
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




        workflow2 = processIMGdir(input_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                            output_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput")

        workflow2.run()

        print(workflow2.imagesDf)

        print("All Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())







if __name__ == '__main__':

    main()