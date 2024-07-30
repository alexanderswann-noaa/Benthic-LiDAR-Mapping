import os
import traceback

from gooey import Gooey, GooeyParser

from cleanCloud import cleanCloud
from segmentCloud import segmentCloud


# ----------------------------------------------------------------------------------------------------------------------
# Gooey GUI
# ----------------------------------------------------------------------------------------------------------------------

@Gooey
def main():
    """
    Main function to parse arguments and initiate processing.
    """
    parser = GooeyParser(description='Process and classify point clouds.')
    subs = parser.add_subparsers(help='commands', dest='command')

    # Clean parser
    clean_parser = subs.add_parser('Clean')

    clean_parser_panel_1 = clean_parser.add_argument_group('Clean',
                                                           'Provide a path to LAS file to clean.')

    clean_parser_panel_1.add_argument('--pcd_file', type=str, required=True,
                                      metavar='Point Cloud (LAS)',
                                      help='Path to point cloud LAS file.',
                                      widget='FileChooser')

    clean_parser_panel_1.add_argument('--output_dir', type=str,
                                      default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                      help='Directory to save the processed files.')

    # TODO add all parameterized arguments here
    # Segment parser
    segment_parser = subs.add_parser('Segment')

    segment_parser_panel_1 = segment_parser.add_argument_group('Segment',
                                                               'Provide a path to LAS file to segment.')

    segment_parser_panel_1.add_argument('--pcd_file', type=str, required=True,
                                        metavar='Point Cloud (LAS)',
                                        help='Path to point cloud LAS file.',
                                        widget='FileChooser')

    segment_parser_panel_1.add_argument('--output_dir', type=str,
                                        default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                        help='Directory to save the processed files.')

    args = parser.parse_args()

    try:
        if args.command == 'Clean':
            # Create a cleanCloud instance
            cloud_cleaner = cleanCloud(pcd_file=args.pcd_file,
                                       output_dir=args.output_dir,
                                       intensity_thresh=args.intensity_thresh,
                                       perimeter_thresh=args.perimeter_thresh,
                                       min_point_thresh=args.min_point_thresh,
                                       verbose=args.verbose)

            # Load the cloud from file
            cloud_cleaner.load_pcd()

            # Clean the cloud
            cloud_cleaner.clean()

        # TODO add all parameterized arguments here
        elif args.command == 'Segment':
            # Create a segmentCloud instance
            cloud_segmentor = segmentCloud(pcd_file=args.pcd_file,
                                           output_dir=args.output_dir,

                                           verbose=args.verbose)

            # Load the cleaned cloud from file
            cloud_segmentor.load_pcd()

            # Segment the cloud
            cloud_segmentor.segment()

        print("Done.")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == "__main__":
    main()