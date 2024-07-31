import os
import glob
import argparse
import traceback

from segmentCloud import segmentCloud


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class segmentClouds:
    def __init__(self,
                 pcd_dir,
                 output_dir,
                 dem_grid_step=.07,
                 pcd_above_seafloor_thresh=0.08,

                 coral_cell_size=0.02,
                 fish_cell_size=0.06,
                 min_comp_size=10,
                 verbose=True):

        self.pcd_directory = pcd_dir
        self.output_dir = output_dir
        self.dem_grid_step = dem_grid_step
        self.pcd_above_seafloor_thresh = pcd_above_seafloor_thresh
        self.coral_cell_size = coral_cell_size
        self.fish_cell_size =fish_cell_size
        self.min_comp_size =min_comp_size
        self.verbose = verbose

    def cleanDir(self):

        pcd_files = glob.glob(f"{self.pcd_directory}/**/*.las", recursive=True)

        for pcd_file in pcd_files:
            cloud_segmentor = segmentCloud(pcd_file=pcd_file,
                                           output_dir=self.output_dir,
                                           verbose=self.verbose)

            # Load the cloud
            cloud_segmentor.load_pcd()

            # Segment the cloud
            cloud_segmentor.segment()

        print("Done.")

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------

def main():
    """

    """
    parser = argparse.ArgumentParser(description='Process and classify point clouds.')

    parser.add_argument('--pcd_dir', type=str, required=True,
                        help='Path to point cloud file (las).')

    parser.add_argument('--output_dir', type=str, default="./data/processed",
                        help='Directory to save the processed files.')
    #
    # parser.add_argument('--intensity_thresh', type=int, default=100,
    #                     help='Threshold for point perimeter squared.')
    #
    # parser.add_argument('--perimeter_thresh', type=int, default=7000,
    #                     help='Threshold for point perimeter squared.')
    #
    # parser.add_argument('--min_point_thresh', type=int, default=100000,
    #                     help='Minimum points threshold.')

    # dem_grid_step = .07,
    # pcd_above_seafloor_thresh = 0.08,
    #
    # coral_cell_size = 0.02,
    # fish_cell_size = 0.06,
    # min_comp_size = 10,

    parser.add_argument('--verbose', action='store_true',
                        help='Print to console.')

    args = parser.parse_args()

    try:
        pcd_files = glob.glob(f"{args.pcd_directory}/**/*.las", recursive=True)

        for pcd_file in pcd_files:

            # Create a cleanCloud instance
            cloud_segmentor = segmentCloud(pcd_file=pcd_file,
                                           output_dir=args.output_dir)

            # Load the cleaned cloud from file
            cloud_segmentor.load_pcd()

            # Segment the cloud
            cloud_segmentor.segment()

        print("Done.")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()