import math

import os
import glob
import argparse
import traceback

import CloudCompare.cloudComPy as cc
import pandas as pd
from common import announce
from lasRender import lasRender


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class lasRenderMany:
    def __init__(self,
                 bin_dir,
                 main_image_dir,
                 output_dir):


        #self.img_info = img_info
        #need to get image info
        self.output_dir = output_dir
        # Input PCD (las) file, checks
        self.bin_file = bin_dir
        self.bin_name = os.path.basename(bin_dir)
        self.bin_basename = "".join(self.bin_name.split(".")[:-1])


        self.main_image_dir = main_image_dir

        print(self.output_dir)

        print(self.bin_file)
        print(self.bin_name)
        print(self.bin_basename)

        print(self.main_image_dir)

        # assert os.path.exists(self.bin_file), "Error: PCD file doesn't exist"
        # assert self.bin_name.lower().endswith(".bin"), "Error: PCD file is not a 'bin' file"

    def renderMany(self):

        bin_files = glob.glob(f"{self.bin_dir}/**/*.bin", recursive=True)

        for bin_file in bin_files:
            print(bin_file)

        directory = self.input_dir
        outputDirectory = self.output_dir

        fileList = os.listdir(directory)

        print("Files and directories in '", directory, "' :")
        print(fileList)
        tracksData = []

        for file in fileList:
            if file.endswith(".bin"):
                print("Processing file:", file)

    def run(self):

        #self.render()
        print("Done.")


# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------

def main():
    """

    """
    parser = argparse.ArgumentParser(description='Process and classify point clouds.')

    parser.add_argument('--bin_file', type=str, required=True,
                        help='Path to point cloud file (las).')

    parser.add_argument('--img_path', type=str, help='Directory containing the image files.')

    parser.add_argument('--output_dir', type=str, default="./data/processed",
                        help='Directory to save the processed files.')

    args = parser.parse_args()

    try:
        tracks = lasRender(bin_file=args.bin_file, image_dir=args.img_dir, output_dir=args.output_dir)

        # tracks.load_pcd()

        tracks.run()
        print("Done.")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()