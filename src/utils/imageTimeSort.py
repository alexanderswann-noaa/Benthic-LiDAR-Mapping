# -----------------------------------------------------------------------------------------------------------
# Import Statements
# -----------------------------------------------------------------------------------------------------------

import time

import os
import pandas as pd
import shutil
import traceback
import argparse

import numpy as np

from lasTimeTagging import processLASdir as lasProcess

from imageTimeTagging import processIMGdir as imgProcess


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


def is_within_box_Time(image_time, box, secsOffset):
    return box['Tstart'] - secsOffset <= image_time <= box['Tend'] + secsOffset


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class IMGsort:
    def __init__(self, tracks_df, images_df, output_dir):
        print("\n\n")
        announce("Start of New Object")
        self.tracksDf = tracks_df
        self.imagesDf = images_df
        self.outputDirectory = output_dir

    @classmethod  # https://www.programiz.com/python-programming/methods/built-in/classmethod
    def fromArgs(cls, args):

        tracks_df_csv = args.tracks_df
        output_directory = args.output_dir
        images_df_csv = args.images_df




        tracks_df = pd.read_csv(tracks_df_csv)
        images_df = pd.read_csv(images_df_csv)


        return cls(tracks_df=tracks_df,
                   images_df=images_df,
                   output_dir=output_directory)

    def IMGsort(self):
        boxes_df = self.tracksDf
        images_df = self.imagesDf
        outputDirectory = self.outputDirectory

        sortedOutputDirectory = os.path.join(outputDirectory, "Sorted Images")
        if not os.path.exists(sortedOutputDirectory):
            os.makedirs(sortedOutputDirectory)


        output_base_dir = sortedOutputDirectory
        os.makedirs(output_base_dir, exist_ok=True)
        for _, box in boxes_df.iterrows():
            box_file_name = box['box_file_name']
            box_dir = os.path.join(output_base_dir, box_file_name)

            os.makedirs(box_dir, exist_ok=True)

            shutil.copy(box['box_file_path'], os.path.join(box_dir, box_file_name))

        for _, box in boxes_df.iterrows():
            box_file_name = box['box_file_name']
            box_dir = os.path.join(output_base_dir, box_file_name)

            secsOffset = 4

            images_in_box = images_df[
                images_df.apply(lambda img: is_within_box_Time(img['time'], box, secsOffset), axis=1)]

            for _, image in images_in_box.iterrows():
                shutil.copy(image['file_path'], os.path.join(box_dir, image['file_name']))
        # print(tracksDf)

    def add(self):
        announce("Input DIR: " + self.input_dir)

    def run(self):
        """

                    """
        announce("Template Workflow")
        t0 = time.time()

        self.IMGsort()

        announce("Workflow Completed")

        print(f"NOTE: Completed in {np.around(((time.time() - t0) / 60), 2)} minutes")


def main():
    """

    """

    parser = argparse.ArgumentParser(description='Process and classify point clouds.')
    parser.add_argument('--tracks_df', type=str, help='Directory containing the LAS files.')
    parser.add_argument('--output_dir', type=str, default='.', help='Directory to save the processed files.')
    parser.add_argument('--images_df', type=str, default='.', help='Directory to save the processed files.')

    args = parser.parse_args()
    print(args)
    print(type(args))

    try:

        # Run the workflow

        #
        # #python "C:\Users\Alexander.Swann\PycharmProjects\pythonProject\src\classTemplate.py" "hello" --output_dir "hello again" --file "my_files yay"
        # workflow = IMGsort.fromArgs(args = args)
        #
        # workflow.run()
        #
        #
        #
        #
        # workflow2 = IMGsort(tracks_df="input_path",
        #                     images_df="project_file",
        #                     output_dir="output_path")
        #
        # workflow2.run()

        tracks = lasProcess(input_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                            output_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput")
        tracks.run()

        images = imgProcess(input_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                            output_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput")
        images.run()

        imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
        imgSort.run()

        print("All Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()
