# -----------------------------------------------------------------------------------------------------------
# Import Statements
# -----------------------------------------------------------------------------------------------------------

from gooey import Gooey, GooeyParser

from cleanCloud import cleanCloud as cleanCloud

from segmentation import segmentation as seg





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

    #figure out what above line does

    subs = parser.add_subparsers(help='commands', dest='command')

#____
    clean_parser = subs.add_parser('clean')
    group1 = clean_parser.add_argument_group('General')
    group1.add_argument('path', type=str, default = r"C:\Users\Alexander.Swann\Desktop\testingDATA\data", help='Directory containing the LAS files.')
    group1.add_argument('--output_dir', type=str, default= r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput', help='Directory to save the processed files.')
    group1.add_argument('--file', type=str, default= r'C:\Users\Alexander.Swann\Desktop\testingDATA\data\processed_LLS_2024-03-15T054218.010100_1_3.las', help='Directory to save the processed files.')




    process_parser = subs.add_parser('process')
    group2 = process_parser.add_argument_group('processing')
    group2.add_argument('path', type=str, default=r"C:\Users\Alexander.Swann\Desktop\testingDATA\data",
                        help='Directory containing the LAS files.')
    group2.add_argument('--output_dir', type=str, default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput',
                        help='Directory to save the processed files.')
    group2.add_argument('--file', type=str,
                        default=r'C:\Users\Alexander.Swann\Desktop\testingDATA\data\processed_LLS_2024-03-15T054218.010100_1_3.las',
                        help='Directory to save the processed files.')

    args = parser.parse_args()









    if args.command == 'clean':
        cleanCld = cleanCloud.fromArgs(args=args)
        cleanCld.run()

    if args.command == 'process':
        cleanCld = cleanCloud.fromArgs(args=args)
        cleanCld.run()

        segmentedCloud = seg.fromPrev(prev=cleanCld, args=args)
        segmentedCloud.run()


if __name__ == "__main__":
    main()