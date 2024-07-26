# -----------------------------------------------------------------------------------------------------------
# Import Statements
# -----------------------------------------------------------------------------------------------------------

import time
import os
import traceback
import argparse
import pathlib

import numpy as np

import CloudCompare.cloudComPy as cc
import CloudCompare.cloudComPy.CSF

from removeBadCloud import removeBadCloud as removeClds


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

class cleanCloud:
    def __init__(self, input_dir, project_file, output_dir):
        print("\n\n")
        announce("Start of New Object")
        self.input_dir = input_dir
        self.project_file = project_file
        self.output_dir = output_dir

    @classmethod  # https://www.programiz.com/python-programming/methods/built-in/classmethod
    def fromArgs(cls, args):

        my_path = args.path
        output_directory = args.output_dir
        file_project = args.file

        return cls(input_dir=my_path,
                   project_file=file_project,
                   output_dir=output_directory)

    def add(self):
        announce("Input DIR: " + self.input_dir)

    def clean(self):
        directory = self.input_dir
        file = pathlib.Path(self.project_file)
        filename = file.name

        self.filename = filename
        outputDirectory = self.output_dir
        """
        Process and classify a point cloud.

        Args:
        - directory (str): Directory path containing the point cloud file.
        - filename (str): Name of the point cloud file.
        - outputDirectory (str): Directory to save processed files.
        """
        # Load the original point cloud
        originalPointCloud = cc.loadPointCloud(os.path.join(directory, filename))
        originalPointCloud.setName("Original Point Cloud")

        self.originalPointCloud = originalPointCloud

        # Export coordinate to scalar fields
        exportResult = originalPointCloud.exportCoordToSF(True, True, True)

        # Get scalar fields
        scalarFieldX = originalPointCloud.getScalarField(3)
        scalarFieldY = originalPointCloud.getScalarField(4)
        scalarFieldZ = originalPointCloud.getScalarField(5)
        scalarFieldDictionary = originalPointCloud.getScalarFieldDic()
        print(scalarFieldDictionary)

        intensityScalarField = originalPointCloud.getScalarField(scalarFieldDictionary['Intensity'])

        # Filter out lowest intensity values -> values below 100
        originalPointCloud.setCurrentScalarField(0)
        filteredIntensityCloud = cc.filterBySFValue(100, intensityScalarField.getMax(), originalPointCloud)

        y_across = abs(abs(scalarFieldY.getMin()) - abs(scalarFieldY.getMax()))
        x_across = abs(abs(scalarFieldX.getMin()) - abs(scalarFieldX.getMax()))
        areatot = x_across * y_across
        ptsPermeterSquared = filteredIntensityCloud.size() / areatot

        print(y_across)
        print(x_across)
        print(areatot)
        print(ptsPermeterSquared)

        if ptsPermeterSquared < 7000 or filteredIntensityCloud.size() < 100000:
            badOutputDirectory = os.path.join(outputDirectory, "badFiles")
            if not os.path.exists(badOutputDirectory):
                os.makedirs(badOutputDirectory)
            badoutputFile = os.path.join(badOutputDirectory, "BAD" + filename[:-4] + ".las")
            # badexport = cc.SaveEntities([originalPointCloud], badoutputFile)
            badexport = cc.SavePointCloud(originalPointCloud, badoutputFile)

            return

        # Compute CSF (Conditional Sampling Framework) plugin for filtering lowest z values
        clouds = cc.CSF.computeCSF(filteredIntensityCloud)
        lowZPoints = clouds[0]
        highZPoints = clouds[1]

        # Remove statistical outliers using SOR filter
        cloudReference = cc.CloudSamplingTools.sorFilter(knn=6, nSigma=10, cloud=highZPoints)
        cleanedPointCloud, res = highZPoints.partialClone(cloudReference)
        cleanedPointCloud.setName("Cleaned Point Cloud")

        self.cleanedPointCloud = cleanedPointCloud

        lasOutputDirectory = os.path.join(outputDirectory, "lasFiles")

        if not os.path.exists(lasOutputDirectory):
            os.makedirs(lasOutputDirectory)

        smalllasOutputFile = os.path.join(lasOutputDirectory, "SMALL" + filename[:-4] + ".las")

        cc.SavePointCloud(cleanedPointCloud, smalllasOutputFile)
        print("exported")

    def run(self):
        """

                    """
        announce("Template Workflow")
        t0 = time.time()

        self.clean()

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

        # python "C:\Users\Alexander.Swann\PycharmProjects\pythonProject\src\classTemplate.py" "hello" --output_dir "hello again" --file "my_files yay"
        workflow = cleanCloud.fromArgs(args=args)

        workflow.run()

        workflow2 = cleanCloud(input_dir="input_path",
                               project_file="project_file",
                               output_dir="output_path")

        workflow2.run()

        print("All Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()
