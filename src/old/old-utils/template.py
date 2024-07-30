# -----------------------------------------------------------------------------------------------------------
# Import Funtions
# -----------------------------------------------------------------------------------------------------------

import os
import sys
import time
import datetime
import traceback

import numpy as np

# -----------------------------------------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------------------------------------

def announce(announcement: str):
    """
    Gabriel's message to the world.
    """
    print("\n###############################################")
    print(announcement)
    print("###############################################\n")




# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class myClass:
    def __init__(self, device, input_dir, project_file, output_dir, quality='high', target_percentage=75):
        announce("Hello")



    def run(self):
        """

                    """
        announce("Structure from Motion")
        t0 = time.time()

        self.add_photos()

        announce("Workflow Completed")
        print(f"NOTE: Processing finished, results saved to {self.output_dir}")
        print(f"NOTE: Completed in {np.around(((time.time() - t0) / 60), 2)} minutes")

def main(device, input_path, project_file, output_path, quality, target_percentage):
    """

    """

    try:
        workflow = myClass(device=device,
                               input_dir=input_path,
                               project_file=project_file,
                               output_dir=output_path,
                               quality=quality,
                               target_percentage=target_percentage)
        workflow.run()

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':

    main(sys.argv[1],  # Device
         sys.argv[2],  # Input Path
         sys.argv[3],  # Project File
         sys.argv[4],  # Output Path
         sys.argv[5],  # Quality
         sys.argv[6])  # Target Percentage