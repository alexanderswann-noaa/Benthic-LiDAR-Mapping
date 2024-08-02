import time
import traceback
import argparse
import os
import psutil
import pathlib

import numpy as np

import cloudComPy as cc
import cloudComPy.CSF

from common import announce


# -----------------------------------------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------------------------------------

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

        if listOfClouds[1][index].size() < maxPoints:
            return index


def emptyCellFill(fill):
    if fill == "KRIGING":
        return cc.EmptyCellFillOption.KRIGING
    elif fill == "LEAVE_EMPTY":
        return cc.EmptyCellFillOption.LEAVE_EMPTY
    elif fill == "FILL_MINIMUM_HEIGHT":
        return cc.EmptyCellFillOption.FILL_MINIMUM_HEIGHT
    elif fill == "FILL_MAXIMUM_HEIGHT":
        return cc.EmptyCellFillOption.FILL_MAXIMUM_HEIGHT
    elif fill == "FILL_CUSTOM_HEIGHT":
        return cc.EmptyCellFillOption.FILL_CUSTOM_HEIGHT
    elif fill == "FILL_AVERAGE_HEIGHT":
        return cc.EmptyCellFillOption.FILL_AVERAGE_HEIGHT
    elif fill == "INTERPOLATE_DELAUNAY":
        return cc.EmptyCellFillOption.INTERPOLATE_DELAUNAY


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class segmentCloud:
    def __init__(self,
                 pcd_file,
                 output_dir,
                 dem_grid_step=.07,
                 empty_cell_fill_option="KRIGING",
                 pcd_above_seafloor_thresh=0.08,
                 intensity_threshold=320,
                 coral_cell_size=0.02,
                 coral_min_comp_size=10,
                 max_coral_pts=5000,
                 fish_cell_size=0.06,
                 fish_min_comp_size=10,
                 exportOption="small_output",
                 verbose=True):

        # Input PCD (las) file, checks
        self.possible_coral_cloud = None
        self.pcd_file = pcd_file
        self.pcd_name = os.path.basename(pcd_file)
        self.pcd_basename = "".join(self.pcd_name.split(".")[:-1])

        assert os.path.exists(self.pcd_file), "Error: PCD file doesn't exist"
        assert self.pcd_name.lower().endswith(".las"), "Error: PCD file is not a 'las' file"

        self.output_file = ""

        # Where all output goes
        self.output_dir = f"{output_dir}/segmented"
        self.lasOutputDirectory = f"{self.output_dir}/lasFiles"
        self.binOutputDirectory = f"{self.output_dir}/binFiles"

        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.lasOutputDirectory, exist_ok=True)
        os.makedirs(self.binOutputDirectory, exist_ok=True)

        self.originalPointCloud = None
        self.cleanedPointCloud = None

        self.extractionResult = None

        # TODO add short explanations for these

        self.groundPoints = None
        self.unsegmentedPoints = None

        self.belowIntensityThresholdCloud = None

        # TODO add short explanations for these
        self.fishPoints = None
        self.totalfish = None

        # Represents the...
        self.seafloorDEM = None

        self.combinedCloud = None
        self.possibleCoralCloud = None
        self.yCoordSF = None
        self.xCoordSF = None

        self.croppedCloud = None
        self.aboveSeaFloorCloud = None

        self.nonCoralPoints = None
        self.coralPoints = None
        self.bigCoralPoints = None

        # TODO add short explanations for these
        # Used in separating fish
        # (should be lower if you want more fish, should be higher if you want fewer fish)
        # Setting this number much lower than the default could result in segmenting corals as well as fish
        self.fish_cell_size = fish_cell_size

        # Used in separating coral
        # (should be lower if you want smaller corals, should be higher if you want larger corals)
        # Setting this number much lower than the default could result in segmenting non corals
        self.coral_cell_size = coral_cell_size

        # Used in creating DEM
        # (should be lower if you want a more fine DEM, should be higher if you want a more coarse DEM)
        self.dem_grid_step = dem_grid_step
        self.empty_cell_fill_option = empty_cell_fill_option
        print(self.empty_cell_fill_option)

        # Used in calculating the distance between
        # (should be lower if _, should be higher if _)
        self.pcd_above_seafloor_thresh = pcd_above_seafloor_thresh

        # Used in calculating...
        # (should be lower if _, should be higher if _)
        self.coral_min_comp_size = coral_min_comp_size

        # Used in calculating...
        # (should be lower if _, should be higher if _)
        self.fish_min_comp_size = fish_min_comp_size

        # Used in calculating...
        # (should be lower if _, should be higher if _)
        self.max_coral_pts = max_coral_pts

        self.exportOption = exportOption

        self.intensity_threshold = intensity_threshold

        self.verbose = verbose

    def load_pcd(self, pcd=None):
        """
        Loads the provided PCD (LAS) file provided; user can provide an opened
        CC PCD if it's already stored in memory.
        """
        if pcd is None:
            # Load the original point cloud from file
            self.originalPointCloud = cc.loadPointCloud(self.pcd_file)
            self.originalPointCloud.setName("Original Point Cloud")
            self.cleanedPointCloud = self.originalPointCloud
        else:
            self.originalPointCloud = pcd.originalPointCloud
            self.cleanedPointCloud = pcd.cleanedPointCloud

        if None in [self.originalPointCloud, self.cleanedPointCloud]:
            raise Exception("Error: PCD file is empty")

    def segmentFish(self):
        """
        This function segments fish by...


        ExtractConnectedComponents segments the clouds in smaller parts separated by a minimum distance. Each part is
        a connected component (i.e. a set of ‘connected’ points). CloudCompare uses a 3D grid to extract the
        connected components. This grid is deduced from the octree structure. By selecting on octree level you define
        how small is the minimum gap between two components. If n is the octree level and d the dimension of the
        clouds (Bounding box side), the gap is roughly d/2**n.

        https://www.simulation.openfields.fr/documentation/CloudComPy/html/cloudComPy.html#cloudComPy.ExtractConnectedComponents

        """
        # Select octree level for fish segmentation
        octree = self.cleanedPointCloud.computeOctree(progressCb=None, autoAddChild=True)
        selectedOctreeLevel = octreeLevel(octree, self.fish_cell_size)

        if self.verbose:
            print(selectedOctreeLevel)
            print(self.cleanedPointCloud)

        # Extract connected components (fish points)

        self.extractionResult = cc.ExtractConnectedComponents(clouds=[self.cleanedPointCloud],
                                                              minComponentSize=self.fish_min_comp_size,
                                                              octreeLevel=selectedOctreeLevel,
                                                              randomColors=True)
        # Subset extraction results
        smallComponents = [self.extractionResult[1][0]]
        allComponents = self.extractionResult[2] + smallComponents

        # TODO explain what these are
        # Merge entities to form ground points V1 (these are...)

        # Merge entities to form the points that make up the seafloor
        self.groundPoints = cc.MergeEntities(smallComponents, createSFcloudIndex=True)
        self.groundPoints.setName("Ground Points")

        # Merge entities to form the points that are not a part of the seafloor and are not fish
        self.unsegmentedPoints = cc.MergeEntities(self.extractionResult[2], createSFcloudIndex=True)
        self.unsegmentedPoints.setName("Not Fish or Part of Seafloor")

        # Merge entities to form the points that make up the fish
        self.fishPoints = cc.MergeEntities(self.extractionResult[1][1:], createSFcloudIndex=True)

        # Extract the total amount of fish
        self.totalfish = len(self.extractionResult[1][1:])

        # If the total number of fish is 0, then set the V1 to the original point cloud If there are no fish the code
        # will error out later so if there are no fish we se the fish points to the original point cloud
        if self.totalfish < 1:
            self.fishPoints = self.originalPointCloud

        # Set the name
        self.fishPoints.setName(f"Fish Points: "
                                f"V1 | {self.totalfish} total fish | "
                                f"Utilized Octree Level for fish segmentation: {selectedOctreeLevel}")

        #Print out the total number of fish
        if self.verbose:
            print(f"Total Fish Found: {self.totalfish}")

        self.extractionResult = None
        allComponents = None
        smallComponents = None

    def createDEM(self):
        """
        Creates a DEM using the seafloor points
        """
        # Create Digital Elevation Model (DEM) of seafloor

        self.seafloorDEM = cc.RasterizeToMesh(self.groundPoints,
                                              gridStep=self.dem_grid_step,
                                              emptyCellFillStrategy=emptyCellFill(self.empty_cell_fill_option),
                                              projectionType=cc.ProjectionType.PROJ_MINIMUM_VALUE)

        # Make the scalar fields visible so that it displays correctly when opened in cloud compare
        cc.ccMesh.showSF(self.seafloorDEM, True)

    def computeC2M(self):
        """
        This function computes the distance in Meters from the DEM seafloor point cloud
        """
        # Calculate the "best" octree level
        bestOctreeLevel = cc.DistanceComputationTools.determineBestOctreeLevel(self.groundPoints,
                                                                               self.seafloorDEM)

        # Set the computation parameters before performing distance calculation
        computationParams = cc.Cloud2MeshDistancesComputationParams()
        computationParams.maxThreadCount = psutil.cpu_count()
        computationParams.octreeLevel = bestOctreeLevel
        computationParams.signedDistances = True

        # Compute the distance in Meters from the DEM seafloor point cloud
        cc.DistanceComputationTools.computeCloud2MeshDistances(pointCloud=self.groundPoints,
                                                               mesh=self.seafloorDEM,
                                                               params=computationParams)

    def potentialCoralCloud(self):
        """
        This function creates two separate point clouds: one with all the points that are over specified height off
        of the sea floor the other with all the points that are below a specified intensity value. These two point
        clouds are combined and called the potential coral cloud. This is because when looking at the testing data it
        looked like most of the points that were corals fell into one of these two categories.

        """

        # Create cloud with points greater than the selected amount above the sea floor default .08 meters
        ground_points_base_dictionary = self.groundPoints.getScalarFieldDic()
        c2mDistancesSF = self.groundPoints.getScalarField(ground_points_base_dictionary['C2M signed distances'])
        self.groundPoints.setCurrentScalarField(ground_points_base_dictionary['C2M signed distances'])

        self.aboveSeaFloorCloud = cc.filterBySFValue(self.pcd_above_seafloor_thresh, c2mDistancesSF.getMax(),
                                                     self.groundPoints)
        self.aboveSeaFloorCloud.setName("greater than " + str(self.pcd_above_seafloor_thresh) + "m above sea floor")

        above_sea_floor_dictionary = self.aboveSeaFloorCloud.getScalarFieldDic()
        c2mDistancesSF2 = self.aboveSeaFloorCloud.getScalarField(above_sea_floor_dictionary['C2M signed distances'])
        self.aboveSeaFloorCloud.setCurrentScalarField(above_sea_floor_dictionary['C2M signed distances'])
        self.aboveSeaFloorCloud.setCurrentDisplayedScalarField(above_sea_floor_dictionary['C2M signed distances'])

        # Filter out the highest intensity values
        intensitySF2 = self.groundPoints.getScalarField(ground_points_base_dictionary['Intensity'])
        self.groundPoints.setCurrentScalarField(ground_points_base_dictionary['Intensity'])

        self.belowIntensityThresholdCloud = cc.filterBySFValue(intensitySF2.getMin(), self.intensity_threshold,
                                                               self.groundPoints)
        self.belowIntensityThresholdCloud.setName("Below " + str(self.intensity_threshold) + " Intensity")

        below_intensity_threshold_dictionary = self.belowIntensityThresholdCloud.getScalarFieldDic()
        intensitySF3 = self.belowIntensityThresholdCloud.getScalarField(
            below_intensity_threshold_dictionary['Intensity'])
        self.belowIntensityThresholdCloud.setCurrentScalarField(below_intensity_threshold_dictionary['Intensity'])
        self.belowIntensityThresholdCloud.setCurrentDisplayedScalarField(
            below_intensity_threshold_dictionary['Intensity'])

        # Combine clouds
        self.possibleCoralCloud = cc.MergeEntities([self.aboveSeaFloorCloud, self.belowIntensityThresholdCloud],
                                                   createSFcloudIndex=True)
        self.possibleCoralCloud.setName("possible corals and other things above the sea floor")

        self.combinedCloud = cc.MergeEntities([self.possibleCoralCloud, self.groundPoints], createSFcloudIndex=True)
        self.combinedCloud.setName("everything combined")

    def cleanPotentialCoralCloud(self):
        """
        This function takes the point cloud from the previous step and cleans it. The data along the edge of any
        particular track contains very low quality and also low intensity points. When segmentation occurs many of
        these points get labeled as large corals, which is not the case. This step of the process attempts to trim
        off those bad points, but it does not work very well at the moment. Ideally these points along with other
        points on the outer edge could be filtered out if we had a scan angle for each point.
        """

        potential_coral_dictionary = self.possibleCoralCloud.getScalarFieldDic()

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

        self.croppedCloud = cc.filterBySFValue(self.yCoordSF.getMin() + factor, self.yCoordSF.getMax() - factor,
                                               self.possibleCoralCloud)
        self.croppedCloud.setName("Cropped")

        cropped_cloud_dictionary = self.croppedCloud.getScalarFieldDic()
        if self.verbose:
            print(cropped_cloud_dictionary)
        self.croppedCloud.setCurrentScalarField(cropped_cloud_dictionary['Intensity'])
        self.croppedCloud.setCurrentDisplayedScalarField(cropped_cloud_dictionary['Intensity'])

    def segCoral(self):
        # Select octree level for coral segmentation
        cropped_cloud_octree = self.croppedCloud.computeOctree(progressCb=None, autoAddChild=True)
        coralOctreeLevel = octreeLevel(cropped_cloud_octree, self.coral_cell_size)

        # Extract coral points
        coralExtractionResult = cc.ExtractConnectedComponents(clouds=[self.croppedCloud],
                                                              minComponentSize=self.coral_min_comp_size,
                                                              octreeLevel=coralOctreeLevel,
                                                              randomColors=True,
                                                              maxNumberComponents=100000)

        self.nonCoralPoints = cc.MergeEntities(coralExtractionResult[2], createSFcloudIndex=True)
        self.nonCoralPoints.setName("Not Coral Points")

        print("Section is " + str(self.yCoordSF.getMin()) + "m by " + str(self.yCoordSF.getMax()) + "m or " + str(
            self.yCoordSF.getMax() - self.yCoordSF.getMin()) + "m wide")

        print("Section is " + str(self.xCoordSF.getMin()) + "m by " + str(self.xCoordSF.getMax()) + "m or " + str(
            self.xCoordSF.getMax() - self.xCoordSF.getMin()) + "m long")

        print("Area of section is " + str(
            (self.xCoordSF.getMax() - self.xCoordSF.getMin()) * (
                    self.yCoordSF.getMax() - self.yCoordSF.getMin())) + "m^2")

        self.combinedCoralPoints = coralExtractionResult[2] + coralExtractionResult[1]
        self.allCoralAndNonCoralPoints = cc.MergeEntities(self.combinedCoralPoints, createSFcloudIndex=True)
        self.allCoralAndNonCoralPoints.setName("All Coral + Non Coral points")

        self.lowerBound = filterLargeClouds(coralExtractionResult, self.max_coral_pts)

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

        if self.verbose:
            print(str(len(coralExtractionResult[1])) + " total coral")

        coralExtractionResult = None
        combinedCoralPoints = None

    def export(self):
        # Export clouds and meshes

        self.outputDirectory = self.output_dir

        self.cleanedPointCloud.setCurrentScalarField(0)
        self.fishPoints.setCurrentScalarField(0)
        self.unsegmentedPoints.setCurrentScalarField(0)
        self.groundPoints.setCurrentScalarField(0)

        scalarFieldDictionary = self.groundPoints.getScalarFieldDic()
        print(scalarFieldDictionary)

        colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
        defaultScale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)
        highContrastScale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HIGH_CONTRAST)

        self.cleanedPointCloud.getScalarField(0).setColorScale(defaultScale)
        self.fishPoints.getScalarField(0).setColorScale(defaultScale)
        self.unsegmentedPoints.getScalarField(0).setColorScale(defaultScale)
        self.groundPoints.getScalarField(0).setColorScale(defaultScale)
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
            self.fishPoints.setCurrentDisplayedScalarField(0)
            self.unsegmentedPoints.setCurrentDisplayedScalarField(0)
            self.groundPoints.setCurrentDisplayedScalarField(0)
            self.possibleCoralCloud.setCurrentDisplayedScalarField(0)
            self.combinedCloud.setCurrentDisplayedScalarField(0)

            if self.lowerBound > 1:
                self.bigCoralPoints.setCurrentDisplayedScalarField(
                    self.bigCoralPoints.getScalarFieldDic()['Original cloud index'])
            self.coralPoints.setCurrentDisplayedScalarField(
                self.coralPoints.getScalarFieldDic()['Original cloud index'])
            self.allCoralAndNonCoralPoints.setCurrentDisplayedScalarField(0)
            self.nonCoralPoints.setCurrentDisplayedScalarField(0)

            lasOutputDirectory = os.path.join(self.outputDirectory, "lasFiles")
            if not os.path.exists(lasOutputDirectory):
                os.makedirs(lasOutputDirectory)

            binOutputDirectory = os.path.join(self.outputDirectory, "binFiles")
            if not os.path.exists(binOutputDirectory):
                os.makedirs(binOutputDirectory)

            outputFile = f"{self.binOutputDirectory}/LARGE_{self.pcd_basename}.bin"

            if self.lowerBound > 1:

                entities_to_export = [self.originalPointCloud,
                                      self.cleanedPointCloud,
                                      self.fishPoints,
                                      self.unsegmentedPoints,
                                      self.groundPoints,
                                      self.aboveSeaFloorCloud,
                                      self.belowIntensityThresholdCloud,
                                      self.possibleCoralCloud,
                                      self.combinedCloud,
                                      self.croppedCloud,
                                      self.allCoralAndNonCoralPoints,
                                      self.nonCoralPoints,
                                      self.bigCoralPoints,
                                      self.coralPoints,
                                      self.seafloorDEM]
                for cloud in entities_to_export:
                    print(cloud.getName())
                    print(cloud.size())

                large_export_result = cc.SaveEntities(entities_to_export, outputFile)
            else:
                print("hello6")
                large_export_result = cc.SaveEntities(
                    [self.originalPointCloud, self.cleanedPointCloud, self.fishPoints,
                     self.unsegmentedPoints,
                     self.groundPoints,
                     self.aboveSeaFloorCloud, self.belowIntensityThresholdCloud, self.possibleCoralCloud,
                     self.combinedCloud, self.croppedCloud,
                     self.allCoralAndNonCoralPoints, self.nonCoralPoints, self.coralPoints, self.seafloorDEM],
                    outputFile)

        if self.exportOption == "all" or self.exportOption == "small_output":
            self.coralPoints.setCurrentDisplayedScalarField(
                self.coralPoints.getScalarFieldDic()['Original cloud index'])
            if self.totalfish > 0:
                self.fishPoints.setCurrentDisplayedScalarField(
                    self.fishPoints.getScalarFieldDic()['Original cloud index'])
            self.groundPoints.setCurrentDisplayedScalarField(
                self.groundPoints.getScalarFieldDic()['C2M signed distances'])

            self.coralPoints.getScalarField(self.coralPoints.getScalarFieldDic()['Original cloud index']).setColorScale(
                highContrastScale)
            if self.totalfish > 0:
                self.fishPoints.getScalarField(
                    self.fishPoints.getScalarFieldDic()['Original cloud index']).setColorScale(
                    highContrastScale)
            self.groundPoints.getScalarField(
                self.groundPoints.getScalarFieldDic()['C2M signed distances']).setColorScale(
                highContrastScale)

            lasOutputDirectory = os.path.join(self.outputDirectory, "lasFiles")
            if not os.path.exists(lasOutputDirectory):
                os.makedirs(lasOutputDirectory)

            binOutputDirectory = os.path.join(self.outputDirectory, "binFiles")
            if not os.path.exists(binOutputDirectory):
                os.makedirs(binOutputDirectory)

            smallOutputFile = f"{self.binOutputDirectory}/SMALL_{self.pcd_basename}.bin"

            smalllasOutputFile = f"{self.lasOutputDirectory}/SMALL_{self.pcd_basename}.las"

            exportResult0 = cc.SaveEntities(
                [self.originalPointCloud, self.fishPoints, self.groundPoints, self.coralPoints, self.seafloorDEM],
                smallOutputFile)
            exportlasResult0 = cc.SavePointCloud(self.groundPoints, smalllasOutputFile)


    def segment(self):
        """
        Segments the provided PCD (las) file using multiple techniques.
        """
        t0 = time.time()

        if self.originalPointCloud is None:
            raise Exception("Error: You must use load_pcd before segmenting")

        self.segmentFish()

        self.createDEM()

        self.computeC2M()

        self.potentialCoralCloud()

        self.cleanPotentialCoralCloud()

        self.segCoral()
        self.export()

        print(f"Completed in {np.around(((time.time() - t0) / 60), 2)} minutes")


# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------

def main():
    """

    """
    # TODO add all parameterized arguments here
    parser = argparse.ArgumentParser(description='Segment point clouds.')

    parser.add_argument('--pcd_file', type=str, required=True,
                        help='Path to point cloud file (las).')

    parser.add_argument('--output_dir', type=str, default="./data/processed",
                        help='Directory to save the processed files.')

    # 'Optional Arguments for Segmenting Corals',

    parser.add_argument('--pcd_above_seafloor_thresh', type=float, required=False,
                        default=0.08,
                        help='Points above this Value will be added to the Potential Coral Cloud that is used later to identify corals.')

    parser.add_argument('--intensity_threshold', type=float, required=False,
                        default=320,
                        help='Points below this intensity value will be added to the Potential Coral Cloud that is used later to identify corals.')

    parser.add_argument('--coral_cell_size', type=float, required=False,
                        default=0.02,
                        help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Corals.')
    parser.add_argument('--coral_min_comp_size', type=int, required=False,
                        default=10,
                        help='The smallest number of grouped points that will be classified as coral.')

    parser.add_argument('--max_coral_pts', type=float, required=False,
                        default=5000,
                        help='The largest number of grouped points that will be classified as coral.')

    # 'Optional Arguments for Segmenting Fish'

    parser.add_argument('--fish_cell_size', type=float, required=False,
                        default=0.06,
                        help='The Maximum Value of the Cell size for the Octree Level that will be used to segment Fish.')

    parser.add_argument('--fish_min_comp_size', type=int, required=False,
                        default=10,
                        help='The smallest number of grouped points that will be classified as fish.')

    # 'Optional Arguments for Creating DEM'

    parser.add_argument('--dem_grid_step', type=float, required=False,
                        default=.07,
                        help='The Grid step used to create the DEM.')

    parser.add_argument('--empty_cell_fill_option', type=str, required=False,
                        default="KRIGING",
                        help='How should the values for empty spaces be filled. OPTIONS: "LEAVE_EMPTY", "FILL_MINIMUM_HEIGHT","FILL_MAXIMUM_HEIGHT","FILL_CUSTOM_HEIGHT","FILL_AVERAGE_HEIGHT","INTERPOLATE_DELAUNAY","KRIGING"')

    # 'Other Optional Arguments'

    parser.add_argument('--exportOption', type=str, required=False,
                        default="small_output",
                        help='What should be outputed? Options are "small_output", "large_output", "all" ')
    parser.add_argument('--verbose', default=True,
                        help='Should Information be Printed to the Console.',
                        action='store_true')

    args = parser.parse_args()

    try:
        # TODO add all parameterized arguments here
        # Create a segmentCloud instance
        cloud_segmentor = segmentCloud(pcd_file=args.pcd_file,
                                       output_dir=args.output_dir,
                                       dem_grid_step=args.dem_grid_step,
                                       empty_cell_fill_option=args.empty_cell_fill_option,
                                       pcd_above_seafloor_thresh=args.pcd_above_seafloor_thresh,
                                       intensity_threshold=args.intensity_threshold,
                                       coral_cell_size=args.coral_cell_size,
                                       fish_cell_size=args.fish_cell_size,
                                       fish_min_comp_size=args.fish_min_comp_size,
                                       coral_min_comp_size=args.coral_min_comp_size,
                                       max_coral_pts=args.max_coral_pts,
                                       exportOption=args.exportOption,
                                       verbose=args.verbose)

        # Load the cloud
        cloud_segmentor.load_pcd()

        # Segment the cloud
        cloud_segmentor.segment()

        print("Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()
