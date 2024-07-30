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
from cleanCloud import cleanCloud


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


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class segmentCloud:
    def __init__(self, pcd_file,
                 output_dir,
                 dem_grid_step=.07,
                 pcd_above_seafloor_thresh=0.08,

                 coral_cell_size=0.02,
                 fish_cell_size=0.06,
                 min_comp_size=10,
                 verbose=False):
        # Add params wherever applicable, so others can adjust.
        # If you have reason to believe that some of these should NOT be changed,
        # that's totally fine that it's not a parameterized value and stays fixed.

        # Input PCD (las) file, checks
        self.pcd_file = pcd_file
        self.pcd_name = os.path.basename(pcd_file)
        self.pcd_basename = self.pcd_name.split(".")[0]
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

        self.exportOption = "small_output"
        self.originalPointCloud = None
        self.cleanedPointCloud = None

        self.extractionResult = None

        # TODO add short explanations for these
        # (consider changing names, as there is no V2?)
        # (seafloorPointsOriginal, seafloorPointsAssumed, seafloorPointsNoise)? IDK
        self.groundPointsV1 = None
        self.groundPointsBase = None
        self.groundPointsExtra = None

        self.belowIntensityThresholdCloud = None

        # TODO add short explanations for these
        self.fishPointsV1 = None
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
        # (should be lower if _, should be higher if _)
        self.fish_cell_size = fish_cell_size

        # Used in...
        # (should be lower if _, should be higher if _)
        self.coral_cell_size = coral_cell_size

        # Used in creating DEM
        # (should be lower if _, should be higher if _)
        self.dem_grid_step = dem_grid_step

        # Used in calculating the distance between...
        # (should be lower if _, should be higher if _)
        self.pcd_above_seafloor_thresh = pcd_above_seafloor_thresh

        # Used in calculating...
        # (should be lower if _, should be higher if _)
        self.min_comp_size = min_comp_size

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

    def extractPointCloudComponents(self):
        """
        This function extracts connected components from the original pcd; these components
        correspond to ... .... ...

        Additionally specifying a cell size, we can identify which points in the extracted
        components are likely fish.
        """
        pass

    # TODO
    # Consider breaking this up into two functions: one that is used to into components
    # (which assigns all the groundPoints) and records the self.extractionResults. The other
    # will using the extraction results and create the fishPoints
    def segmentFish(self):
        """
        This function segments fish by...
        """
        # Select octree level for fish segmentation
        octree = self.cleanedPointCloud.computeOctree(progressCb=None, autoAddChild=True)
        selectedOctreeLevel = octreeLevel(octree, self.fish_cell_size)

        if self.verbose:
            print(selectedOctreeLevel)
            print(self.cleanedPointCloud)

        # Extract connected components (fish points)
        self.extractionResult = cc.ExtractConnectedComponents(clouds=[self.cleanedPointCloud],
                                                              minComponentSize=self.min_comp_size,
                                                              octreeLevel=selectedOctreeLevel,
                                                              randomColors=True)
        # Subset extraction results
        smallComponents = [self.extractionResult[1][0]]
        allComponents = self.extractionResult[2] + smallComponents

        # TODO explain what these are
        # Merge entities to form ground points V1 (these are...)
        self.groundPointsV1 = cc.MergeEntities(allComponents, createSFcloudIndex=True)
        self.groundPointsV1.setName("Ground Points: V1")
        # Merge entities to form ground points base (these are...)
        self.groundPointsBase = cc.MergeEntities(smallComponents, createSFcloudIndex=True)
        self.groundPointsBase.setName("Ground Points: V1-base")
        # Merge entities to form ground points extra (these are...)
        self.groundPointsExtra = cc.MergeEntities(self.extractionResult[2], createSFcloudIndex=True)
        self.groundPointsExtra.setName("Ground Points: V1-extra")

        # Merge entities to form fish points V1 (these are...)
        self.fishPointsV1 = cc.MergeEntities(self.extractionResult[1][1:], createSFcloudIndex=True)
        # Extract the total amount of fish
        self.totalfish = len(self.extractionResult[1][1:])

        # TODO explain why
        # If the total number of fish is 0, then set the V1 to the original point cloud
        # because...
        if not self.totalfish:
            self.fishPointsV1 = self.originalPointCloud

        # Set the name
        self.fishPointsV1.setName(f"Fish Points: "
                                  f"V1 | {self.totalfish} total fish | "
                                  f"Utilized Octree Level for fish segmentation: {selectedOctreeLevel}")

        if self.verbose:
            print(f"Total Fish Found: {self.totalfish}")

    def createDEM(self):
        """
        Creates a DEM using the...
        """
        # Create Digital Elevation Model (DEM) of seafloor
        self.seafloorDEM = cc.RasterizeToMesh(self.groundPointsV1,
                                              outputRasterZ=True,
                                              gridStep=self.dem_grid_step,
                                              emptyCellFillStrategy=cc.EmptyCellFillOption.KRIGING,
                                              projectionType=cc.ProjectionType.PROJ_MINIMUM_VALUE,
                                              outputRasterSFs=True)
        # This does...
        cc.ccMesh.showSF(self.seafloorDEM, True)

    def computeC2M(self):
        """
        This function does...
        """
        # Calculate the "best" octree level
        bestOctreeLevel = cc.DistanceComputationTools.determineBestOctreeLevel(self.groundPointsBase,
                                                                               self.seafloorDEM)

        # Set the computation parameters before performing distance calculation
        computationParams = cc.Cloud2MeshDistancesComputationParams()
        computationParams.maxThreadCount = psutil.cpu_count()
        computationParams.octreeLevel = bestOctreeLevel
        computationParams.signedDistances = True

        # This does...
        cc.DistanceComputationTools.computeCloud2MeshDistances(pointCloud=self.groundPointsBase,
                                                               mesh=self.seafloorDEM,
                                                               params=computationParams)

    def potentialCoralCloud(self):
        """

        Returns:

        """
        # Create cloud with points greater than above sea floor (0.08 default)
        ground_points_base_dict = self.groundPointsBase.getScalarFieldDic()
        c2m_distances = self.groundPointsBase.getScalarField(ground_points_base_dict['C2M signed distances'])
        self.groundPointsBase.setCurrentScalarField(ground_points_base_dict['C2M signed distances'])

        # Filter for points above the sea floor
        above_seafloor_cloud = cc.filterBySFValue(
            self.pcd_above_seafloor_thresh,
            c2m_distances.getMax(),
            self.groundPointsBase
        )
        above_seafloor_cloud.setName(f"greater than {self.pcd_above_seafloor_thresh}m above sea floor")
        above_seafloor_dict = above_seafloor_cloud.getScalarFieldDic()
        above_seafloor_cloud.setCurrentScalarField(above_seafloor_dict['C2M signed distances'])
        above_seafloor_cloud.setCurrentDisplayedScalarField(above_seafloor_dict['C2M signed distances'])

        # Filter out highest intensity values
        intensity = self.groundPointsBase.getScalarField(ground_points_base_dict['Intensity'])
        self.groundPointsBase.setCurrentScalarField(ground_points_base_dict['Intensity'])

        below_intensity_cloud = cc.filterBySFValue(intensity.getMin(), 320, self.groundPointsBase)
        below_intensity_cloud.setName("Below 320 Intensity")
        below_intensity_dict = below_intensity_cloud.getScalarFieldDic()
        below_intensity_cloud.setCurrentScalarField(below_intensity_dict['Intensity'])
        below_intensity_cloud.setCurrentDisplayedScalarField(below_intensity_dict['Intensity'])
        self.belowIntensityThresholdCloud = below_intensity_cloud

        # Combine clouds
        entities = [above_seafloor_cloud, below_intensity_cloud]
        possible_coral_cloud = cc.MergeEntities(entities, createSFcloudIndex=True)
        possible_coral_cloud.setName("possible corals and other things above the sea floor")

        # Merge with ground points base
        combined_entities = [possible_coral_cloud, self.groundPointsBase]
        self.combinedCloud = cc.MergeEntities(combined_entities, createSFcloudIndex=True)
        self.combinedCloud.setName("everything combined")

    def cleanPotentialCoralCloud(self):
        """
        This function does...
        """
        # Crop out unnecessary components
        potential_coral_dictionary = self.possibleCoralCloud.getScalarFieldDic()
        self.yCoordSF = self.possibleCoralCloud.getScalarField(potential_coral_dictionary['Coord. Y'])
        self.xCoordSF = self.possibleCoralCloud.getScalarField(potential_coral_dictionary['Coord. X'])
        self.possibleCoralCloud.setCurrentScalarField(potential_coral_dictionary['Coord. Y'])

        factor = .14 * abs((self.yCoordSF.getMin()) - (self.yCoordSF.getMax()))
        distanceCross = abs((self.yCoordSF.getMin()) - (self.yCoordSF.getMax()))

        if self.verbose:
            print(distanceCross)
            print(factor)
            print(self.yCoordSF.getMin())
            print(self.yCoordSF.getMax())

        if distanceCross < 3:
            return

        self.croppedCloud = cc.filterBySFValue(self.yCoordSF.getMin() + factor,
                                               self.yCoordSF.getMax() - factor,
                                               self.possibleCoralCloud)

        cropped_cloud_dictionary = self.croppedCloud.getScalarFieldDic()
        self.croppedCloud.setCurrentScalarField(cropped_cloud_dictionary['Intensity'])
        self.croppedCloud.setCurrentDisplayedScalarField(cropped_cloud_dictionary['Intensity'])
        self.croppedCloud.setName("Cropped")

    def segmentCoral(self):
        """

        """
        # Select octree level for coral segmentation
        cropped_cloud_octree = self.croppedCloud.computeOctree(progressCb=None, autoAddChild=True)
        coralOctreeLevel = octreeLevel(cropped_cloud_octree, self.coral_cell_size)

        # Extract coral points
        coralExtractionResult = cc.ExtractConnectedComponents(clouds=[self.croppedCloud],
                                                              minComponentSize=self.min_comp_size,
                                                              octreeLevel=coralOctreeLevel,
                                                              randomColors=True,
                                                              maxNumberComponents=100000)

        self.nonCoralPoints = cc.MergeEntities(coralExtractionResult[2], createSFcloudIndex=True)
        self.nonCoralPoints.setName("Not Coral Points")

        if self.verbose:
            y_min, y_max = self.yCoordSF.getMin(), self.yCoordSF.getMax()
            x_min, x_max = self.xCoordSF.getMin(), self.xCoordSF.getMax()
            width = y_max - y_min
            length = x_max - x_min
            area = width * length

            print(f"Section is {y_min:.2f}m by {y_max:.2f}m or {width:.2f}m wide")
            print(f"Section is {x_min:.2f}m by {x_max:.2f}m or {length:.2f}m long")
            print(f"Area of section is {area:.2f}m²")

        self.combinedCoralPoints = coralExtractionResult[2] + coralExtractionResult[1]
        self.allCoralAndNonCoralPoints = cc.MergeEntities(self.combinedCoralPoints, createSFcloudIndex=True)
        self.allCoralAndNonCoralPoints.setName("All Coral + Non Coral points")

        self.lowerBound = filterLargeClouds(coralExtractionResult, 5000)

        if self.lowerBound == -1:
            return

        # Merge coral points
        coral_points = coralExtractionResult[1][self.lowerBound:]
        self.coralPoints = cc.MergeEntities(coral_points, createSFcloudIndex=True)
        self.coralPoints.setName(
            f"Coral Points : V1 | {len(coral_points)} total coral | "
            f"Utilized Octree Level for coral segmentation: {coralOctreeLevel}"
        )

        # Merge big coral points
        big_coral_points = coralExtractionResult[1][:self.lowerBound]
        self.bigCoralPoints = cc.MergeEntities(big_coral_points, createSFcloudIndex=True)

        if len(big_coral_points) > 1:
            self.bigCoralPoints.setName(
                f"Big Coral Points : V1 | {len(big_coral_points)} total coral | "
                f"Utilized Octree Level for coral segmentation: {coralOctreeLevel}"
            )

        print(str(len(coralExtractionResult[1])) + " total coral")

    def export(self):
        """
        This function does...
        """
        # ...
        colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
        defaultScale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)
        highContrastScale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HIGH_CONTRAST)

        # Set current scalar field for each point cloud
        for cloud in [
            self.cleanedPointCloud,
            self.groundPointsV1,
            self.fishPointsV1,
            self.groundPointsExtra,
            self.groundPointsBase
        ]:
            cloud.setCurrentScalarField(0)

        # Set color scale for each point cloud
        for cloud in [
            self.cleanedPointCloud,
            self.groundPointsV1,
            self.fishPointsV1,
            self.groundPointsExtra,
            self.groundPointsBase,
            self.belowIntensityThresholdCloud,
            self.possibleCoralCloud,
            self.combinedCloud,
            self.croppedCloud,

            self.allCoralAndNonCoralPoints,
            self.nonCoralPoints
        ]:
            cloud.getScalarField(0).setColorScale(defaultScale)

        if self.exportOption in ["all", "large_output"]:

            # Set current displayed scalar field for each point cloud
            for cloud in [
                self.cleanedPointCloud,
                self.groundPointsV1,
                self.fishPointsV1,
                self.groundPointsExtra,
                self.groundPointsBase,
                self.possibleCoralCloud,
                self.combinedCloud,

                self.allCoralAndNonCoralPoints,
                self.nonCoralPoints,
            ]:
                cloud.setCurrentDisplayedScalarField(0)

            if self.lowerBound > 1:
                index = self.bigCoralPoints.getScalarFieldDic()['Original cloud index']
                self.bigCoralPoints.getScalarField(index).setColorScale(highContrastScale)
                index = self.bigCoralPoints.getScalarFieldDic()['Original cloud index']
                self.bigCoralPoints.setCurrentDisplayedScalarField(index)

            index = self.coralPoints.getScalarFieldDic()['Original cloud index']
            self.coralPoints.getScalarField(index).setColorScale(highContrastScale)
            index = self.coralPoints.getScalarFieldDic()['Original cloud index']
            self.coralPoints.setCurrentDisplayedScalarField(index)

            # The final output file?...
            self.output_file = f"{self.output_dir}/CLEAN_{self.pcd_basename}.bin"

            # List of entities to export
            entities_to_export = [
                self.originalPointCloud,
                self.cleanedPointCloud,
                self.fishPointsV1,
                self.groundPointsV1,
                self.groundPointsExtra,
                self.groundPointsBase,
                self.aboveSeaFloorCloud,
                self.belowIntensityThresholdCloud,
                self.possibleCoralCloud,
                self.combinedCloud,
                self.croppedCloud,
                self.allCoralAndNonCoralPoints,
                self.nonCoralPoints,
                self.coralPoints,
                self.seafloorDEM
            ]

            # Add bigCoralPoints if lowerBound > 1
            if self.lowerBound > 1:
                entities_to_export.append(self.bigCoralPoints)

            # TODO is this needed?
            # Export entities
            exportResult = cc.SaveEntities(entities_to_export, self.output_file)

        if self.exportOption in ["all", "small_output"]:

            index = self.coralPoints.getScalarFieldDic()['Original cloud index']
            self.coralPoints.setCurrentDisplayedScalarField(index)

            if self.totalfish > 0:
                index = self.fishPointsV1.getScalarFieldDic()['Original cloud index']
                self.fishPointsV1.setCurrentDisplayedScalarField(index)

            index = self.groundPointsBase.getScalarFieldDic()['C2M signed distances']
            self.groundPointsBase.setCurrentDisplayedScalarField(index)

            index = self.coralPoints.getScalarFieldDic()['Original cloud index']
            self.coralPoints.getScalarField(index).setColorScale(highContrastScale)

            if self.totalfish > 0:
                index = self.fishPointsV1.getScalarFieldDic()['Original cloud index']
                self.fishPointsV1.getScalarField(index).setColorScale(highContrastScale)

            index = self.groundPointsBase.getScalarFieldDic()['C2M signed distances']
            self.groundPointsBase.getScalarField(index).setColorScale(highContrastScale)

            smallOutputFile = f"{self.binOutputDirectory}/SMALL_{self.pcd_basename}.bin"
            _ = [self.originalPointCloud, self.fishPointsV1, self.groundPointsBase, self.coralPoints, self.seafloorDEM]
            cc.SaveEntities(_, smallOutputFile)

            smalllasOutputFile = f"{self.lasOutputDirectory}/SMALL_{self.pcd_basename}.las"
            cc.SavePointCloud(self.groundPointsBase, smalllasOutputFile)

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
        self.segmentCoral()
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

    parser.add_argument('--output_dir', type=str, default="./output",
                        help='Directory to save the processed files.')

    parser.add_argument('--verbose', action='store_true',
                        help='Print to console.')

    args = parser.parse_args()

    try:
        # TODO add all parameterized arguments here
        # Create a segmentCloud instance
        cloud_segmentor = segmentCloud(pcd_file=args.pcd_file,
                                       output_dir=args.output_dir,
                                       verbose=args.verbose)
        # Segment the cloud
        cloud_segmentor.segment()
        print("Done.\n")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()