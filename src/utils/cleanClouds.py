import os
import glob
import argparse
import traceback

from cleanCloud import cleanCloud


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

    parser.add_argument('--verbose', action='store_true',
                        help='Print to console.')

    args = parser.parse_args()

    try:
        pcd_files = glob.glob(f"{args.pcd_directory}/**/*.las", recursive=True)

        for pcd_file in pcd_files:

            # Create a cleanCloud instance
            cloud_cleaner = cleanCloud(pcd_file=pcd_file,
                                       output_dir=args.output_dir,
                                       intensity_thresh=args.intensity_thresh,
                                       perimeter_thresh=args.perimeter_thresh,
                                       min_point_thresh=args.min_point_thresh,
                                       verbose=args.verbose)

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