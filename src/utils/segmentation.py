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
    def __init__(self, input_dir, project_file, output_dir):
        print("\n\n")
        announce("Start of New Object")

        if isinstance(project_file, cleanCloud):
            self.input_dir = input_dir
            self.project_file = project_file
            self.output_dir = output_dir

            self.originalPointCloud = self.project_file.originalPointCloud
            self.filteredIntensityCloud = self.project_file.filteredIntensityCloud
            self.filename = self.project_file.filename

            self.cleanedPointCloud = self.project_file.cleanedPointCloud

            self.exportOption = "small_output"




        else:
            print(False)





    @classmethod #https://www.programiz.com/python-programming/methods/built-in/classmethod
    def fromArgs(cls, args):

        my_path = args.path
        output_directory = args.output_dir
        file_project = args.file

        return cls(input_dir=my_path,
                               project_file=file_project,
                               output_dir=output_directory)

    @classmethod
    def fromPrev(cls, prev, args):

        my_path = args.path
        output_directory = args.output_dir
        file_project = prev

        return cls(input_dir=my_path,
                   project_file=file_project,
                   output_dir=output_directory)

    def add(self):
        announce("Input DIR: " + self.input_dir)


    def seg(self):

        directory = self.input_dir
        #file = pathlib.Path(self.project_file)
        filename = self.filename
        outputDirectory = self.output_dir

        cleanedPointCloud = self.cleanedPointCloud
        originalPointCloud = self.originalPointCloud
        filteredIntensityCloud = self.filteredIntensityCloud
        exportOption = self.exportOption



        # Select octree level for fish segmentation
        octree = cleanedPointCloud.computeOctree(progressCb=None, autoAddChild=True)
        selectedOctreeLevel = octreeLevel(octree, .06)

        # Extract connected components (fish points)
        print(selectedOctreeLevel)
        print(cleanedPointCloud)
        extractionResult = cc.ExtractConnectedComponents(clouds=[cleanedPointCloud],
                                                         minComponentSize=10,
                                                         octreeLevel=selectedOctreeLevel,
                                                         randomColors=True)
        # print(extractionResult)

        smallComponents = [extractionResult[1][0]]
        allComponents = extractionResult[2] + smallComponents

        # Merge entities to form ground points and fish points
        groundPointsV1 = cc.MergeEntities(allComponents, createSFcloudIndex=True)
        groundPointsV1.setName("Ground Points: V1")

        groundPointsBase = cc.MergeEntities(smallComponents, createSFcloudIndex=True)
        groundPointsBase.setName("Ground Points: V1-base")

        groundPointsExtra = cc.MergeEntities(extractionResult[2], createSFcloudIndex=True)
        groundPointsExtra.setName("Ground Points: V1-extra")

        fishPointsV1 = cc.MergeEntities(extractionResult[1][1:], createSFcloudIndex=True)

        totalfish = len(extractionResult[1][1:])

        if totalfish < 1:
            fishPointsV1 = originalPointCloud

        fishPointsV1.setName("Fish Points : V1 | " + str(
            totalfish) + " total fish | Utilized Octree Level for fish segmentation: " + str(
            selectedOctreeLevel))
        print(str(totalfish) + " total fish")

        extractionResult = None
        allComponents = None
        smallComponents = None

        # Create Digital Elevation Model (DEM) of seafloor
        seafloorDEM = cc.RasterizeToMesh(groundPointsV1,
                                         outputRasterZ=True,
                                         gridStep=.07,
                                         emptyCellFillStrategy=cc.EmptyCellFillOption.KRIGING,
                                         projectionType=cc.ProjectionType.PROJ_MINIMUM_VALUE,
                                         outputRasterSFs=True)
        cc.ccMesh.showSF(seafloorDEM, True)

        # Compute cloud to mesh distance
        numCpu = psutil.cpu_count()
        bestOctreeLevel = cc.DistanceComputationTools.determineBestOctreeLevel(groundPointsBase, seafloorDEM)
        computationParams = cc.Cloud2MeshDistancesComputationParams()
        computationParams.signedDistances = True
        computationParams.maxThreadCount = numCpu
        computationParams.octreeLevel = bestOctreeLevel

        cc.DistanceComputationTools.computeCloud2MeshDistances(pointCloud=groundPointsBase, mesh=seafloorDEM,
                                                               params=computationParams)

        # Create cloud with points greater than .08m above sea floor
        ground_points_base_dictionary = groundPointsBase.getScalarFieldDic()
        c2mDistancesSF = groundPointsBase.getScalarField(ground_points_base_dictionary['C2M signed distances'])
        groundPointsBase.setCurrentScalarField(ground_points_base_dictionary['C2M signed distances'])

        aboveSeaFloorCloud = cc.filterBySFValue(.08, c2mDistancesSF.getMax(), groundPointsBase)
        aboveSeaFloorCloud.setName("greater than .08m above sea floor")

        above_sea_floor_dictionary = aboveSeaFloorCloud.getScalarFieldDic()
        c2mDistancesSF2 = aboveSeaFloorCloud.getScalarField(above_sea_floor_dictionary['C2M signed distances'])
        aboveSeaFloorCloud.setCurrentScalarField(above_sea_floor_dictionary['C2M signed distances'])
        aboveSeaFloorCloud.setCurrentDisplayedScalarField(above_sea_floor_dictionary['C2M signed distances'])

        # Filter out highest intensity values
        intensitySF2 = groundPointsBase.getScalarField(ground_points_base_dictionary['Intensity'])
        groundPointsBase.setCurrentScalarField(ground_points_base_dictionary['Intensity'])

        belowIntensityThresholdCloud = cc.filterBySFValue(intensitySF2.getMin(), 320, groundPointsBase)
        belowIntensityThresholdCloud.setName("Below 320 Intensity")

        below_intensity_threshold_dictionary = belowIntensityThresholdCloud.getScalarFieldDic()
        intensitySF3 = belowIntensityThresholdCloud.getScalarField(below_intensity_threshold_dictionary['Intensity'])
        belowIntensityThresholdCloud.setCurrentScalarField(below_intensity_threshold_dictionary['Intensity'])
        belowIntensityThresholdCloud.setCurrentDisplayedScalarField(below_intensity_threshold_dictionary['Intensity'])

        # Combine clouds
        possibleCoralCloud = cc.MergeEntities([aboveSeaFloorCloud, belowIntensityThresholdCloud],
                                              createSFcloudIndex=True)
        possibleCoralCloud.setName("possible corals and other things above the sea floor")

        combinedCloud = cc.MergeEntities([possibleCoralCloud, groundPointsBase], createSFcloudIndex=True)
        combinedCloud.setName("everything combined")

        # Crop out unnecessary components
        potential_coral_dictionary = possibleCoralCloud.getScalarFieldDic()
        # print(potential_coral_dictionary)
        yCoordSF = possibleCoralCloud.getScalarField(potential_coral_dictionary['Coord. Y'])
        xCoordSF = possibleCoralCloud.getScalarField(potential_coral_dictionary['Coord. X'])
        possibleCoralCloud.setCurrentScalarField(potential_coral_dictionary['Coord. Y'])

        factor = .14 * abs((yCoordSF.getMin()) - (yCoordSF.getMax()))
        distanceCross = abs((yCoordSF.getMin()) - (yCoordSF.getMax()))
        print(distanceCross)
        print(factor)
        print(yCoordSF.getMin())
        print(yCoordSF.getMax())
        if distanceCross < 3:
            return

        croppedCloud = cc.filterBySFValue(yCoordSF.getMin() + factor, yCoordSF.getMax() - factor, possibleCoralCloud)
        croppedCloud.setName("Cropped")

        cropped_cloud_dictionary = croppedCloud.getScalarFieldDic()
        print("Hello")
        print(cropped_cloud_dictionary)
        croppedCloud.setCurrentScalarField(cropped_cloud_dictionary['Intensity'])
        croppedCloud.setCurrentDisplayedScalarField(cropped_cloud_dictionary['Intensity'])

        # Select octree level for coral segmentation
        cropped_cloud_octree = croppedCloud.computeOctree(progressCb=None, autoAddChild=True)
        coralOctreeLevel = octreeLevel(cropped_cloud_octree, .02)

        # Extract coral points
        coralExtractionResult = cc.ExtractConnectedComponents(clouds=[croppedCloud],
                                                              minComponentSize=10,
                                                              octreeLevel=coralOctreeLevel,
                                                              randomColors=True,
                                                              maxNumberComponents=100000)
        # print(coralExtractionResult)

        nonCoralPoints = cc.MergeEntities(coralExtractionResult[2], createSFcloudIndex=True)
        nonCoralPoints.setName("Not Coral Points")

        print("Section is " + str(yCoordSF.getMin()) + "m by " + str(yCoordSF.getMax()) + "m or " + str(
            yCoordSF.getMax() - yCoordSF.getMin()) + "m wide")

        print("Section is " + str(xCoordSF.getMin()) + "m by " + str(xCoordSF.getMax()) + "m or " + str(
            xCoordSF.getMax() - xCoordSF.getMin()) + "m long")

        print("Area of section is " + str(
            (xCoordSF.getMax() - xCoordSF.getMin()) * (yCoordSF.getMax() - yCoordSF.getMin())) + "m^2")

        combinedCoralPoints = coralExtractionResult[2] + coralExtractionResult[1]
        allCoralAndNonCoralPoints = cc.MergeEntities(combinedCoralPoints, createSFcloudIndex=True)
        allCoralAndNonCoralPoints.setName("All Coral + Non Coral points")

        lowerBound = filterLargeClouds(coralExtractionResult, 5000)

        if lowerBound == -1:
            return

        coralPoints = cc.MergeEntities(coralExtractionResult[1][lowerBound:], createSFcloudIndex=True)
        coralPoints.setName("Coral Points : V1 | " + str(
            len(coralExtractionResult[1][
                lowerBound:])) + " total coral | Utilized Octree Level for coral segmentation: " + str(
            coralOctreeLevel))

        bigCoralPoints = cc.MergeEntities(coralExtractionResult[1][:lowerBound], createSFcloudIndex=True)

        if len(coralExtractionResult[1][:lowerBound]) > 1:
            bigCoralPoints.setName("Big Coral Points : V1 | " + str(
                len(coralExtractionResult[1][
                    :lowerBound])) + " total coral | Utilized Octree Level for coral segmentation: " + str(
                coralOctreeLevel))

        print(str(len(coralExtractionResult[1])) + " total coral")

        coralExtractionResult = None
        combinedCoralPoints = None

        # Export clouds and meshes
        finalPointCloud = filteredIntensityCloud
        cleanedPointCloud.setCurrentScalarField(0)
        groundPointsV1.setCurrentScalarField(0)
        fishPointsV1.setCurrentScalarField(0)
        groundPointsExtra.setCurrentScalarField(0)
        groundPointsBase.setCurrentScalarField(0)

        scalarFieldDictionary = groundPointsBase.getScalarFieldDic()
        print(scalarFieldDictionary)

        colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
        defaultScale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)
        highContrastScale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HIGH_CONTRAST)

        cleanedPointCloud.getScalarField(0).setColorScale(defaultScale)
        groundPointsV1.getScalarField(0).setColorScale(defaultScale)
        fishPointsV1.getScalarField(0).setColorScale(defaultScale)
        groundPointsExtra.getScalarField(0).setColorScale(defaultScale)
        groundPointsBase.getScalarField(0).setColorScale(defaultScale)
        belowIntensityThresholdCloud.getScalarField(0).setColorScale(defaultScale)
        possibleCoralCloud.getScalarField(0).setColorScale(defaultScale)
        combinedCloud.getScalarField(0).setColorScale(defaultScale)
        croppedCloud.getScalarField(0).setColorScale(defaultScale)
        if exportOption == "all" or exportOption == "large_output":
            if lowerBound > 1:
                bigCoralPoints.getScalarField(
                    bigCoralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(highContrastScale)
            coralPoints.getScalarField(coralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(
                highContrastScale)
            allCoralAndNonCoralPoints.getScalarField(0).setColorScale(defaultScale)
            nonCoralPoints.getScalarField(0).setColorScale(defaultScale)

            cleanedPointCloud.setCurrentDisplayedScalarField(0)
            groundPointsV1.setCurrentDisplayedScalarField(0)
            fishPointsV1.setCurrentDisplayedScalarField(0)
            groundPointsExtra.setCurrentDisplayedScalarField(0)
            groundPointsBase.setCurrentDisplayedScalarField(0)
            possibleCoralCloud.setCurrentDisplayedScalarField(0)
            combinedCloud.setCurrentDisplayedScalarField(0)

            if lowerBound > 1:
                bigCoralPoints.setCurrentDisplayedScalarField(
                    bigCoralPoints.getScalarFieldDic()['Original cloud index'])
            coralPoints.setCurrentDisplayedScalarField(coralPoints.getScalarFieldDic()['Original cloud index'])
            allCoralAndNonCoralPoints.setCurrentDisplayedScalarField(0)
            nonCoralPoints.setCurrentDisplayedScalarField(0)

            outputFile = os.path.join(outputDirectory, "CLEAN" + filename[:-4] + ".bin")

            if lowerBound > 1:
                exportResult = cc.SaveEntities(
                    [originalPointCloud, cleanedPointCloud, fishPointsV1, groundPointsV1, groundPointsExtra,
                     groundPointsBase,
                     aboveSeaFloorCloud, belowIntensityThresholdCloud, possibleCoralCloud, combinedCloud, croppedCloud,
                     allCoralAndNonCoralPoints, nonCoralPoints, bigCoralPoints, coralPoints, seafloorDEM], outputFile)
            else:
                exportResult = cc.SaveEntities(
                    [originalPointCloud, cleanedPointCloud, fishPointsV1, groundPointsV1, groundPointsExtra,
                     groundPointsBase,
                     aboveSeaFloorCloud, belowIntensityThresholdCloud, possibleCoralCloud, combinedCloud, croppedCloud,
                     allCoralAndNonCoralPoints, nonCoralPoints, coralPoints, seafloorDEM], outputFile)

        # smallOutputDirectory = os.path.join(outputDirectory, "smallClean")
        # if not os.path.exists(smallOutputDirectory):
        #     os.makedirs(smallOutputDirectory)
        if exportOption == "all" or exportOption == "small_output":
            coralPoints.setCurrentDisplayedScalarField(coralPoints.getScalarFieldDic()['Original cloud index'])
            if totalfish > 0:
                fishPointsV1.setCurrentDisplayedScalarField(fishPointsV1.getScalarFieldDic()['Original cloud index'])
            groundPointsBase.setCurrentDisplayedScalarField(
                groundPointsBase.getScalarFieldDic()['C2M signed distances'])

            coralPoints.getScalarField(coralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(
                highContrastScale)
            if totalfish > 0:
                fishPointsV1.getScalarField(fishPointsV1.getScalarFieldDic()['Original cloud index']).setColorScale(
                    highContrastScale)
            groundPointsBase.getScalarField(groundPointsBase.getScalarFieldDic()['C2M signed distances']).setColorScale(
                highContrastScale)

            lasOutputDirectory = os.path.join(outputDirectory, "lasFiles")
            if not os.path.exists(lasOutputDirectory):
                os.makedirs(lasOutputDirectory)

            binOutputDirectory = os.path.join(outputDirectory, "binFiles")
            if not os.path.exists(binOutputDirectory):
                os.makedirs(binOutputDirectory)

            smallOutputFile = os.path.join(binOutputDirectory, "SMALL" + filename[:-4] + ".bin")
            smalllasOutputFile = os.path.join(lasOutputDirectory, "SMALL" + filename[:-4] + ".las")
            exportResult0 = cc.SaveEntities(
                [originalPointCloud, fishPointsV1, groundPointsBase, coralPoints, seafloorDEM], smallOutputFile)
            exportlasResult0 = cc.SavePointCloud(groundPointsBase, smalllasOutputFile)

    def run(self):
        """

                    """
        announce("Template Workflow")
        t0 = time.time()

        self.seg()

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
        workflow = segmentation.fromArgs(args = args)

        workflow.run()




        workflow2 = segmentation(input_dir="input_path",
                            project_file="project_file",
                            output_dir="output_path")

        workflow2.run()

        print("All Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())




if __name__ == '__main__':

    main()