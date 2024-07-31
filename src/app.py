import os
import traceback
import glob

from gooey import Gooey, GooeyParser

from cleanCloud import cleanCloud
from cleanClouds import cleanClouds
from segmentCloud import segmentCloud
from segmentClouds import segmentClouds

from lasTimeTagging import processLASdir as lasProcess

from imageTimeTagging import processIMGdir as imgProcess

from imageTimeSort import IMGsort as IMGsort


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

    # TODO add all the other parameters!
    # Clean parser
    clean_parser = subs.add_parser('CleanFile')

    clean_parser_panel_1 = clean_parser.add_argument_group('Clean File',
                                                           'Provide a path to LAS file to clean.')

    clean_parser_panel_1.add_argument('--pcd_file', type=str, required=True,
                                      metavar='Point Cloud (LAS)',
                                      help='Path to point cloud LAS file.',
                                      widget='FileChooser')

    clean_parser_panel_1.add_argument('--output_dir', type=str,
                                      metavar="Output Directory",
                                      default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                      help='Directory to save the processed files.',
                                      widget='DirChooser')

    clean_parser_panel_2 = clean_parser.add_argument_group('Optional Arguments for Cleaning',
                                                           'Provide a path to LAS file to clean.')

    clean_parser_panel_2.add_argument('--intensity_thresh', type=float, required=False,
                                      default=100,
                                      metavar='Intensity Threshold',
                                      help='All intensity values below this number will be filtered out.')

    clean_parser_panel_3 = clean_parser.add_argument_group('Optional Arguments for Removing Bad Files',
                                                           'Provide a path to LAS file to clean.')

    clean_parser_panel_3.add_argument('--density_thresh', type=float, required=False,
                                      default=7000,
                                      metavar='Density Threshold',
                                      help='All point clouds with fewer than this number of points per meter squared will be removed')

    clean_parser_panel_3.add_argument('--min_point_thresh', type=float, required=False,
                                      default=100000,
                                      metavar='Total Points Threshold',
                                      help='All point clouds with fewer than this number of points will be removed')

    clean_parser_panel_4 = clean_parser.add_argument_group(
        'Optional Arguments for the Statistical Outliers Removal (SOR) filter',
        'Arguments for the Statistical Outliers Removal (SOR) filter.')

    clean_parser_panel_4.add_argument('--knn', type=int, required=False,
                                      default=6,
                                      metavar='K Nearest Neighbors',
                                      help='number of neighbors (must be an int)')
    clean_parser_panel_4.add_argument('--nSigma', type=float, required=False,
                                      default=10,
                                      metavar='Total Points Threshold',
                                      help='number of sigmas under which the points should be kept')

    clean_parser_panel_5 = clean_parser.add_argument_group('Optional Arguments for Removing Bad Files',
                                                           'Other Arguments.')

    clean_parser_panel_5.add_argument('--verbose', default=True,
                                      help='Should Information be Printed to the Console.',
                                      metavar="Verbose",
                                      action='store_true',
                                      widget='BlockCheckbox')

    clean_parser_panel_5.add_argument('--export', default=True,
                                      help='Should the cleaned point clouds be saved to their own folder.',
                                      metavar="Intermediate Export Option",
                                      action='store_true', widget='BlockCheckbox')

    # Clean parser
    clean_dir_parser = subs.add_parser('CleanFiles')

    clean_dir_parser_panel_1 = clean_dir_parser.add_argument_group('Clean Files',
                                                                   'Provide a path to directory of LAS files to clean.')

    clean_dir_parser_panel_1.add_argument('--pcd_dir', type=str, required=True,
                                          metavar='Directory of Point Clouds (LAS)',
                                          help='Path to directory of LAS files.',
                                          widget='DirChooser')

    clean_dir_parser_panel_1.add_argument('--output_dir', type=str,
                                          metavar="Output Directory",
                                          default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                          help='Directory to save the processed files.',
                                          widget='DirChooser')

    clean_dir_parser_panel_2 = clean_dir_parser.add_argument_group('Optional Arguments for Cleaning',
                                                                   'Provide a path to LAS file to clean.')

    clean_dir_parser_panel_2.add_argument('--intensity_thresh', type=float, required=False,
                                          default=100,
                                          metavar='Intensity Threshold',
                                          help='All intensity values below this number will be filtered out.')

    clean_dir_parser_panel_3 = clean_dir_parser.add_argument_group('Optional Arguments for Removing Bad Files',
                                                                   'Provide a path to LAS file to clean.')

    clean_dir_parser_panel_3.add_argument('--density_thresh', type=float, required=False,
                                          default=7000,
                                          metavar='Density Threshold',
                                          help='All point clouds with fewer than this number of points per meter squared will be removed')

    clean_dir_parser_panel_3.add_argument('--min_point_thresh', type=float, required=False,
                                          default=100000,
                                          metavar='Total Points Threshold',
                                          help='All point clouds with fewer than this number of points will be removed')

    clean_dir_parser_panel_4 = clean_dir_parser.add_argument_group(
        'Optional Arguments for the Statistical Outliers Removal (SOR) filter',
        'Arguments for the Statistical Outliers Removal (SOR) filter.')

    clean_dir_parser_panel_4.add_argument('--knn', type=int, required=False,
                                          default=6,
                                          metavar='K Nearest Neighbors',
                                          help='number of neighbors (must be an int)')
    clean_dir_parser_panel_4.add_argument('--nSigma', type=float, required=False,
                                          default=10,
                                          metavar='Total Points Threshold',
                                          help='number of sigmas under which the points should be kept')

    clean_dir_parser_panel_5 = clean_dir_parser.add_argument_group('Optional Arguments for Removing Bad Files',
                                                                   'Other Arguments.')

    clean_dir_parser_panel_5.add_argument('--verbose', default=True,
                                          help='Should Information be Printed to the Console.',
                                          metavar="Verbose",
                                          action='store_true',
                                          widget='BlockCheckbox')

    clean_dir_parser_panel_5.add_argument('--export', default=True,
                                          help='Should the cleaned point clouds be saved to their own folder.',
                                          metavar="Intermediate Export Option",
                                          action='store_true', widget='BlockCheckbox')

    # Segment parser
    segment_parser = subs.add_parser('Segment')

    segment_parser_panel_1 = segment_parser.add_argument_group('Segment',
                                                               'Provide a path to LAS file to segment.')

    segment_parser_panel_1.add_argument('--pcd_file', type=str, required=True,
                                        metavar='Point Cloud (LAS)',
                                        help='Path to point cloud LAS file.',
                                        widget='FileChooser')

    segment_parser_panel_1.add_argument('--output_dir', type=str,
                                        metavar="Output Directory",
                                        default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                        help='Directory to save the processed files.')

    segment_parser_panel_2 = segment_parser.add_argument_group('Optional Arguments for Segmenting Corals',
                                                                   'Provide a path to LAS file to clean.')


    segment_parser_panel_2.add_argument('--pcd_above_seafloor_thresh', type=float, required=False,
                                          default=0.08,
                                          metavar='Meters Above Sea Floor Threshold',
                                          help='Points above this Value will be added to the Potential Coral Cloud that is used later to identify corals.')

    segment_parser_panel_2.add_argument('--intensity_threshold', type=float, required=False,
                                          default=320,
                                          metavar='Intensity Threshold',
                                          help='Points below this intensity value will be added to the Potential Coral Cloud that is used later to identify corals.')

    segment_parser_panel_2.add_argument('--coral_cell_size', type=float, required=False,
                                          default=0.02,
                                          metavar='Coral Cell Size',
                                          help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Corals.')
    segment_parser_panel_2.add_argument('--coral_min_comp_size', type=int, required=False,
                                          default= 10 ,
                                          metavar='Minimum Coral Size',
                                          help='The smallest number of grouped points that will be classified as coral.')

    segment_parser_panel_2.add_argument('--max_coral_pts', type=float, required=False,
                                          default=5000,
                                          metavar='Maximum Coral Size',
                                          help='The largest number of grouped points that will be classified as coral.')

    segment_parser_panel_3 = segment_parser.add_argument_group('Optional Arguments for Segmenting Fish',
                                                                   'Provide a path to LAS file to clean.')
    segment_parser_panel_3.add_argument('--fish_cell_size', type=float, required=False,
                                          default=0.02,
                                          metavar='Fish Cell Size',
                                          help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Fish.')
    segment_parser_panel_3.add_argument('--fish_min_comp_size', type=int, required=False,
                                          default= 10 ,
                                          metavar='Minimum Fish Size',
                                          help='The smallest number of grouped points that will be classified as fish.')

    segment_parser_panel_4 = segment_parser.add_argument_group('Optional Arguments for Creating DEM',
                                                               'Provide a path to LAS file to clean.')

    segment_parser_panel_4.add_argument('--dem_grid_step', type=float, required=False,
                                          default=.07,
                                          metavar='Grid Step for DEM',
                                          help='The Grid step used to create the DEM.')

    #not working rn cant figure out how to add the choice to the end of the variable name
    segment_parser_panel_4.add_argument('--empty_cell_fill_option', type=str, required=False,
                                          default="KRIGING",
                                          metavar='Empty cell fill Ooption for DEM',
                                          help='How should the values for empty spaces be filled. OPTIONS: "LEAVE_EMPTY", "FILL_MINIMUM_HEIGHT","FILL_MAXIMUM_HEIGHT","FILL_CUSTOM_HEIGHT","FILL_AVERAGE_HEIGHT","INTERPOLATE_DELAUNAY","KRIGING"')

    segment_parser_panel_5 = segment_parser.add_argument_group('Other Optional Arguments',
                                                               'Provide a path to LAS file to clean.')

    segment_parser_panel_5.add_argument('--exportOption', type=str, required=False,
                                        default="small_output",
                                        metavar='Export Option',
                                        help='What should be outputed? Options are "small_output", "large_output", "all" ')
    segment_parser_panel_5.add_argument('--verbose', default=True,
                                          help='Should Information be Printed to the Console.',
                                          metavar="Verbose",
                                          action='store_true',
                                          widget='BlockCheckbox')

    # segment many parser
    segment_dir_parser = subs.add_parser('SegmentFiles')

    segment_dir_parser_panel_1 = segment_dir_parser.add_argument_group('Segment Files',
                                                                       'Provide a path to directory of CLEANED LAS files to Segment.')

    segment_dir_parser_panel_1.add_argument('--pcd_dir', type=str, required=True,
                                            metavar='Directory of Point Clouds (LAS)',
                                            help='Path to directory of LAS files.',
                                            widget='DirChooser')

    segment_dir_parser_panel_1.add_argument('--output_dir', type=str,
                                            metavar="Output Directory",
                                            default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                            help='Directory to save the processed files.',
                                            widget='DirChooser')

    # Clean Segment parser
    cleansegment_parser = subs.add_parser('CleanSegment')

    cleansegment_parser_panel_1 = cleansegment_parser.add_argument_group('CleanSegment',
                                                                         'Provide a path to LAS file to segment.')

    cleansegment_parser_panel_1.add_argument('--pcd_file', type=str, required=True,
                                             metavar='Point Cloud (LAS)',
                                             help='Path to point cloud LAS file.',
                                             widget='FileChooser')

    cleansegment_parser_panel_1.add_argument('--output_dir', type=str,
                                             metavar="Output Directory",
                                             default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                             help='Directory to save the processed files.')

    # Many Clean Segment parser
    manycleansegment_dir_parser = subs.add_parser('manyCleanSegment')

    manycleansegment_dir_parser_panel_1 = manycleansegment_dir_parser.add_argument_group('manyCleanSegment',
                                                                                         'Provide a path to LAS file to segment.')
    manycleansegment_dir_parser_panel_1.add_argument('--pcd_dir', type=str, required=True,
                                                     metavar='Directory of Point Clouds (LAS)',
                                                     help='Path to directory of LAS files.',
                                                     widget='DirChooser')

    manycleansegment_dir_parser_panel_1.add_argument('--output_dir', type=str,
                                                     metavar="Output Directory",
                                                     default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                                     help='Directory to save the processed files.',
                                                     widget='DirChooser')

    # Image Sort
    image_sort_parser = subs.add_parser('Sort')
    image_sort_parser_panel_1 = image_sort_parser.add_argument_group('Just Sorting')
    image_sort_parser_panel_1.add_argument('--pcd_dir', type=str,
                                           default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                                           help='Directory containing the LAS files.', widget='DirChooser')
    image_sort_parser_panel_1.add_argument('--output_dir', type=str,
                                           default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                                           help='Directory to save the processed files.', widget='DirChooser')
    image_sort_parser_panel_1.add_argument('--img_dir', type=str,
                                           default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                                           help='Directory to save the processed files.',
                                           metavar="Image Path", widget='DirChooser')

    # Clean Segment + Image Sort

    cleansegmentsort_dir_parser = subs.add_parser('Everything')
    cleansegmentsort_dir_parser_panel_1 = cleansegmentsort_dir_parser.add_argument_group(
        'Cleaning + Segmenting + Sorting')
    # group4.add_argument('path', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
    #                     help='Directory containing the LAS files.')

    cleansegmentsort_dir_parser_panel_1.add_argument('--pcd_dir', type=str,
                                                     default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\data',
                                                     help='Directory containing the LAS files.', widget='DirChooser',
                                                     metavar="las directory Path")

    cleansegmentsort_dir_parser_panel_1.add_argument('--img_dir', type=str,
                                                     default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                                                     help='Directory to save the processed files.',
                                                     metavar="Image Path", widget='DirChooser')

    cleansegmentsort_dir_parser_panel_1.add_argument('--output_dir', type=str,
                                                     default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                                                     help='Directory to save the processed files.', widget='DirChooser')
    cleansegmentsort_dir_parser_panel_1.add_argument('--export', default=False,
                                                     help='Should the cleaned point clouds be saved to their own folder.',
                                                     metavar="Intermediate Export Option",
                                                     action='store_true', widget='BlockCheckbox')

    args = parser.parse_args()

    try:
        if args.command == 'CleanFile':
            # Create a cleanCloud instance
            cloud_cleaner = cleanCloud(pcd_file=args.pcd_file,
                                       output_dir=args.output_dir,
                                       intensity_thresh=args.intensity_thresh,
                                       density_thresh=args.density_thresh,
                                       min_point_thresh=args.min_point_thresh,
                                       knn=args.knn,
                                       nSigma=args.nSigma,
                                       verbose=args.verbose,
                                       export=args.export)

            # cloud_cleaner = cleanCloud(pcd_file=args.pcd_file,
            #                            output_dir=args.output_dir)

            # Load the cloud from file
            cloud_cleaner.load_pcd()

            # Clean the cloud
            cloud_cleaner.clean()

        # TODO add all parameterized arguments here
        elif args.command == 'Segment':
            # Create a segmentCloud instance
            # cloud_segmentor = segmentCloud(pcd_file=args.pcd_file,
            #                                output_dir=args.output_dir,
            #                                verbose=args.verbose)

            cloud_segmentor = segmentCloud(pcd_file=args.pcd_file,
                                           output_dir=args.output_dir,
                                           dem_grid_step=args.dem_grid_step,
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

        elif args.command == 'CleanFiles':
            # Create a cleanCloud instance
            cloud_cleaner = cleanClouds(pcd_dir=args.pcd_dir,
                                        output_dir=args.output_dir,
                                        intensity_thresh=args.intensity_thresh,
                                        density_thresh=args.density_thresh,
                                        min_point_thresh=args.min_point_thresh,
                                        knn=args.knn,
                                        nSigma=args.nSigma,
                                        verbose=args.verbose,
                                        export=args.export)

            # cloud_cleaner = cleanClouds(pcd_dir=args.pcd_dir,
            #                            output_dir=args.output_dir)

            # Clean the clouds
            cloud_cleaner.cleanDir()

        elif args.command == 'SegmentFiles':
            # Create a cleanCloud instance
            # cloud_cleaner = cleanClouds(pcd_dir=args.pcd_dir,
            #                             output_dir=args.output_dir,
            #                             intensity_thresh=args.intensity_thresh,
            #                             perimeter_thresh=args.perimeter_thresh,
            #                             min_point_thresh=args.min_point_thresh,
            #                             verbose=args.verbose)

            cloud_segmentor = segmentClouds(pcd_dir=args.pcd_dir,
                                            output_dir=args.output_dir)

            # Clean the clouds
            cloud_segmentor.cleanDir()

        elif args.command == 'CleanSegment':
            # Create a cleanCloud instance
            # cloud_cleaner = cleanCloud(pcd_file=args.pcd_file,
            #                            output_dir=args.output_dir,
            #                            intensity_thresh=args.intensity_thresh,
            #                            perimeter_thresh=args.perimeter_thresh,
            #                            min_point_thresh=args.min_point_thresh,
            #                            verbose=args.verbose)

            cloud_cleaner = cleanCloud(pcd_file=args.pcd_file,
                                       output_dir=args.output_dir)

            # Load the cloud from file
            cloud_cleaner.load_pcd()

            # Clean the cloud
            cloud_cleaner.clean()

            cloud_segmentor = segmentCloud(pcd_file=str(args.pcd_file),
                                           output_dir=args.output_dir)

            # Load the cleaned cloud from file
            cloud_segmentor.load_pcd(pcd=cloud_cleaner)

            # Segment the cloud
            cloud_segmentor.segment()
        elif args.command == 'manyCleanSegment':
            # Create a cleanCloud instance
            # cloud_cleaner = cleanCloud(pcd_file=args.pcd_file,
            #                            output_dir=args.output_dir,
            #                            intensity_thresh=args.intensity_thresh,
            #                            perimeter_thresh=args.perimeter_thresh,
            #                            min_point_thresh=args.min_point_thresh,
            #                            verbose=args.verbose)
            pcd_files = glob.glob(f"{args.pcd_dir}/**/*.las", recursive=True)

            for pcd_file in pcd_files:
                cloud_cleaner = cleanCloud(pcd_file=pcd_file,
                                           output_dir=args.output_dir)

                # Load the cloud from file
                cloud_cleaner.load_pcd()

                # Clean the cloud
                cloud_cleaner.clean()

                if None in [cloud_cleaner.originalPointCloud, cloud_cleaner.cleanedPointCloud]:
                    print("Error: PCD file is empty")
                else:
                    cloud_segmentor = segmentCloud(pcd_file=str(pcd_file),
                                                   output_dir=args.output_dir)

                    # Load the cleaned cloud from file
                    cloud_segmentor.load_pcd(pcd=cloud_cleaner)

                    # Segment the cloud
                    cloud_segmentor.segment()
        elif args.command == 'Sort':
            tracks = lasProcess(input_dir=args.pcd_dir, output_dir=args.output_dir)
            tracks.run()

            images = imgProcess(input_dir=args.img_dir, output_dir=args.output_dir)
            images.run()

            imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
            imgSort.run()
        elif args.command == 'Everything':
            pcd_files = glob.glob(f"{args.pcd_dir}/**/*.las", recursive=True)

            for pcd_file in pcd_files:
                cloud_cleaner = cleanCloud(pcd_file=pcd_file,
                                           output_dir=args.output_dir)

                # Load the cloud from file
                cloud_cleaner.load_pcd()

                # Clean the cloud
                cloud_cleaner.clean()

                if None in [cloud_cleaner.originalPointCloud, cloud_cleaner.cleanedPointCloud]:
                    print("Error: PCD file is empty")
                else:
                    cloud_segmentor = segmentCloud(pcd_file=str(pcd_file),
                                                   output_dir=args.output_dir)

                    # Load the cleaned cloud from file
                    cloud_segmentor.load_pcd(pcd=cloud_cleaner)

                    # Segment the cloud
                    cloud_segmentor.segment()

            tracks = lasProcess(input_dir=args.pcd_dir, output_dir=args.output_dir)
            tracks.run()

            images = imgProcess(input_dir=args.img_dir, output_dir=args.output_dir)
            images.run()

            imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
            imgSort.run()

        print("Done.")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == "__main__":
    main()
