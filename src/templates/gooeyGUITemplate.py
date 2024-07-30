# -----------------------------------------------------------------------------------------------------------
# Import Funtions
# -----------------------------------------------------------------------------------------------------------

from gooey import Gooey, GooeyParser
from classTemplate import myClass as mc





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
    group1.add_argument('path', type=str, default = "default1",help='Directory containing the LAS files.')
    group1.add_argument('--output_dir', type=str, default='default1', help='Directory to save the processed files.')
    group1.add_argument('--file', type=str, default='default1', help='Directory to save the processed files.')




    process_parser = subs.add_parser('process')
    group2 = process_parser.add_argument_group('processing')
    group2.add_argument('path', type=str, default = "default2", help='Directory containing the LAS files.')
    group2.add_argument('--output_dir', type=str, default='default2', help='Directory to save the processed files.')
    group2.add_argument('--file', type=str, default='default2', help='Directory to save the processed files.')


    args = parser.parse_args()


    workflow = mc.fromArgs(args=args)

    workflow.run()



    if args.command == 'clean':
        print("clean")

    if args.command == 'process':
        print("process")


if __name__ == "__main__":
    main()