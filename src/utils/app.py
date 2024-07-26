# -----------------------------------------------------------------------------------------------------------
# Import Statements
# -----------------------------------------------------------------------------------------------------------
import os
from gooey import Gooey, GooeyParser

from cleanCloud import cleanCloud as cleanCloud

from segmentation import segmentation as seg

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
    desc = 'Process and classify point clouds.'
    parser = GooeyParser(description=desc)

    # parser.add_argument('--verbose', help='be verbose', dest='verbose',
    #                     action='store_true', default=False)

    # figure out what above line does

    subs = parser.add_subparsers(help='commands', dest='command')

    # ____
    clean_parser = subs.add_parser('Clean')
    group1 = clean_parser.add_argument_group('Just Cleaning')
    group1.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.' , widget='DirChooser')
    group1.add_argument('--file', type=str,
                        default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\data',
                        help='Directory containing the LAS files.' , widget='FileChooser',
                        metavar="las directory Path")

    process_parser2 = subs.add_parser('Segment')
    group2 = process_parser2.add_argument_group('Clean + Segment out Fish and Corals')

    group2.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.', widget='DirChooser')
    group2.add_argument('--file', type=str,
                        default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput\lasFiles\SMALLprocessed_LLS_2024-03-15T054218.010100_1_4.las",
                        help='ONE LAS file.' , widget='FileChooser',
                        metavar="las directory Path")



    process_parser3 = subs.add_parser('Sort')
    group3 = process_parser3.add_argument_group('Just Sorting')
    group3.add_argument('path', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                        help='Directory containing the LAS files.', widget='DirChooser')
    group3.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.', widget='DirChooser')
    group3.add_argument('--img_path', type=str,
                        default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                        help='Directory to save the processed files.',
                        metavar="Image Path", widget='DirChooser')

    process_parser4 = subs.add_parser('(not working)Everything')
    group4 = process_parser4.add_argument_group('(not working)Cleaning + Segmenting + Sorting')
    # group4.add_argument('path', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
    #                     help='Directory containing the LAS files.')

    group4.add_argument('--file', type=str,
                        default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\data',
                        help='Directory containing the LAS files.' , widget='DirChooser',
                        metavar="las directory Path")


    group4.add_argument('--img_path', type=str,
                        default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                        help='Directory to save the processed files.',
                        metavar="Image Path", widget='DirChooser')

    group4.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.', widget='DirChooser')

    args = parser.parse_args()

    if args.command == 'Clean':
        cleanCld = cleanCloud.fromArgs(args=args)
        cleanCld.run()

    if args.command == 'Segment':
        cleanCld = cleanCloud.fromArgs(args=args)
        cleanCld.run()

        segmentedCloud = seg.fromPrev(prev=cleanCld, args=args)
        segmentedCloud.run()

    if args.command == 'Sort':
        tracks = lasProcess.fromArgs(args=args)
        tracks.run()

        images = imgProcess.fromArgs(args=args)
        images.run()

        imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
        imgSort.run()

    if args.command == 'Everything':
        cleanCld = cleanCloud.fromArgs(args=args)
        cleanCld.run()

        segmentedCloud = seg.fromPrev(prev=cleanCld, args=args)
        segmentedCloud.run()

        tracks = lasProcess.fromArgs(args=args)
        tracks.run()

        images = imgProcess.fromArgs(args=args)
        images.run()

        imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
        imgSort.run()


if __name__ == "__main__":
    main()
