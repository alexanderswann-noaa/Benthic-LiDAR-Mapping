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
    clean_parser = subs.add_parser('clean')
    group1 = clean_parser.add_argument_group('Just Clean')
    group1.add_argument('path', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                        help='Directory containing the LAS files.')
    group1.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.')
    group1.add_argument('--file', type=str,
                        default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\data\processed_LLS_2024-03-15T054218.010100_1_3.las',
                        help='Directory to save the processed files.')

    process_parser2 = subs.add_parser('processing')
    group2 = process_parser2.add_argument_group('processing')
    group2.add_argument('path', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                        help='Directory containing the LAS files.')
    group2.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.')
    group2.add_argument('--file', type=str,
                        default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\data\processed_LLS_2024-03-15T054218.010100_1_3.las',
                        help='Directory to save the processed files.')



    process_parser3 = subs.add_parser('sorting')
    group3 = process_parser3.add_argument_group('Just Sorting')
    group3.add_argument('path', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                        help='Directory containing the LAS files.')
    group3.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.')
    group3.add_argument('--img_path', type=str,
                        default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                        help='Directory to save the processed files.',
                        metavar="Image Path")

    process_parser4 = subs.add_parser('All')
    group4 = process_parser4.add_argument_group('mine')
    group4.add_argument('path', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                        help='Directory containing the LAS files.')
    group4.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.')
    group4.add_argument('--img_path', type=str,
                        default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                        help='Directory to save the processed files.',
                        metavar="Image Path")

    args = parser.parse_args()

    if args.command == 'clean':
        cleanCld = cleanCloud.fromArgs(args=args)
        cleanCld.run()

    if args.command == 'processing':
        cleanCld = cleanCloud.fromArgs(args=args)
        cleanCld.run()

        segmentedCloud = seg.fromPrev(prev=cleanCld, args=args)
        segmentedCloud.run()

    if args.command == 'sorting':
        tracks = lasProcess.fromArgs(args=args)
        tracks.run()

        images = imgProcess.fromArgs(args=args)
        images.run()

        imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
        imgSort.run()

    if args.command == 'All':
        print("HELLOOO")
        tracks_df = args.path
        images_df = args.img_path
        output_directory = args.output_dir

        isdir = os.path.isdir(tracks_df)
        print(os.path.isdir(tracks_df))


if __name__ == "__main__":
    main()
