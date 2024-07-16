import argparse
import os
import sys
import math
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import psutil
from matplotlib import colors
import argparse
from gooey import Gooey, GooeyParser

# Importing custom modules from CloudCompare
import CloudCompare.cloudComPy as cc
import CloudCompare.cloudComPy.CSF

# os.environ["_CCTRACE_"]="ON" # Uncomment to enable C++ debug traces (optional)

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

# Define the main processing and classification function
def cleanAndClassify(directory, filename, outputDirectory, exportOption):
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

    # Export coordinate to scalar fields
    exportResult = originalPointCloud.exportCoordToSF(True, True, True)

    # Get scalar fields
    scalarFieldX = originalPointCloud.getScalarField(3)
    scalarFieldY = originalPointCloud.getScalarField(4)
    scalarFieldZ = originalPointCloud.getScalarField(5)
    scalarFieldDictionary = originalPointCloud.getScalarFieldDic()
    print(scalarFieldDictionary)

    intensityScalarField = originalPointCloud.getScalarField(scalarFieldDictionary['Intensity'])

    # Filter out lowest intensity values
    originalPointCloud.setCurrentScalarField(0)
    filteredIntensityCloud = cc.filterBySFValue(100, intensityScalarField.getMax(), originalPointCloud)

    print(filteredIntensityCloud.size())
    print(filteredIntensityCloud.size())
    print(filteredIntensityCloud.size())
    print(filteredIntensityCloud.size())



    y_across = abs(abs(scalarFieldY.getMin()) - abs(scalarFieldY.getMax()))
    x_across = abs(abs(scalarFieldX.getMin()) - abs(scalarFieldX.getMax()))
    areatot = x_across * y_across
    ptsPermeterSquared = filteredIntensityCloud.size()/areatot

    print(y_across)
    print(x_across)
    print(areatot)
    print(ptsPermeterSquared)


    if ptsPermeterSquared < 7000 or filteredIntensityCloud.size() < 100000:
        badOutputDirectory = os.path.join(outputDirectory, "badFiles")
        if not os.path.exists(badOutputDirectory):
            os.makedirs(badOutputDirectory)
        badoutputFile = os.path.join(badOutputDirectory, "BAD" + filename[:-4] + ".las")
        #badexport = cc.SaveEntities([originalPointCloud], badoutputFile)
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
    #print(extractionResult)

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
    possibleCoralCloud = cc.MergeEntities([aboveSeaFloorCloud, belowIntensityThresholdCloud], createSFcloudIndex=True)
    possibleCoralCloud.setName("possible corals and other things above the sea floor")

    combinedCloud = cc.MergeEntities([possibleCoralCloud, groundPointsBase], createSFcloudIndex=True)
    combinedCloud.setName("everything combined")

    # Crop out unnecessary components
    potential_coral_dictionary = possibleCoralCloud.getScalarFieldDic()
    #print(potential_coral_dictionary)
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
    #print(coralExtractionResult)

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
        len(coralExtractionResult[1][lowerBound:])) + " total coral | Utilized Octree Level for coral segmentation: " + str(
        coralOctreeLevel))

    bigCoralPoints = cc.MergeEntities(coralExtractionResult[1][:lowerBound], createSFcloudIndex=True)

    if len(coralExtractionResult[1][:lowerBound]) > 1:
        bigCoralPoints.setName("Big Coral Points : V1 | " + str(
            len(coralExtractionResult[1][:lowerBound])) + " total coral | Utilized Octree Level for coral segmentation: " + str(
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
        coralPoints.getScalarField(coralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(highContrastScale)
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
            bigCoralPoints.setCurrentDisplayedScalarField(bigCoralPoints.getScalarFieldDic()['Original cloud index'])
        coralPoints.setCurrentDisplayedScalarField(coralPoints.getScalarFieldDic()['Original cloud index'])
        allCoralAndNonCoralPoints.setCurrentDisplayedScalarField(0)
        nonCoralPoints.setCurrentDisplayedScalarField(0)

        outputFile = os.path.join(outputDirectory, "CLEAN" + filename[:-4] + ".bin")

        if lowerBound > 1:
            exportResult = cc.SaveEntities(
                [originalPointCloud, cleanedPointCloud, fishPointsV1, groundPointsV1, groundPointsExtra, groundPointsBase,
                 aboveSeaFloorCloud, belowIntensityThresholdCloud, possibleCoralCloud, combinedCloud, croppedCloud,
                 allCoralAndNonCoralPoints, nonCoralPoints, bigCoralPoints, coralPoints, seafloorDEM], outputFile)
        else:
            exportResult = cc.SaveEntities(
                [originalPointCloud, cleanedPointCloud, fishPointsV1, groundPointsV1, groundPointsExtra, groundPointsBase,
                 aboveSeaFloorCloud, belowIntensityThresholdCloud, possibleCoralCloud, combinedCloud, croppedCloud,
                 allCoralAndNonCoralPoints, nonCoralPoints, coralPoints, seafloorDEM], outputFile)

    # smallOutputDirectory = os.path.join(outputDirectory, "smallClean")
    # if not os.path.exists(smallOutputDirectory):
    #     os.makedirs(smallOutputDirectory)
    if exportOption == "all" or exportOption == "small_output":
        coralPoints.setCurrentDisplayedScalarField(coralPoints.getScalarFieldDic()['Original cloud index'])
        if totalfish > 0:
            fishPointsV1.setCurrentDisplayedScalarField(fishPointsV1.getScalarFieldDic()['Original cloud index'])
        groundPointsBase.setCurrentDisplayedScalarField(groundPointsBase.getScalarFieldDic()['C2M signed distances'])

        coralPoints.getScalarField(coralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(highContrastScale)
        if totalfish > 0:
            fishPointsV1.getScalarField(fishPointsV1.getScalarFieldDic()['Original cloud index']).setColorScale(highContrastScale)
        groundPointsBase.getScalarField(groundPointsBase.getScalarFieldDic()['C2M signed distances']).setColorScale(highContrastScale)

        lasOutputDirectory = os.path.join(outputDirectory, "lasFiles")
        if not os.path.exists(lasOutputDirectory):
            os.makedirs(lasOutputDirectory)

        binOutputDirectory = os.path.join(outputDirectory, "binFiles")
        if not os.path.exists(binOutputDirectory):
            os.makedirs(binOutputDirectory)




        smallOutputFile = os.path.join(binOutputDirectory, "SMALL" + filename[:-4] + ".bin")
        smalllasOutputFile = os.path.join(lasOutputDirectory, "SMALL" + filename[:-4] + ".las")
        exportResult0 = cc.SaveEntities([originalPointCloud, fishPointsV1, groundPointsBase, coralPoints, seafloorDEM], smallOutputFile)
        exportlasResult0 = cc.SavePointCloud(groundPointsBase, smalllasOutputFile)








    # Decorate main function with Gooey for GUI-based execution
@Gooey
def main():
    """
    Main function to parse arguments and initiate processing.
    """
    parser = GooeyParser(description='Process and classify point clouds.')
    parser.add_argument('directory', type=str, help='Directory containing the LAS files.', widget='DirChooser')
    parser.add_argument('outputDirectory', type=str, help='Directory to save the processed files.', widget='DirChooser')
    parser.add_argument('--exportOption', type=str, choices=["all", "large_output", "small_output"], default='all',
                        help='Choose which output files to export (all, output, small_output). Default is all.')
    parser.add_argument('--processingOption', type=str, choices=["all", "data cleaning", "aligning"], default='all',
                        help='Choose which output files to export (all, output, small_output). Default is all.')

    args = parser.parse_args()

    directory = args.directory
    outputDirectory = args.outputDirectory
    exportOption = args.exportOption
    processingOption = args.processingOption

    fileList = os.listdir(directory)
    print("Files and directories in '", directory, "' :")
    print(fileList)

    # Process each LAS file in the directory
    if processingOption == "all" or processingOption == "data cleaning":
        for file in fileList:
            if file.endswith(".las"):
                print("Processing file:", file)
                cleanAndClassify(directory, file, outputDirectory, exportOption)


    # if processingOption == "all" or processingOption == "aligning":
    #     for file in fileList:
    #         if file.endswith(".las"):
    #             print("Processing file:", file)
    #             lasAlign(directory, file, outputDirectory, exportOption)



if __name__ == "__main__":
    main()



