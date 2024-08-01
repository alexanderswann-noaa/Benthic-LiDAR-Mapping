import os
import glob
import argparse
import traceback

from cleanCloud import cleanCloud


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class cleanClouds:
    def __init__(self,
                 pcd_dir,
                 output_dir,
                 intensity_thresh=100,
                 density_thresh=7000,
                 min_point_thresh=100000,
                 knn=6,
                 nSigma=10,
                 verbose=False,
                 export = True):

        self.pcd_directory = pcd_dir
        self.output_dir = output_dir
        self.intensity_thresh = intensity_thresh
        self.density_thresh = density_thresh
        self.min_point_thresh = min_point_thresh
        self.verbose = verbose
        self.export = export
        # Params for SOR filter
        self.knn = knn
        self.nSigma = nSigma

    def cleanDir(self):

        pcd_files = glob.glob(f"{self.pcd_directory}/**/*.las", recursive=True)

        for pcd_file in pcd_files:

            # Create a cleanCloud instance
            cloud_cleaner = cleanCloud(pcd_file=pcd_file,
                                       output_dir=self.output_dir,
                                       intensity_thresh=self.intensity_thresh,
                                       density_thresh=self.density_thresh,
                                       min_point_thresh=self.min_point_thresh,
                                       knn = self.knn,
                                       nSigma=self.nSigma,
                                       verbose=self.verbose,
                                       export = self.export)

            # Load point cloud
            cloud_cleaner.load_pcd()

            # Clean the cloud
            cloud_cleaner.clean()
        print("Done.")

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------

def main():
    """

    """
    parser = argparse.ArgumentParser(description='Process and classify point clouds.')

    parser.add_argument('--pcd_directory', type=str, required=True,
                        help='Path to point cloud file (las).')

    parser.add_argument('--output_dir', type=str, default="./data/processed",
                        help='Directory to save the processed files.')

    parser.add_argument('--intensity_thresh', type=int, default=100,
                        help='Threshold for point perimeter squared.')

    parser.add_argument('--perimeter_thresh', type=int, default=7000,
                        help='Threshold for point perimeter squared.')

    parser.add_argument('--min_point_thresh', type=int, default=100000,
                        help='Minimum points threshold.')

    parser.add_argument('--knn', type=int, required=False,
                  default=6,
                  metavar='K Nearest Neighbors',
                  help='number of neighbors (must be an int)')

    parser.add_argument('--nSigma', type=float, required=False,
                                      default=10,
                                      help='number of sigmas under which the points should be kept')


    parser.add_argument('--verbose', action='store_true',
                        help='Print to console.')

    parser.add_argument('--export', default=True,
                                        help='Should the cleaned point clouds be saved to their own folder.',
                                        action='store_true')

    args = parser.parse_args()

    try:
        pcd_files = glob.glob(f"{args.pcd_directory}/**/*.las", recursive=True)

        for pcd_file in pcd_files:

            # Create a cleanCloud instance
            cloud_cleaner = cleanCloud(pcd_file=args.pcd_file,
                                       output_dir=args.output_dir,
                                       intensity_thresh=args.intensity_thresh,
                                       density_thresh=args.density_thresh,
                                       min_point_thresh=args.min_point_thresh,
                                       knn = args.knn,
                                       nSigma = args.nSigma,
                                       verbose=args.verbose,
                                       export = args.export)

            # Load point cloud
            cloud_cleaner.load_pcd()

            # Clean the cloud
            cloud_cleaner.clean()
        print("Done.")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()