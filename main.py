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
                        help='Directory containing the LAS files.' , widget='DirChooser',
                        metavar="las directory Path")
    group1.add_argument('--export', default=True,
                        help='Should the cleaned point clouds be saved to their own folder.',
                        metavar="Export Option",
                        action='store_true', widget='BlockCheckbox')

    process_parser2 = subs.add_parser('Segment')
    group2 = process_parser2.add_argument_group('Just Segment out Fish and Corals')

    group2.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.', widget='DirChooser')
    group2.add_argument('--file', type=str,
                        default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput\lasFiles\SMALLprocessed_LLS_2024-03-15T054218.010100_1_4.las",
                        help='ONE LAS file.' , widget='DirChooser',
                        metavar="las directory Path")

    process_parser5 = subs.add_parser('CleanANDsegment')
    group5 = process_parser5.add_argument_group('Clean + Segment out Fish and Corals')

    group5.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.', widget='DirChooser')
    group5.add_argument('--file', type=str,
                        default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data\processed_LLS_2024-03-15T054218.010100_1_4.las",
                        help='ONE LAS file.', widget='DirChooser',
                        metavar="las directory Path")
    group5.add_argument('--export',  default=False,
                        help='Should the cleaned point clouds be saved to their own folder.',
                        metavar = "Intermediate Export Option",
                         action='store_true',widget='BlockCheckbox')


#
    process_parser3 = subs.add_parser('Sort')
    group3 = process_parser3.add_argument_group('Just Sorting')
    group3.add_argument('--file', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                        help='Directory containing the LAS files.', widget='DirChooser')
    group3.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.', widget='DirChooser')
    group3.add_argument('--img_path', type=str,
                        default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\images",
                        help='Directory to save the processed files.',
                        metavar="Image Path", widget='DirChooser')

    process_parser4 = subs.add_parser('Everything')
    group4 = process_parser4.add_argument_group('Cleaning + Segmenting + Sorting')
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
    group4.add_argument('--export', default=False,
                        help='Should the cleaned point clouds be saved to their own folder.',
                        metavar="Intermediate Export Option",
                        action='store_true', widget='BlockCheckbox')

    args = parser.parse_args()

    if args.command == 'Clean':
        cleanCld = cleanCloud.fromArgs(args=args)
        cleanCld.run()

    if args.command == 'CleanANDsegment':

        files = []

        if os.path.isdir(args.file):
            fileList = os.listdir(args.file)
            for file in fileList:
                if file.endswith(".las"):
                    files.append(os.path.join(args.file, file))

        else:
            files.append(args.file)

        for x in files:
            cleanCld = cleanCloud(project_file=x, output_dir=args.output_dir, export=args.export)
            cleanCld.run()

            if cleanCld.good_cloud:
                segmentedCloud = seg.fromPrev(prev=cleanCld)
                segmentedCloud.run()

    if args.command == 'Segment':


        segmentedCloud = seg.fromArgs(args=args)
        segmentedCloud.run()

    if args.command == 'Sort':
        tracks = lasProcess.fromArgs(args=args)
        tracks.run()

        images = imgProcess.fromArgs(args=args)
        images.run()

        imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
        imgSort.run()

    if args.command == 'Everything':

        files = []

        if os.path.isdir(args.file):
            fileList = os.listdir(args.file)
            for file in fileList:
                if file.endswith(".las"):
                    files.append(os.path.join(args.file, file))

        else:
            files.append(args.file)

        for x in files:
            cleanCld = cleanCloud(project_file=x, output_dir=args.output_dir, export=args.export)
            cleanCld.run()

            if cleanCld.good_cloud:
                segmentedCloud = seg.fromPrev(prev=cleanCld)
                segmentedCloud.run()



        tracks = lasProcess.fromArgs(args=args)
        tracks.run()

        images = imgProcess.fromArgs(args=args)
        images.run()

        imgSort = IMGsort(tracks.tracksDf, images.imagesDf, tracks.output_dir)
        imgSort.run()


if __name__ == "__main__":
    main()
