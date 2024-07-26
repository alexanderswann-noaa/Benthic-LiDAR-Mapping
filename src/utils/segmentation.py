# -----------------------------------------------------------------------------------------------------------
# Import Statements
# -----------------------------------------------------------------------------------------------------------

import time
import traceback
import argparse
import os
import psutil
import pathlib

import numpy as np
import CloudCompare.cloudComPy as cc
import CloudCompare.cloudComPy.CSF

from cleanCloud import cleanCloud as cleanCloud


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

# Define a function to determine octree level based on cell size
def octreeLevel(octree, cellSize):
    """
    Determine the octree level based on cell size.

    Args:
    - octree (Octree): Octree object to analyze.
    - cellSize (float): Maximum cell size threshold.

    Returns:
    - int: Selected octree level.
    """
    for oct_elem in range(11, 0, -1):
        if octree.getCellSize(oct_elem) > cellSize:
            print(str(octree.getCellSize(oct_elem)) + " : " + str(oct_elem))
            print(str(octree.getCellSize(oct_elem + 1)) + " : " + str(oct_elem + 1))
            print(str(octree.getCellSize(oct_elem - 1)) + " : " + str(oct_elem - 1))
            return oct_elem

# Define a function to filter out large clouds based on point count
def filterLargeClouds(listOfClouds, maxPoints):
    """
    Filter out large clouds based on a maximum point count threshold.

    Args:
    - listOfClouds (list): List of clouds to filter.
    - maxPoints (int): Maximum number of points threshold.

    Returns:
    - int: Index of the filtered cloud.
    """
    if len(listOfClouds[1]) == 0:
        return -1


    for index in range(40):
        print(index)
        #print(listOfClouds)

        if listOfClouds[1][index].size() < maxPoints:
            return index


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class segmentation:
    def __init__(self, project_file, output_dir):
        print("\n\n")
        announce("Start of New Object")




        if isinstance(project_file, cleanCloud):
            self.input_dir = project_file.input_dir
            self.project_file = project_file
            self.outputDirectory = output_dir

            self.filename = self.project_file.filename


            self.originalPointCloud = self.project_file.originalPointCloud

            self.cleanedPointCloud = self.project_file.cleanedPointCloud

            self.exportOption = "small_output"

        elif os.path.isdir(project_file):
            print("Sorry Jordan cant do that right now :(")
            return


        else:


            self.input_dir = pathlib.Path(project_file).parent
            self.outputDirectory = output_dir



            self.project_file = project_file
            #self.filename = self.project_file.filename


            file = pathlib.Path(project_file)
            self.filename = file.name


            # Load the original point cloud
            self.originalPointCloud = cc.loadPointCloud(os.path.join(self.input_dir, self.filename))
            self.originalPointCloud.setName("Original Point Cloud")


            self.cleanedPointCloud = self.originalPointCloud

            self.exportOption = "small_output"







    @classmethod #https://www.programiz.com/python-programming/methods/built-in/classmethod
    def fromArgs(cls, args):

        my_path = os.path.join(args.output_dir, "lasFiles")
        output_directory = args.output_dir
        file_project = args.file

        return cls(project_file=file_project,
                               output_dir=output_directory)

    @classmethod
    def fromPrev(cls, prev, args):

        my_path = os.path.join(args.output_dir, "lasFiles")
        output_directory = args.output_dir
        file_project = prev

        return cls(project_file=file_project,
                   output_dir=output_directory)

    def add(self):
        announce("Input DIR: " + self.input_dir)


    def segmentFish(self):
        # Select octree level for fish segmentation
        octree = self.cleanedPointCloud.computeOctree(progressCb=None, autoAddChild=True)
        selectedOctreeLevel = octreeLevel(octree, .06)

        # Extract connected components (fish points)
        print(selectedOctreeLevel)
        print(self.cleanedPointCloud)
        extractionResult = cc.ExtractConnectedComponents(clouds=[self.cleanedPointCloud],
                                                         minComponentSize=10,
                                                         octreeLevel=selectedOctreeLevel,
                                                         randomColors=True)
        # print(extractionResult)

        smallComponents = [extractionResult[1][0]]
        allComponents = extractionResult[2] + smallComponents

        # Merge entities to form ground points and fish points
        self.groundPointsV1 = cc.MergeEntities(allComponents, createSFcloudIndex=True)
        self.groundPointsV1.setName("Ground Points: V1")

        self.groundPointsBase = cc.MergeEntities(smallComponents, createSFcloudIndex=True)
        self.groundPointsBase.setName("Ground Points: V1-base")

        self.groundPointsExtra = cc.MergeEntities(extractionResult[2], createSFcloudIndex=True)
        self.groundPointsExtra.setName("Ground Points: V1-extra")

        self.fishPointsV1 = cc.MergeEntities(extractionResult[1][1:], createSFcloudIndex=True)

        self.totalfish = len(extractionResult[1][1:])

        if self.totalfish < 1:
            self.fishPointsV1 = self.originalPointCloud

        self.fishPointsV1.setName("Fish Points : V1 | " + str(
            self.totalfish) + " total fish | Utilized Octree Level for fish segmentation: " + str(
            selectedOctreeLevel))
        print(str(self.totalfish) + " total fish")

        extractionResult = None
        allComponents = None
        smallComponents = None

    def createDEM (self):
        # Create Digital Elevation Model (DEM) of seafloor
        self.seafloorDEM = cc.RasterizeToMesh(self.groundPointsV1,
                                         outputRasterZ=True,
                                         gridStep=.07,
                                         emptyCellFillStrategy=cc.EmptyCellFillOption.KRIGING,
                                         projectionType=cc.ProjectionType.PROJ_MINIMUM_VALUE,
                                         outputRasterSFs=True)
        cc.ccMesh.showSF(self.seafloorDEM, True)

    def computeC2M(self):
        # Compute cloud to mesh distance
        numCpu = psutil.cpu_count()
        bestOctreeLevel = cc.DistanceComputationTools.determineBestOctreeLevel(self.groundPointsBase, self.seafloorDEM)
        computationParams = cc.Cloud2MeshDistancesComputationParams()
        computationParams.signedDistances = True
        computationParams.maxThreadCount = numCpu
        computationParams.octreeLevel = bestOctreeLevel

        cc.DistanceComputationTools.computeCloud2MeshDistances(pointCloud=self.groundPointsBase, mesh=self.seafloorDEM,
                                                               params=computationParams)

    def potentialCoralCloud(self):
        # Create cloud with points greater than .08m above sea floor
        ground_points_base_dictionary = self.groundPointsBase.getScalarFieldDic()
        c2mDistancesSF = self.groundPointsBase.getScalarField(ground_points_base_dictionary['C2M signed distances'])
        self.groundPointsBase.setCurrentScalarField(ground_points_base_dictionary['C2M signed distances'])

        aboveSeaFloorCloud = cc.filterBySFValue(.08, c2mDistancesSF.getMax(), self.groundPointsBase)
        aboveSeaFloorCloud.setName("greater than .08m above sea floor")

        above_sea_floor_dictionary = aboveSeaFloorCloud.getScalarFieldDic()
        c2mDistancesSF2 = aboveSeaFloorCloud.getScalarField(above_sea_floor_dictionary['C2M signed distances'])
        aboveSeaFloorCloud.setCurrentScalarField(above_sea_floor_dictionary['C2M signed distances'])
        aboveSeaFloorCloud.setCurrentDisplayedScalarField(above_sea_floor_dictionary['C2M signed distances'])

        # Filter out highest intensity values
        intensitySF2 = self.groundPointsBase.getScalarField(ground_points_base_dictionary['Intensity'])
        self.groundPointsBase.setCurrentScalarField(ground_points_base_dictionary['Intensity'])

        self.belowIntensityThresholdCloud = cc.filterBySFValue(intensitySF2.getMin(), 320, self.groundPointsBase)
        self.belowIntensityThresholdCloud.setName("Below 320 Intensity")

        below_intensity_threshold_dictionary = self.belowIntensityThresholdCloud.getScalarFieldDic()
        intensitySF3 = self.belowIntensityThresholdCloud.getScalarField(below_intensity_threshold_dictionary['Intensity'])
        self.belowIntensityThresholdCloud.setCurrentScalarField(below_intensity_threshold_dictionary['Intensity'])
        self.belowIntensityThresholdCloud.setCurrentDisplayedScalarField(below_intensity_threshold_dictionary['Intensity'])

        # Combine clouds
        self.possibleCoralCloud = cc.MergeEntities([aboveSeaFloorCloud, self.belowIntensityThresholdCloud],
                                              createSFcloudIndex=True)
        self.possibleCoralCloud.setName("possible corals and other things above the sea floor")

        self.combinedCloud = cc.MergeEntities([self.possibleCoralCloud, self.groundPointsBase], createSFcloudIndex=True)
        self.combinedCloud.setName("everything combined")

    def cleanPotentialCoralCloud(self):
        # Crop out unnecessary components
        potential_coral_dictionary = self.possibleCoralCloud.getScalarFieldDic()
        # print(potential_coral_dictionary)
        self.yCoordSF = self.possibleCoralCloud.getScalarField(potential_coral_dictionary['Coord. Y'])
        self.xCoordSF = self.possibleCoralCloud.getScalarField(potential_coral_dictionary['Coord. X'])
        self.possibleCoralCloud.setCurrentScalarField(potential_coral_dictionary['Coord. Y'])

        factor = .14 * abs((self.yCoordSF.getMin()) - (self.yCoordSF.getMax()))
        distanceCross = abs((self.yCoordSF.getMin()) - (self.yCoordSF.getMax()))
        print(distanceCross)
        print(factor)
        print(self.yCoordSF.getMin())
        print(self.yCoordSF.getMax())
        if distanceCross < 3:
            return

        self.croppedCloud = cc.filterBySFValue(self.yCoordSF.getMin() + factor, self.yCoordSF.getMax() - factor, self.possibleCoralCloud)
        self.croppedCloud.setName("Cropped")

        cropped_cloud_dictionary = self.croppedCloud.getScalarFieldDic()
        print("Hello")
        print(cropped_cloud_dictionary)
        self.croppedCloud.setCurrentScalarField(cropped_cloud_dictionary['Intensity'])
        self.croppedCloud.setCurrentDisplayedScalarField(cropped_cloud_dictionary['Intensity'])

    def segCoral(self):
        # Select octree level for coral segmentation
        cropped_cloud_octree = self.croppedCloud.computeOctree(progressCb=None, autoAddChild=True)
        coralOctreeLevel = octreeLevel(cropped_cloud_octree, .02)

        # Extract coral points
        coralExtractionResult = cc.ExtractConnectedComponents(clouds=[self.croppedCloud],
                                                              minComponentSize=10,
                                                              octreeLevel=coralOctreeLevel,
                                                              randomColors=True,
                                                              maxNumberComponents=100000)
        # print(coralExtractionResult)

        self.nonCoralPoints = cc.MergeEntities(coralExtractionResult[2], createSFcloudIndex=True)
        self.nonCoralPoints.setName("Not Coral Points")

        print("Section is " + str(self.yCoordSF.getMin()) + "m by " + str(self.yCoordSF.getMax()) + "m or " + str(
            self.yCoordSF.getMax() - self.yCoordSF.getMin()) + "m wide")

        print("Section is " + str(self.xCoordSF.getMin()) + "m by " + str(self.xCoordSF.getMax()) + "m or " + str(
            self.xCoordSF.getMax() - self.xCoordSF.getMin()) + "m long")

        print("Area of section is " + str(
            (self.xCoordSF.getMax() - self.xCoordSF.getMin()) * (self.yCoordSF.getMax() - self.yCoordSF.getMin())) + "m^2")

        self.combinedCoralPoints = coralExtractionResult[2] + coralExtractionResult[1]
        self.allCoralAndNonCoralPoints = cc.MergeEntities(self.combinedCoralPoints, createSFcloudIndex=True)
        self.allCoralAndNonCoralPoints.setName("All Coral + Non Coral points")

        self.lowerBound = filterLargeClouds(coralExtractionResult, 5000)

        if self.lowerBound == -1:
            return

        self.coralPoints = cc.MergeEntities(coralExtractionResult[1][self.lowerBound:], createSFcloudIndex=True)
        self.coralPoints.setName("Coral Points : V1 | " + str(
            len(coralExtractionResult[1][
                self.lowerBound:])) + " total coral | Utilized Octree Level for coral segmentation: " + str(
            coralOctreeLevel))

        self.bigCoralPoints = cc.MergeEntities(coralExtractionResult[1][:self.lowerBound], createSFcloudIndex=True)

        if len(coralExtractionResult[1][:self.lowerBound]) > 1:
            self.bigCoralPoints.setName("Big Coral Points : V1 | " + str(
                len(coralExtractionResult[1][
                    :self.lowerBound])) + " total coral | Utilized Octree Level for coral segmentation: " + str(
                coralOctreeLevel))

        print(str(len(coralExtractionResult[1])) + " total coral")

        coralExtractionResult = None
        combinedCoralPoints = None

    def export(self):
        # Export clouds and meshes


        self.cleanedPointCloud.setCurrentScalarField(0)
        self.groundPointsV1.setCurrentScalarField(0)
        self.fishPointsV1.setCurrentScalarField(0)
        self.groundPointsExtra.setCurrentScalarField(0)
        self.groundPointsBase.setCurrentScalarField(0)

        scalarFieldDictionary = self.groundPointsBase.getScalarFieldDic()
        print(scalarFieldDictionary)

        colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
        defaultScale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)
        highContrastScale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HIGH_CONTRAST)

        self.cleanedPointCloud.getScalarField(0).setColorScale(defaultScale)
        self.groundPointsV1.getScalarField(0).setColorScale(defaultScale)
        self.fishPointsV1.getScalarField(0).setColorScale(defaultScale)
        self.groundPointsExtra.getScalarField(0).setColorScale(defaultScale)
        self.groundPointsBase.getScalarField(0).setColorScale(defaultScale)
        self.belowIntensityThresholdCloud.getScalarField(0).setColorScale(defaultScale)
        self.possibleCoralCloud.getScalarField(0).setColorScale(defaultScale)
        self.combinedCloud.getScalarField(0).setColorScale(defaultScale)
        self.croppedCloud.getScalarField(0).setColorScale(defaultScale)
        if self.exportOption == "all" or self.exportOption == "large_output":
            if self.lowerBound > 1:
                self.bigCoralPoints.getScalarField(
                    self.bigCoralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(highContrastScale)
            self.coralPoints.getScalarField(self.coralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(
                highContrastScale)
            self.allCoralAndNonCoralPoints.getScalarField(0).setColorScale(defaultScale)
            self.nonCoralPoints.getScalarField(0).setColorScale(defaultScale)

            self.cleanedPointCloud.setCurrentDisplayedScalarField(0)
            self.groundPointsV1.setCurrentDisplayedScalarField(0)
            self.fishPointsV1.setCurrentDisplayedScalarField(0)
            self.groundPointsExtra.setCurrentDisplayedScalarField(0)
            self.groundPointsBase.setCurrentDisplayedScalarField(0)
            self.possibleCoralCloud.setCurrentDisplayedScalarField(0)
            self.combinedCloud.setCurrentDisplayedScalarField(0)

            if self.lowerBound > 1:
                self.bigCoralPoints.setCurrentDisplayedScalarField(
                    self.bigCoralPoints.getScalarFieldDic()['Original cloud index'])
            self.coralPoints.setCurrentDisplayedScalarField(self.coralPoints.getScalarFieldDic()['Original cloud index'])
            self.allCoralAndNonCoralPoints.setCurrentDisplayedScalarField(0)
            self.nonCoralPoints.setCurrentDisplayedScalarField(0)

            outputFile = os.path.join(self.outputDirectory, "CLEAN" + self.filename[:-4] + ".bin")

            if self.lowerBound > 1:
                exportResult = cc.SaveEntities(
                    [self.originalPointCloud, self.cleanedPointCloud, self.fishPointsV1, self.groundPointsV1, self.groundPointsExtra,
                     self.groundPointsBase,
                     self.aboveSeaFloorCloud, self.belowIntensityThresholdCloud, self.possibleCoralCloud, self.combinedCloud, self.croppedCloud,
                     self.allCoralAndNonCoralPoints, self.nonCoralPoints, self.bigCoralPoints, self.coralPoints, self.seafloorDEM], outputFile)
            else:
                exportResult = cc.SaveEntities(
                    [self.originalPointCloud, self.cleanedPointCloud, self.fishPointsV1, self.groundPointsV1, self.groundPointsExtra,
                     self.groundPointsBase,
                     self.aboveSeaFloorCloud, self.belowIntensityThresholdCloud, self.possibleCoralCloud, self.combinedCloud, self.croppedCloud,
                     self.allCoralAndNonCoralPoints, self.nonCoralPoints, self.coralPoints, self.seafloorDEM], outputFile)

        # smallOutputDirectory = os.path.join(outputDirectory, "smallClean")
        # if not os.path.exists(smallOutputDirectory):
        #     os.makedirs(smallOutputDirectory)
        if self.exportOption == "all" or self.exportOption == "small_output":
            self.coralPoints.setCurrentDisplayedScalarField(self.coralPoints.getScalarFieldDic()['Original cloud index'])
            if self.totalfish > 0:
                self.fishPointsV1.setCurrentDisplayedScalarField(self.fishPointsV1.getScalarFieldDic()['Original cloud index'])
            self.groundPointsBase.setCurrentDisplayedScalarField(
                self.groundPointsBase.getScalarFieldDic()['C2M signed distances'])

            self.coralPoints.getScalarField(self.coralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(
                highContrastScale)
            if self.totalfish > 0:
                self.fishPointsV1.getScalarField(self.fishPointsV1.getScalarFieldDic()['Original cloud index']).setColorScale(
                    highContrastScale)
            self.groundPointsBase.getScalarField(self.groundPointsBase.getScalarFieldDic()['C2M signed distances']).setColorScale(
                highContrastScale)

            lasOutputDirectory = os.path.join(self.outputDirectory, "lasFiles")
            if not os.path.exists(lasOutputDirectory):
                os.makedirs(lasOutputDirectory)

            binOutputDirectory = os.path.join(self.outputDirectory, "binFiles")
            if not os.path.exists(binOutputDirectory):
                os.makedirs(binOutputDirectory)

            smallOutputFile = os.path.join(binOutputDirectory, "SMALL" + self.filename[:-4] + ".bin")
            smalllasOutputFile = os.path.join(lasOutputDirectory, "SMALL" + self.filename[:-4] + ".las")
            exportResult0 = cc.SaveEntities(
                [self.originalPointCloud, self.fishPointsV1, self.groundPointsBase, self.coralPoints, self.seafloorDEM], smallOutputFile)
            exportlasResult0 = cc.SavePointCloud(self.groundPointsBase, smalllasOutputFile)

    def run(self):
        """

                    """
        announce("Template Workflow")
        t0 = time.time()



        self.segmentFish()
        self.createDEM()
        self.computeC2M()
        self.potentialCoralCloud()
        self.cleanPotentialCoralCloud()
        self.segCoral()
        self.export()

        announce("Workflow Completed")

        print(f"NOTE: Completed in {np.around(((time.time() - t0) / 60), 2)} minutes")

def main():
    """

    """

    parser = argparse.ArgumentParser(description='Process and classify point clouds.')
    parser.add_argument('--path', type=str, help='Directory containing the LAS files.')
    parser.add_argument('--output_dir', type=str, default='.', help='Directory to save the processed files.')
    parser.add_argument('--file', type=str, default='.', help='Directory to save the processed files.')

    args = parser.parse_args()
    print(args)
    print(type(args))

    try:

        # Run the workflow


        #python "C:\Users\Alexander.Swann\PycharmProjects\pythonProject\src\classTemplate.py" "hello" --output_dir "hello again" --file "my_files yay"

        # workflow = segmentation.fromArgs(args = args)
        #
        # workflow.run()




        workflow2 = segmentation(input_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput\lasFiles",
                            project_file=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput\lasFiles\SMALLprocessed_LLS_2024-03-15T054218.010100_1_3.las",
                            output_dir=r"C:\Users\Alexander.Swann\Desktop\testingDATA\newoutput")

        workflow2.run()

        print("All Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())




if __name__ == '__main__':

    main()