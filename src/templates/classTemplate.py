# -----------------------------------------------------------------------------------------------------------
# Import Funtions
# -----------------------------------------------------------------------------------------------------------

import time
import traceback
import argparse

import numpy as np

# -----------------------------------------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------------------------------------

def announce(announcement: str):
    """
    Print whatever you would like with formatting.
    """
    print("\n###############################################")
    print(announcement)
    print("###############################################\n")




# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class myClass:
    def __init__(self, input_dir, project_file, output_dir):
        print("\n\n")
        announce("Start of New Object")
        self.input_dir = input_dir
        self.project_file = project_file
        self.output_dir = output_dir


    @classmethod #https://www.programiz.com/python-programming/methods/built-in/classmethod
    def fromArgs(cls, args):

        my_path = args.path
        output_directory = args.output_dir
        file_project = args.file

        return cls(input_dir=my_path,
                               project_file=file_project,
                               output_dir=output_directory)

    def add(self):
        announce("Input DIR: " + self.input_dir)


    def run(self):
        """

                    """
        announce("Template Workflow")
        t0 = time.time()

        self.add()

        announce("Workflow Completed")

        print(f"NOTE: Completed in {np.around(((time.time() - t0) / 60), 2)} minutes")

def main():
    """

    """

    parser = argparse.ArgumentParser(description='Process and classify point clouds.')
    parser.add_argument('path', type=str, help='Directory containing the LAS files.')
    parser.add_argument('--output_dir', type=str, default='.', help='Directory to save the processed files.')
    parser.add_argument('--file', type=str, default='.', help='Directory to save the processed files.')

    args = parser.parse_args()
    print(args)
    print(type(args))

    try:

        # Run the workflow


        #python "C:\Users\Alexander.Swann\PycharmProjects\pythonProject\src\classTemplate.py" "hello" --output_dir "hello again" --file "my_files yay"
        workflow = myClass.fromArgs(args = args)

        workflow.run()




        workflow2 = myClass(input_dir="input_path",
                            project_file="project_file",
                            output_dir="output_path")

        workflow2.run()

        print("All Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())




if __name__ == '__main__':
    #
    # main(sys.argv[1],  # Device
    #      sys.argv[2],  # Input Path
    #      sys.argv[3],  # Project File
    #      sys.argv[4],  # Output Path
    #      sys.argv[5],  # Quality
    #      sys.argv[6])  # Target Percentage
    main()