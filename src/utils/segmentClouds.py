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
                 empty_cell_fill_option = "KRIGING",
                 pcd_above_seafloor_thresh=0.08,
                 intensity_threshold=320,
                 coral_cell_size=0.02,
                 coral_min_comp_size=10,
                 max_coral_pts=5000,
                 fish_cell_size=0.06,
                 fish_min_comp_size=10,
                 exportOption="small_output",
                 verbose=True):

        self.pcd_directory = pcd_dir
        self.output_dir = output_dir
        # TODO add short explanations for these
        # Used in separating fish
        # (should be lower if _, should be higher if _)
        self.fish_cell_size = fish_cell_size

        # Used in...
        # (should be lower if _, should be higher if _)
        self.coral_cell_size = coral_cell_size

        # Used in creating DEM
        # (should be lower if _, should be higher if _)
        self.dem_grid_step = dem_grid_step
        self.empty_cell_fill_option = empty_cell_fill_option
        print(self.empty_cell_fill_option)

        # Used in calculating the distance between...
        # (should be lower if _, should be higher if _)
        self.pcd_above_seafloor_thresh = pcd_above_seafloor_thresh

        # Used in calculating...
        # (should be lower if _, should be higher if _)
        self.coral_min_comp_size = coral_min_comp_size

        # Used in calculating...
        # (should be lower if _, should be higher if _)
        self.fish_min_comp_size = fish_min_comp_size

        # Used in calculating...
        # (should be lower if _, should be higher if _)
        self.max_coral_pts = max_coral_pts

        self.exportOption = exportOption

        self.intensity_threshold = intensity_threshold

        self.verbose = verbose

    def cleanDir(self):

        pcd_files = glob.glob(f"{self.pcd_directory}/**/*.las", recursive=True)

        for pcd_file in pcd_files:
            cloud_segmentor = segmentCloud(pcd_file=pcd_file,
                                           output_dir=self.output_dir,
                                           dem_grid_step=self.dem_grid_step,
                                           empty_cell_fill_option=self.empty_cell_fill_option,
                                           pcd_above_seafloor_thresh=self.pcd_above_seafloor_thresh,
                                           intensity_threshold=self.intensity_threshold,
                                           coral_cell_size=self.coral_cell_size,
                                           fish_cell_size=self.fish_cell_size,
                                           fish_min_comp_size=self.fish_min_comp_size,
                                           coral_min_comp_size=self.coral_min_comp_size,
                                           max_coral_pts=self.max_coral_pts,
                                           exportOption=self.exportOption,
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
    parser = argparse.ArgumentParser(description='Segment point clouds.')

    parser.add_argument('--pcd_file', type=str, required=True,
                        help='Path to point cloud file (las).')

    parser.add_argument('--output_dir', type=str, default="./data/processed",
                        help='Directory to save the processed files.')

    # 'Optional Arguments for Segmenting Corals',

    parser.add_argument('--pcd_above_seafloor_thresh', type=float, required=False,
                        default=0.08,
                        help='Points above this Value will be added to the Potential Coral Cloud that is used later to identify corals.')

    parser.add_argument('--intensity_threshold', type=float, required=False,
                        default=320,
                        help='Points below this intensity value will be added to the Potential Coral Cloud that is used later to identify corals.')

    parser.add_argument('--coral_cell_size', type=float, required=False,
                        default=0.02,
                        help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Corals.')
    parser.add_argument('--coral_min_comp_size', type=int, required=False,
                        default=10,
                        help='The smallest number of grouped points that will be classified as coral.')

    parser.add_argument('--max_coral_pts', type=float, required=False,
                        default=5000,
                        help='The largest number of grouped points that will be classified as coral.')

    # 'Optional Arguments for Segmenting Fish'

    parser.add_argument('--fish_cell_size', type=float, required=False,
                        default=0.06,
                        help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Fish.')

    parser.add_argument('--fish_min_comp_size', type=int, required=False,
                        default=10,
                        help='The smallest number of grouped points that will be classified as fish.')

    # 'Optional Arguments for Creating DEM'

    parser.add_argument('--dem_grid_step', type=float, required=False,
                        default=.07,
                        help='The Grid step used to create the DEM.')

    parser.add_argument('--empty_cell_fill_option', type=str, required=False,
                        default="KRIGING",
                        help='How should the values for empty spaces be filled. OPTIONS: "LEAVE_EMPTY", "FILL_MINIMUM_HEIGHT","FILL_MAXIMUM_HEIGHT","FILL_CUSTOM_HEIGHT","FILL_AVERAGE_HEIGHT","INTERPOLATE_DELAUNAY","KRIGING"')

    # 'Other Optional Arguments'

    parser.add_argument('--exportOption', type=str, required=False,
                        default="small_output",
                        help='What should be outputed? Options are "small_output", "large_output", "all" ')
    parser.add_argument('--verbose', default=True,
                        help='Should Information be Printed to the Console.',
                        action='store_true')

    args = parser.parse_args()

    try:
        pcd_files = glob.glob(f"{args.pcd_directory}/**/*.las", recursive=True)

        for pcd_file in pcd_files:

            # Create a cleanCloud instance
            cloud_segmentor = segmentCloud(pcd_file=pcd_file,
                                           output_dir=args.output_dir,
                                           dem_grid_step=args.dem_grid_step,
                                           empty_cell_fill_option=args.empty_cell_fill_option,
                                           pcd_above_seafloor_thresh=args.pcd_above_seafloor_thresh,
                                           intensity_threshold=args.intensity_threshold,
                                           coral_cell_size=args.coral_cell_size,
                                           fish_cell_size=args.fish_cell_size,
                                           fish_min_comp_size=args.fish_min_comp_size,
                                           coral_min_comp_size=args.coral_min_comp_size,
                                           max_coral_pts=args.max_coral_pts,
                                           exportOption=args.exportOption,
                                           verbose=args.verbose)

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