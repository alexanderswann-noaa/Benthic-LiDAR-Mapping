# -----------------------------------------------------------------------------------------------------------
# Import Statements
# -----------------------------------------------------------------------------------------------------------

import time

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

def getLasInfo(loc, file):
    result = subprocess.run([loc, file, "-stdout"], shell=True, capture_output=True, text=True)
    return result.stdout

def TIMEparse_lasinfo_report(report):
    min_pattern = re.compile(r'gps_time\s+([\d\.]+)\s+([\d\.]+)')
    min_match = min_pattern.search(report)
    min_values = list(map(float, min_match.groups()))

    startTime = min_values[0] + 1000000000
    endTime = min_values[1] + 1000000000

    sec = [startTime, endTime]
    las_t_in = Time(sec, format='gps')
    las_t_out = Time(las_t_in, format='iso', scale='utc')
    print(las_t_out)

    las_t_out2 = Time(las_t_out, format='unix')

    return las_t_out2.to_value('unix', subfmt='float')


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class processLASdir:
    def __init__(self, input_dir,  output_dir):
        self.tracksDf = None
        print("\n\n")
        announce("Start of New Object")
        self.input_dir = input_dir
        self.output_dir = output_dir


    @classmethod #https://www.programiz.com/python-programming/methods/built-in/classmethod
    def fromArgs(cls, args):

        my_path = args.file
        output_directory = args.output_dir


        return cls(input_dir=my_path,
                               output_dir=output_directory)

    def add(self):
        announce("Input DIR: " + self.input_dir)

    def processLASdir(self):
        directory = self.input_dir
        outputDirectory = self.output_dir

        fileList = os.listdir(directory)

        print("Files and directories in '", directory, "' :")
        print(fileList)
        tracksData = []

        for file in fileList:
            if file.endswith(".las"):
                print("Processing file:", file)

                lasinfo = r".\build\lasinfo.exe"
                print(lasinfo)
                lasinfo_report = getLasInfo(lasinfo, (os.path.join(directory, file)))

                # print(lasinfo_report)

                min_vals = TIMEparse_lasinfo_report(lasinfo_report)
                print(min_vals[0], min_vals[1])

                # #new_row = pd.DataFrame(
                #     {'min_x': [min_vals[0]], 'min_y': [min_vals[1]], 'max_x': [max_vals[0]], 'max_y': [max_vals[1]],
                #      'box_file_name': [file], 'box_file_path': [(os.path.join(directory, file))]})
                tracksData.append([min_vals[0], min_vals[1], file, (os.path.join(directory, file))])
                # print(new_row)

                # pd.concat([tracksDf, new_row], ignore_index=False)

        tracksDf = pd.DataFrame(tracksData, columns=['Tstart', 'Tend', 'box_file_name', 'box_file_path'])

        output_base_dir = outputDirectory
        os.makedirs(output_base_dir, exist_ok=True)

        tracksDf.to_csv(os.path.join(output_base_dir, "tracks.csv"))

        self.tracksDf = tracksDf




    def run(self):
        """

                    """
        announce("Template Workflow")
        t0 = time.time()

        self.processLASdir()

        announce("Workflow Completed")

        print(f"NOTE: Completed in {np.around(((time.time() - t0) / 60), 2)} minutes")

def main():
    """

    """

    parser = argparse.ArgumentParser(description='extract all of the times from specific las files.')
    parser.add_argument('--pcd_dir', type=str, help='Directory containing the LAS files.')
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




        workflow2 = processLASdir(input_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                            output_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput")

        workflow2.run()

        print(workflow2.tracksDf)

        print("All Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())







if __name__ == '__main__':

    main()