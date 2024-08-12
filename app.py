import os
import traceback
import glob

from gooey import Gooey, GooeyParser

from src.cleanCloud import cleanCloud
from src.cleanClouds import cleanClouds
from src.segmentCloud import segmentCloud
from src.segmentClouds import segmentClouds

from src.lasTimeTagging import processLASdir as lasProcess

from src.imageTimeTagging import processIMGdir as imgProcess

from src.imageTimeSort import IMGsort as IMGsort

from src.lasRender import lasRender as lasRender
from src.lasRenderMany import lasRenderMany as lasRenderMany

from src.imageLocation import imageLocation as imageLocation

from src.SfM import sfm


# ----------------------------------------------------------------------------------------------------------------------
# Gooey GUI
# ----------------------------------------------------------------------------------------------------------------------

@Gooey(program_name="Benthic LiDAR Mapping Toolbox",
       default_size=(1200, 900))
def main():
    """
    Main function to parse arguments and initiate processing.
    """
    parser = GooeyParser(description='Process and classify point clouds.')
    subs = parser.add_subparsers(help='commands', dest='command')


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
                                                           'More Options For Cleaning.')

    clean_parser_panel_2.add_argument('--intensity_thresh', type=float, required=False,
                                      default=100,
                                      metavar='Intensity Threshold',
                                      help='All intensity values below this number will be filtered out.')

    clean_parser_panel_3 = clean_parser.add_argument_group('Optional Arguments for Removing Bad Files',
                                                           'More Options Removing Bad Files.')

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
                                                           'More Options Removing Bad Files.')

    clean_parser_panel_5.add_argument('--verbose', default=True,
                                      help='Should Information be Printed to the Console.',
                                      metavar="Verbose",
                                      action='store_true',
                                      widget='BlockCheckbox')

    clean_parser_panel_5.add_argument('--export', default=True,
                                      help='Should the cleaned point clouds be saved to their own folder.',
                                      metavar="Intermediate Export Option",
                                      action='store_true', widget='BlockCheckbox')

    # Clean dir parser
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
                                                                   'More Options For Cleaning.')

    clean_dir_parser_panel_2.add_argument('--intensity_thresh', type=float, required=False,
                                          default=100,
                                          metavar='Intensity Threshold',
                                          help='All intensity values below this number will be filtered out.')

    clean_dir_parser_panel_3 = clean_dir_parser.add_argument_group('Optional Arguments for Removing Bad Files',
                                                                   'More Options Removing Bad Files.')

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
                                                                   'More Options Removing Bad Files.')

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
                                                               'More Options For Coral Segmentation.')

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
                                        default=10,
                                        metavar='Minimum Coral Size',
                                        help='The smallest number of grouped points that will be classified as coral.')

    segment_parser_panel_2.add_argument('--max_coral_pts', type=float, required=False,
                                        default=5000,
                                        metavar='Maximum Coral Size',
                                        help='The largest number of grouped points that will be classified as coral.')

    segment_parser_panel_3 = segment_parser.add_argument_group('Optional Arguments for Segmenting Fish',
                                                               'More Options For Fish Segmentation.')
    segment_parser_panel_3.add_argument('--fish_cell_size', type=float, required=False,
                                        default=0.06,
                                        metavar='Fish Cell Size',
                                        help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Fish.')
    segment_parser_panel_3.add_argument('--fish_min_comp_size', type=int, required=False,
                                        default=10,
                                        metavar='Minimum Fish Size',
                                        help='The smallest number of grouped points that will be classified as fish.')

    segment_parser_panel_4 = segment_parser.add_argument_group('Optional Arguments for Creating DEM',
                                                               'Provide a path to LAS file to clean.')

    segment_parser_panel_4.add_argument('--dem_grid_step', type=float, required=False,
                                        default=.07,
                                        metavar='Grid Step for DEM',
                                        help='The Grid step used to create the DEM.')

    segment_parser_panel_4.add_argument('--empty_cell_fill_option', type=str, required=False,
                                        default="KRIGING",
                                        metavar='Empty cell fill Option for DEM',
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

    segment_dir_parser_panel_2 = segment_dir_parser.add_argument_group('Optional Arguments for Segmenting Corals',
                                                                       'More Options For Coral Segmentation.')

    segment_dir_parser_panel_2.add_argument('--pcd_above_seafloor_thresh', type=float, required=False,
                                            default=0.08,
                                            metavar='Meters Above Sea Floor Threshold',
                                            help='Points above this Value will be added to the Potential Coral Cloud that is used later to identify corals.')

    segment_dir_parser_panel_2.add_argument('--intensity_threshold', type=float, required=False,
                                            default=320,
                                            metavar='Intensity Threshold',
                                            help='Points below this intensity value will be added to the Potential Coral Cloud that is used later to identify corals.')

    segment_dir_parser_panel_2.add_argument('--coral_cell_size', type=float, required=False,
                                            default=0.02,
                                            metavar='Coral Cell Size',
                                            help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Corals.')
    segment_dir_parser_panel_2.add_argument('--coral_min_comp_size', type=int, required=False,
                                            default=10,
                                            metavar='Minimum Coral Size',
                                            help='The smallest number of grouped points that will be classified as coral.')

    segment_dir_parser_panel_2.add_argument('--max_coral_pts', type=float, required=False,
                                            default=5000,
                                            metavar='Maximum Coral Size',
                                            help='The largest number of grouped points that will be classified as coral.')

    segment_dir_parser_panel_3 = segment_dir_parser.add_argument_group('Optional Arguments for Segmenting Fish',
                                                                       'More Options For Fish Segmentation.')
    segment_dir_parser_panel_3.add_argument('--fish_cell_size', type=float, required=False,
                                            default=0.06,
                                            metavar='Fish Cell Size',
                                            help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Fish.')
    segment_dir_parser_panel_3.add_argument('--fish_min_comp_size', type=int, required=False,
                                            default=10,
                                            metavar='Minimum Fish Size',
                                            help='The smallest number of grouped points that will be classified as fish.')

    segment_dir_parser_panel_4 = segment_dir_parser.add_argument_group('Optional Arguments for Creating DEM',
                                                                       'Provide a path to LAS file to clean.')

    segment_dir_parser_panel_4.add_argument('--dem_grid_step', type=float, required=False,
                                            default=.07,
                                            metavar='Grid Step for DEM',
                                            help='The Grid step used to create the DEM.')

    # not working rn cant figure out how to add the choice to the end of the variable name
    segment_dir_parser_panel_4.add_argument('--empty_cell_fill_option', type=str, required=False,
                                            default="KRIGING",
                                            metavar='Empty cell fill Ooption for DEM',
                                            help='How should the values for empty spaces be filled. OPTIONS: "LEAVE_EMPTY", "FILL_MINIMUM_HEIGHT","FILL_MAXIMUM_HEIGHT","FILL_CUSTOM_HEIGHT","FILL_AVERAGE_HEIGHT","INTERPOLATE_DELAUNAY","KRIGING"')

    segment_dir_parser_panel_5 = segment_dir_parser.add_argument_group('Other Optional Arguments',
                                                                       'Provide a path to LAS file to clean.')

    segment_dir_parser_panel_5.add_argument('--exportOption', type=str, required=False,
                                            default="small_output",
                                            metavar='Export Option',
                                            help='What should be outputed? Options are "small_output", "large_output", "all" ')
    segment_dir_parser_panel_5.add_argument('--verbose', default=True,
                                            help='Should Information be Printed to the Console.',
                                            metavar="Verbose",
                                            action='store_true',
                                            widget='BlockCheckbox')

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

    cleansegment_parser_panel_2 = cleansegment_parser.add_argument_group('Optional Arguments for Cleaning',
                                                                         'More Options For Cleaning.')

    cleansegment_parser_panel_2.add_argument('--intensity_thresh', type=float, required=False,
                                             default=100,
                                             metavar='Intensity Threshold',
                                             help='All intensity values below this number will be filtered out.')

    cleansegment_parser_panel_3 = cleansegment_parser.add_argument_group('Optional Arguments for Removing Bad Files',
                                                                         'More Options Removing Bad Files.')

    cleansegment_parser_panel_3.add_argument('--density_thresh', type=float, required=False,
                                             default=7000,
                                             metavar='Density Threshold',
                                             help='All point clouds with fewer than this number of points per meter squared will be removed')

    cleansegment_parser_panel_3.add_argument('--min_point_thresh', type=float, required=False,
                                             default=100000,
                                             metavar='Total Points Threshold',
                                             help='All point clouds with fewer than this number of points will be removed')

    cleansegment_parser_panel_4 = cleansegment_parser.add_argument_group(
        'Optional Arguments for the Statistical Outliers Removal (SOR) filter',
        'Arguments for the Statistical Outliers Removal (SOR) filter.')

    cleansegment_parser_panel_4.add_argument('--knn', type=int, required=False,
                                             default=6,
                                             metavar='K Nearest Neighbors',
                                             help='number of neighbors (must be an int)')
    cleansegment_parser_panel_4.add_argument('--nSigma', type=float, required=False,
                                             default=10,
                                             metavar='Total Points Threshold',
                                             help='number of sigmas under which the points should be kept')

    cleansegment_parser_panel_5 = cleansegment_parser.add_argument_group('Optional Arguments for Segmenting Corals',
                                                                         'More Options For Coral Segmentation.')

    cleansegment_parser_panel_5.add_argument('--pcd_above_seafloor_thresh', type=float, required=False,
                                             default=0.08,
                                             metavar='Meters Above Sea Floor Threshold',
                                             help='Points above this Value will be added to the Potential Coral Cloud that is used later to identify corals.')

    cleansegment_parser_panel_5.add_argument('--intensity_threshold', type=float, required=False,
                                             default=320,
                                             metavar='Intensity Threshold',
                                             help='Points below this intensity value will be added to the Potential Coral Cloud that is used later to identify corals.')

    cleansegment_parser_panel_5.add_argument('--coral_cell_size', type=float, required=False,
                                             default=0.02,
                                             metavar='Coral Cell Size',
                                             help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Corals.')
    cleansegment_parser_panel_5.add_argument('--coral_min_comp_size', type=int, required=False,
                                             default=10,
                                             metavar='Minimum Coral Size',
                                             help='The smallest number of grouped points that will be classified as coral.')

    cleansegment_parser_panel_5.add_argument('--max_coral_pts', type=float, required=False,
                                             default=5000,
                                             metavar='Maximum Coral Size',
                                             help='The largest number of grouped points that will be classified as coral.')

    cleansegment_parser_panel_6 = cleansegment_parser.add_argument_group('Optional Arguments for Segmenting Fish',
                                                                         'More Options For Fish Segmentation.')
    cleansegment_parser_panel_6.add_argument('--fish_cell_size', type=float, required=False,
                                             default=0.06,
                                             metavar='Fish Cell Size',
                                             help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Fish.')
    cleansegment_parser_panel_6.add_argument('--fish_min_comp_size', type=int, required=False,
                                             default=10,
                                             metavar='Minimum Fish Size',
                                             help='The smallest number of grouped points that will be classified as fish.')

    cleansegment_parser_panel_7 = cleansegment_parser.add_argument_group('Optional Arguments for Creating DEM',
                                                                         'Provide a path to LAS file to clean.')

    cleansegment_parser_panel_7.add_argument('--dem_grid_step', type=float, required=False,
                                             default=.07,
                                             metavar='Grid Step for DEM',
                                             help='The Grid step used to create the DEM.')

    # not working rn cant figure out how to add the choice to the end of the variable name
    cleansegment_parser_panel_7.add_argument('--empty_cell_fill_option', type=str, required=False,
                                             default="KRIGING",
                                             metavar='Empty cell fill Ooption for DEM',
                                             help='How should the values for empty spaces be filled. OPTIONS: "LEAVE_EMPTY", "FILL_MINIMUM_HEIGHT","FILL_MAXIMUM_HEIGHT","FILL_CUSTOM_HEIGHT","FILL_AVERAGE_HEIGHT","INTERPOLATE_DELAUNAY","KRIGING"')

    cleansegment_parser_panel_8 = cleansegment_parser.add_argument_group('Other Optional Arguments',
                                                                         'Provide a path to LAS file to clean.')

    cleansegment_parser_panel_8.add_argument('--exportOption', type=str, required=False,
                                             default="small_output",
                                             metavar='Export Option',
                                             help='What should be outputed? Options are "small_output", "large_output", "all" ')

    cleansegment_parser_panel_8.add_argument('--export', default=False,
                                             help='Should the cleaned point clouds be saved to their own folder.',
                                             metavar="Intermediate Export Option",
                                             action='store_true', widget='BlockCheckbox')

    cleansegment_parser_panel_8.add_argument('--verbose', default=True,
                                             help='Should Information be Printed to the Console.',
                                             metavar="Verbose",
                                             action='store_true',
                                             widget='BlockCheckbox')

    # Many Clean Segment parser
    cleansegment_dir_parser = subs.add_parser('manyCleanSegment')

    cleansegment_dir_parser_panel_1 = cleansegment_dir_parser.add_argument_group('manyCleanSegment',
                                                                                 'Provide a path to LAS file to segment.')
    cleansegment_dir_parser_panel_1.add_argument('--pcd_dir', type=str, required=True,
                                                 metavar='Directory of Point Clouds (LAS)',
                                                 help='Path to directory of LAS files.',
                                                 widget='DirChooser')

    cleansegment_dir_parser_panel_1.add_argument('--output_dir', type=str,
                                                 metavar="Output Directory",
                                                 default=f"{os.path.dirname(os.path.abspath(__file__))}/data/processed",
                                                 help='Directory to save the processed files.',
                                                 widget='DirChooser')

    cleansegment_dir_parser_panel_2 = cleansegment_dir_parser.add_argument_group('Optional Arguments for Cleaning',
                                                                                 'More Options For Cleaning.')

    cleansegment_dir_parser_panel_2.add_argument('--intensity_thresh', type=float, required=False,
                                                 default=100,
                                                 metavar='Intensity Threshold',
                                                 help='All intensity values below this number will be filtered out.')

    cleansegment_dir_parser_panel_3 = cleansegment_dir_parser.add_argument_group(
        'Optional Arguments for Removing Bad Files',
        'More Options Removing Bad Files.')

    cleansegment_dir_parser_panel_3.add_argument('--density_thresh', type=float, required=False,
                                                 default=7000,
                                                 metavar='Density Threshold',
                                                 help='All point clouds with fewer than this number of points per meter squared will be removed')

    cleansegment_dir_parser_panel_3.add_argument('--min_point_thresh', type=float, required=False,
                                                 default=100000,
                                                 metavar='Total Points Threshold',
                                                 help='All point clouds with fewer than this number of points will be removed')

    cleansegment_dir_parser_panel_4 = cleansegment_dir_parser.add_argument_group(
        'Optional Arguments for the Statistical Outliers Removal (SOR) filter',
        'Arguments for the Statistical Outliers Removal (SOR) filter.')

    cleansegment_dir_parser_panel_4.add_argument('--knn', type=int, required=False,
                                                 default=6,
                                                 metavar='K Nearest Neighbors',
                                                 help='number of neighbors (must be an int)')
    cleansegment_dir_parser_panel_4.add_argument('--nSigma', type=float, required=False,
                                                 default=10,
                                                 metavar='Total Points Threshold',
                                                 help='number of sigmas under which the points should be kept')

    cleansegment_dir_parser_panel_5 = cleansegment_dir_parser.add_argument_group(
        'Optional Arguments for Segmenting Corals',
        'More Options For Coral Segmentation.')

    cleansegment_dir_parser_panel_5.add_argument('--pcd_above_seafloor_thresh', type=float, required=False,
                                                 default=0.08,
                                                 metavar='Meters Above Sea Floor Threshold',
                                                 help='Points above this Value will be added to the Potential Coral Cloud that is used later to identify corals.')

    cleansegment_dir_parser_panel_5.add_argument('--intensity_threshold', type=float, required=False,
                                                 default=320,
                                                 metavar='Intensity Threshold',
                                                 help='Points below this intensity value will be added to the Potential Coral Cloud that is used later to identify corals.')

    cleansegment_dir_parser_panel_5.add_argument('--coral_cell_size', type=float, required=False,
                                                 default=0.02,
                                                 metavar='Coral Cell Size',
                                                 help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Corals.')
    cleansegment_dir_parser_panel_5.add_argument('--coral_min_comp_size', type=int, required=False,
                                                 default=10,
                                                 metavar='Minimum Coral Size',
                                                 help='The smallest number of grouped points that will be classified as coral.')

    cleansegment_dir_parser_panel_5.add_argument('--max_coral_pts', type=float, required=False,
                                                 default=5000,
                                                 metavar='Maximum Coral Size',
                                                 help='The largest number of grouped points that will be classified as coral.')

    cleansegment_dir_parser_panel_6 = cleansegment_dir_parser.add_argument_group(
        'Optional Arguments for Segmenting Fish',
        'More Options For Fish Segmentation.')
    cleansegment_dir_parser_panel_6.add_argument('--fish_cell_size', type=float, required=False,
                                                 default=0.06,
                                                 metavar='Fish Cell Size',
                                                 help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Fish.')
    cleansegment_dir_parser_panel_6.add_argument('--fish_min_comp_size', type=int, required=False,
                                                 default=10,
                                                 metavar='Minimum Fish Size',
                                                 help='The smallest number of grouped points that will be classified as fish.')

    cleansegment_dir_parser_panel_7 = cleansegment_dir_parser.add_argument_group('Optional Arguments for Creating DEM',
                                                                                 'Provide a path to LAS file to clean.')

    cleansegment_dir_parser_panel_7.add_argument('--dem_grid_step', type=float, required=False,
                                                 default=.07,
                                                 metavar='Grid Step for DEM',
                                                 help='The Grid step used to create the DEM.')

    # not working rn cant figure out how to add the choice to the end of the variable name
    cleansegment_dir_parser_panel_7.add_argument('--empty_cell_fill_option', type=str, required=False,
                                                 default="KRIGING",
                                                 metavar='Empty cell fill Ooption for DEM',
                                                 help='How should the values for empty spaces be filled. OPTIONS: "LEAVE_EMPTY", "FILL_MINIMUM_HEIGHT","FILL_MAXIMUM_HEIGHT","FILL_CUSTOM_HEIGHT","FILL_AVERAGE_HEIGHT","INTERPOLATE_DELAUNAY","KRIGING"')

    cleansegment_dir_parser_panel_8 = cleansegment_dir_parser.add_argument_group('Other Optional Arguments',
                                                                                 'Provide a path to LAS file to clean.')

    cleansegment_dir_parser_panel_8.add_argument('--exportOption', type=str, required=False,
                                                 default="small_output",
                                                 metavar='Export Option',
                                                 help='What should be outputed? Options are "small_output", "large_output", "all" ')

    cleansegment_dir_parser_panel_8.add_argument('--export', default=False,
                                                 help='Should the cleaned point clouds be saved to their own folder.',
                                                 metavar="Intermediate Export Option",
                                                 action='store_true', widget='BlockCheckbox')

    cleansegment_dir_parser_panel_8.add_argument('--verbose', default=True,
                                                 help='Should Information be Printed to the Console.',
                                                 metavar="Verbose",
                                                 action='store_true',
                                                 widget='BlockCheckbox')

    # Image Sort
    image_sort_parser = subs.add_parser('Sort')
    image_sort_parser_panel_1 = image_sort_parser.add_argument_group('Just Sorting')
    image_sort_parser_panel_1.add_argument('--pcd_dir', type=str,
                                           default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                                           help='Directory containing the LAS files.', widget='DirChooser')

    image_sort_parser_panel_1.add_argument('--img_dir', type=str,
                                           default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                                           help='Directory to save the processed files.',
                                           metavar="Image Path", widget='DirChooser')

    image_sort_parser_panel_1.add_argument('--output_dir', type=str,
                                           default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                                           help='Directory to save the processed files.', widget='DirChooser')

    # Clean Segment + Image Sort

    cleansegmentsort_dir_parser = subs.add_parser('Everything')
    cleansegmentsort_dir_parser_panel_1 = cleansegmentsort_dir_parser.add_argument_group(
        'Cleaning + Segmenting + Sorting', "Provide the Path to the uncleaned LAS files, images, and output")
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

    cleansegmentsort_dir_parser_panel_2 = cleansegmentsort_dir_parser.add_argument_group(
        'Optional Arguments for Cleaning',
        'More Options For Cleaning.')

    cleansegmentsort_dir_parser_panel_2.add_argument('--intensity_thresh', type=float, required=False,
                                                     default=100,
                                                     metavar='Intensity Threshold',
                                                     help='All intensity values below this number will be filtered out.')

    cleansegmentsort_dir_parser_panel_3 = cleansegmentsort_dir_parser.add_argument_group(
        'Optional Arguments for Removing Bad Files',
        'More Options Removing Bad Files.')

    cleansegmentsort_dir_parser_panel_3.add_argument('--density_thresh', type=float, required=False,
                                                     default=7000,
                                                     metavar='Density Threshold',
                                                     help='All point clouds with fewer than this number of points per meter squared will be removed')

    cleansegmentsort_dir_parser_panel_3.add_argument('--min_point_thresh', type=float, required=False,
                                                     default=100000,
                                                     metavar='Total Points Threshold',
                                                     help='All point clouds with fewer than this number of points will be removed')

    cleansegmentsort_dir_parser_panel_4 = cleansegmentsort_dir_parser.add_argument_group(
        'Optional Arguments for the Statistical Outliers Removal (SOR) filter',
        'Arguments for the Statistical Outliers Removal (SOR) filter.')

    cleansegmentsort_dir_parser_panel_4.add_argument('--knn', type=int, required=False,
                                                     default=6,
                                                     metavar='K Nearest Neighbors',
                                                     help='number of neighbors (must be an int)')
    cleansegmentsort_dir_parser_panel_4.add_argument('--nSigma', type=float, required=False,
                                                     default=10,
                                                     metavar='Total Points Threshold',
                                                     help='number of sigmas under which the points should be kept')

    cleansegmentsort_dir_parser_panel_5 = cleansegmentsort_dir_parser.add_argument_group(
        'Optional Arguments for Segmenting Corals',
        'More Options For Coral Segmentation.')

    cleansegmentsort_dir_parser_panel_5.add_argument('--pcd_above_seafloor_thresh', type=float, required=False,
                                                     default=0.08,
                                                     metavar='Meters Above Sea Floor Threshold',
                                                     help='Points above this Value will be added to the Potential Coral Cloud that is used later to identify corals.')

    cleansegmentsort_dir_parser_panel_5.add_argument('--intensity_threshold', type=float, required=False,
                                                     default=320,
                                                     metavar='Intensity Threshold',
                                                     help='Points below this intensity value will be added to the Potential Coral Cloud that is used later to identify corals.')

    cleansegmentsort_dir_parser_panel_5.add_argument('--coral_cell_size', type=float, required=False,
                                                     default=0.02,
                                                     metavar='Coral Cell Size',
                                                     help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Corals.')
    cleansegmentsort_dir_parser_panel_5.add_argument('--coral_min_comp_size', type=int, required=False,
                                                     default=10,
                                                     metavar='Minimum Coral Size',
                                                     help='The smallest number of grouped points that will be classified as coral.')

    cleansegmentsort_dir_parser_panel_5.add_argument('--max_coral_pts', type=float, required=False,
                                                     default=5000,
                                                     metavar='Maximum Coral Size',
                                                     help='The largest number of grouped points that will be classified as coral.')

    cleansegmentsort_dir_parser_panel_6 = cleansegmentsort_dir_parser.add_argument_group(
        'Optional Arguments for Segmenting Fish',
        'More Options For Fish Segmentation.')
    cleansegmentsort_dir_parser_panel_6.add_argument('--fish_cell_size', type=float, required=False,
                                                     default=0.06,
                                                     metavar='Fish Cell Size',
                                                     help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Fish.')
    cleansegmentsort_dir_parser_panel_6.add_argument('--fish_min_comp_size', type=int, required=False,
                                                     default=10,
                                                     metavar='Minimum Fish Size',
                                                     help='The smallest number of grouped points that will be classified as fish.')

    cleansegmentsort_dir_parser_panel_7 = cleansegmentsort_dir_parser.add_argument_group(
        'Optional Arguments for Creating DEM',
        'Provide a path to LAS file to clean.')

    cleansegmentsort_dir_parser_panel_7.add_argument('--dem_grid_step', type=float, required=False,
                                                     default=.07,
                                                     metavar='Grid Step for DEM',
                                                     help='The Grid step used to create the DEM.')

    # not working rn cant figure out how to add the choice to the end of the variable name
    cleansegmentsort_dir_parser_panel_7.add_argument('--empty_cell_fill_option', type=str, required=False,
                                                     default="KRIGING",
                                                     metavar='Empty cell fill Option for DEM',
                                                     help='How should the values for empty spaces be filled. OPTIONS: "LEAVE_EMPTY", "FILL_MINIMUM_HEIGHT","FILL_MAXIMUM_HEIGHT","FILL_CUSTOM_HEIGHT","FILL_AVERAGE_HEIGHT","INTERPOLATE_DELAUNAY","KRIGING"')

    cleansegmentsort_dir_parser_panel_8 = cleansegmentsort_dir_parser.add_argument_group('Other Optional Arguments',
                                                                                         'Other Optional Arguments.')

    cleansegmentsort_dir_parser_panel_8.add_argument('--exportOption', type=str, required=False,
                                                     default="small_output",
                                                     metavar='Export Option',
                                                     help='What should be outputed? Options are "small_output", "large_output", "all" ')

    cleansegmentsort_dir_parser_panel_8.add_argument('--export', default=False,
                                                     help='Should the cleaned point clouds be saved to their own folder.',
                                                     metavar="Intermediate Export Option",
                                                     action='store_true', widget='BlockCheckbox')

    cleansegmentsort_dir_parser_panel_8.add_argument('--verbose', default=True,
                                                     help='Should Information be Printed to the Console.',
                                                     metavar="Verbose",
                                                     action='store_true',
                                                     widget='BlockCheckbox')


    # Las Image Render
    las_render_parser = subs.add_parser('FileRender')
    las_render_parser_panel_1 = las_render_parser.add_argument_group('Image Render')
    las_render_parser_panel_1.add_argument('--bin_file', type=str,
                                           default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput\segmented\binFiles\SMALL_processed_LLS_2024-03-15T054218010100_1_4.bin",
                                           help='Location of the BIN file.', widget='FileChooser')
    las_render_parser_panel_1.add_argument('--img_dir', type=str,
                                           default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput\Sorted Images\processed_LLS_2024-03-15T054218.010100_1_4.las",
                                           help='Directory containing the folders that contain the images.',
                                           metavar="Image Path", widget='DirChooser')
    las_render_parser_panel_1.add_argument('--output_dir', type=str,
                                           default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput6',
                                           help='Directory to save the rendered images.', widget='DirChooser')

    # Las Image Render Many
    las_render_many_parser = subs.add_parser('(Under Development)FilesRender')
    las_render_many_parser_panel_1 = las_render_many_parser.add_argument_group('(Under Development)Image Render for multiple Bin files')
    las_render_many_parser_panel_1.add_argument('--bin_dir', type=str,
                                           default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput\segmented\binFiles",
                                           help='Location of the BIN file.', widget='DirChooser')
    las_render_many_parser_panel_1.add_argument('--main_img_dir', type=str,
                                           default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput\Sorted Images",
                                           help='Directory containing the folders that contain the images.',
                                           metavar="Image Path", widget='DirChooser')
    las_render_many_parser_panel_1.add_argument('--output_dir', type=str,
                                           default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput6',
                                           help='Directory to save the rendered images.', widget='DirChooser')

    # ------------------------------------------------------------------------------------------------------------------
    # SfM
    # ------------------------------------------------------------------------------------------------------------------
    sfm_parser = subs.add_parser('SfM')

    # Panel 1
    sfm_parser_panel_1 = sfm_parser.add_argument_group('Structure from Motion',
                                                       'Use Metashape (2.0.X) API to perform Structure from Motion on '
                                                       'images of a scene.',
                                                       gooey_options={'show_border': True})

    sfm_parser_panel_1.add_argument('--metashape_license', type=str,
                                    metavar="Metashape License (Pro)",
                                    default=os.getenv('METASHAPE_LICENSE'),
                                    help='The license for Professional version of Metashape',
                                    widget="PasswordField")

    sfm_parser_panel_1.add_argument('--remember_license', action="store_false",
                                    metavar="Remember License",
                                    help='Store License as an Environmental Variable',
                                    widget="BlockCheckbox")

    sfm_parser_panel_1.add_argument('--input_dir',
                                    metavar="Image Directory",
                                    help='Directory containing images of scene',
                                    widget="DirChooser")

    sfm_parser_panel_1.add_argument('--output_dir',
                                    metavar='Output Directory',
                                    help='Root directory where output will be saved',
                                    widget="DirChooser")

    sfm_parser_panel_1.add_argument('--quality', type=str, default="Medium",
                                    metavar="Quality",
                                    help='Quality of data products',
                                    widget="Dropdown", choices=['Lowest', 'Low', 'Medium', 'High', 'Highest'])

    sfm_parser_panel_1.add_argument('--target_percentage', type=int, default=75,
                                    metavar="Target Percentage",
                                    help='Percentage of points to target for each gradual selection method',
                                    widget='Slider', gooey_options={'min': 0, 'max': 99, 'increment': 1})

    # Panel 2
    sfm_parser_panel_2 = sfm_parser.add_argument_group('Existing Project',
                                                       'Provide an existing project directory to pick up where the '
                                                       'program left off instead of re-running from scratch.',
                                                       gooey_options={'show_border': True})

    sfm_parser_panel_2.add_argument('--project_file', type=str, required=False,
                                    metavar="Project File",
                                    help='Path to existing Metashape project file (.psx)',
                                    widget='FileChooser')


    args = parser.parse_args()

    if 'metashape_license' in vars(args):
        if not args.remember_license:
            os.environ['METASHAPE_LICENSE'] = args.metashape_license

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

        elif args.command == 'Segment':
            # Create a segmentCloud instance
            # cloud_segmentor = segmentCloud(pcd_file=args.pcd_file,
            #                                output_dir=args.output_dir,
            #                                verbose=args.verbose)

            cloud_segmentor = segmentCloud(pcd_file=args.pcd_file,
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

            cloud_segmentor = segmentClouds(pcd_dir=args.pcd_dir,
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

            # Clean the clouds
            cloud_segmentor.cleanDir()

        elif args.command == 'CleanSegment':
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

            # Load the cloud from file
            cloud_cleaner.load_pcd()

            # Clean the cloud
            cloud_cleaner.clean()

            cloud_segmentor = segmentCloud(pcd_file=args.pcd_file,
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
                                           output_dir=args.output_dir,
                                           intensity_thresh=args.intensity_thresh,
                                           density_thresh=args.density_thresh,
                                           min_point_thresh=args.min_point_thresh,
                                           knn=args.knn,
                                           nSigma=args.nSigma,
                                           verbose=args.verbose,
                                           export=args.export)

                # Load the cloud from file
                cloud_cleaner.load_pcd()

                # Clean the cloud
                cloud_cleaner.clean()

                if None in [cloud_cleaner.originalPointCloud, cloud_cleaner.cleanedPointCloud]:
                    print("Error: PCD file is empty")
                else:
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
                                           output_dir=args.output_dir,
                                           intensity_thresh=args.intensity_thresh,
                                           density_thresh=args.density_thresh,
                                           min_point_thresh=args.min_point_thresh,
                                           knn=args.knn,
                                           nSigma=args.nSigma,
                                           verbose=args.verbose,
                                           export=args.export)

                # Load the cloud from file
                cloud_cleaner.load_pcd()

                # Clean the cloud
                cloud_cleaner.clean()

                if None in [cloud_cleaner.originalPointCloud, cloud_cleaner.cleanedPointCloud]:
                    print("Error: PCD file is empty")
                else:
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
                    cloud_segmentor.load_pcd(pcd=cloud_cleaner)

                    # Segment the cloud
                    cloud_segmentor.segment()

            tracks = lasProcess(input_dir=args.pcd_dir, output_dir=args.output_dir)
            tracks.run()

            images = imgProcess(input_dir=args.img_dir, output_dir=args.output_dir)
            images.run()

            imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
            imgSort.run()
        elif args.command == "FileRender":

            images = imageLocation(input_dir= args.img_dir, output_dir = args.output_dir )
            images.run()

            tracks = lasRender(bin_file=args.bin_file, image_dir = args.img_dir, output_dir = args.output_dir, img_info = images.imagesDf)

            #tracks.load_pcd()

            tracks.run()
        elif args.command == "FilesRender":



            tracks = lasRenderMany(bin_dir=args.bin_dir, main_image_dir=args.main_img_dir, output_dir=args.output_dir)

            # tracks.load_pcd()

            tracks.run()
        elif args.command == 'SfM':
            sfm(args)



        print("Done.")


    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == "__main__":
    main()
