import os
import time
import argparse
import traceback

import numpy as np

import cloudComPy as cc
import cloudComPy.CSF

# import CloudCompare.cloudComPy as cc
# import CloudCompare.cloudComPy.CSF

from common import announce


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class cleanCloud:
    def __init__(self,
                 pcd_file,
                 output_dir,
                 intensity_thresh=100,
                 density_thresh=7000,
                 min_point_thresh=100000,
                 knn=6,
                 nSigma=10,
                 verbose=False,
                 export=True):

        # Input PCD (las) file, checks
        self.pcd_file = pcd_file
        self.pcd_name = os.path.basename(pcd_file)
        assert os.path.exists(self.pcd_file), "Error: PCD file doesn't exist"
        assert self.pcd_name.lower().endswith(".las"), "Error: PCD file is not a 'las' file"

        # Will store the cleaned file; if bad, left as blank.
        # Can be used by functions
        self.output_file = ""

        # Where all output goes
        self.output_dir = f"{output_dir}/cleaned/lasFiles"
        self.trash_dir = f"{output_dir}/cleaned/badFiles"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.trash_dir, exist_ok=True)

        # Various versions of PCDs
        self.originalPointCloud = None
        self.filteredIntensityCloud = None
        self.cleanedPointCloud = None

        self.SF_export = None

        # Threshold values for filtering
        self.intensity_thresh = intensity_thresh
        self.perimeter_thresh = density_thresh
        self.min_point_thresh = min_point_thresh

        # Params for SOR filter
        self.knn = knn
        self.nSigma = nSigma

        # Should the cleaned las Files be Exported
        self.export_result = export

        # Only print if True
        self.verbose = verbose

    def load_pcd(self):
        """
        Loads the provided PCD (LAS) file.
        """
        try:
            # Load the original point cloud
            self.originalPointCloud = cc.loadPointCloud(self.pcd_file)
            self.originalPointCloud.setName("Original Point Cloud")

        except Exception as e:
            print(traceback.print_exc())
            raise Exception(f"Error: Could not load PCD file.\n{e}")

    def clean(self):
        """
        Cleans the provided PCD (las) file using multiple filters;
        outputs the clean file in sub-directory. If considered 'dirty',
        saved to a separate trash directory.
        """
        t0 = time.time()

        # Load the PCD from file
        if self.originalPointCloud is None:
            raise Exception("Error: You must use load_pcd before cleaning")

        if self.verbose:
            announce(f"Cleaning {self.pcd_name}")

        # Export coordinate to scalar fields (leave in case needed later)
        self.SF_export = self.originalPointCloud.exportCoordToSF(True, True, True)

        # Get scalar fields
        scalarFieldX = self.originalPointCloud.getScalarField(3)
        scalarFieldY = self.originalPointCloud.getScalarField(4)
        scalarFieldZ = self.originalPointCloud.getScalarField(5)
        scalarFieldDictionary = self.originalPointCloud.getScalarFieldDic()

        if self.verbose:
            print(f"Export Result: \n {self.SF_export} \n")
            print(f"Scalar Field Dictionary: \n {scalarFieldDictionary} \n")

        # Calculate the intensity scalar field (shape), set to 0 by default
        intensityScalarField = self.originalPointCloud.getScalarField(scalarFieldDictionary['Intensity'])
        self.originalPointCloud.setCurrentScalarField(0)

        # Filter out lowest intensity values -> values below 100 (default)
        self.filteredIntensityCloud = cc.filterBySFValue(self.intensity_thresh,
                                                         intensityScalarField.getMax(),
                                                         self.originalPointCloud)

        # Calculate the shape of the point cloud
        y_across = abs(abs(scalarFieldY.getMin()) - abs(scalarFieldY.getMax()))
        x_across = abs(abs(scalarFieldX.getMin()) - abs(scalarFieldX.getMax()))
        area_total = x_across * y_across
        pts_per_squared = self.filteredIntensityCloud.size() / area_total

        if self.verbose:
            print(f"Y Across: {y_across}")
            print(f"X Across: {x_across}")
            print(f"Area Total: {area_total}")
            print(f"Points Perimeter (^2): {pts_per_squared}")

        if pts_per_squared < self.perimeter_thresh or self.filteredIntensityCloud.size() < self.min_point_thresh:
            # If the modified point cloud is too small, save it to trash folder
            trash_file = f"{self.trash_dir}/BAD_{self.pcd_name}"
            cc.SavePointCloud(self.originalPointCloud, trash_file)
            print(f"Warning: PCD file is considered bad, output as {os.path.basename(trash_file)}")
            return

        # Compute CSF (Conditional Sampling Framework) plugin for filtering lowest z values
        clouds = cc.CSF.computeCSF(self.filteredIntensityCloud)
        lowZPoints, highZPoints = clouds[0:2]

        # Remove statistical outliers using SOR filter, update cleaned point cloud
        # https://www.simulation.openfields.fr/documentation/CloudComPy/html/cloudSamplingTools.html#cloudComPy.CloudSamplingTools.sorFilter
        cloudReference = cc.CloudSamplingTools.sorFilter(knn=self.knn, nSigma=self.nSigma, cloud=highZPoints)
        self.cleanedPointCloud, res = highZPoints.partialClone(cloudReference)
        self.cleanedPointCloud.setName("Cleaned Point Cloud")

        if self.export_result:
            self.output_file = f"{self.output_dir}/CLEAN_{self.pcd_name}"
            cc.SavePointCloud(self.cleanedPointCloud, self.output_file)
            print(f"Exported {os.path.basename(self.output_file)}")

        print(f"Completed in {np.around(((time.time() - t0) / 60), 2)} minutes")


# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------

def main():
    """

    """
    parser = argparse.ArgumentParser(description='Process and classify point clouds.')

    parser.add_argument('--pcd_file', type=str, required=True,
                        help='Path to point cloud file (las).')

    parser.add_argument('--output_dir', type=str, default="./data/processed",
                        help='Directory to save the processed files.')

    parser.add_argument('--intensity_thresh', type=float, default=100,
                        help='Threshold for point perimeter squared.')

    parser.add_argument('--density_thresh', type=float, default=7000,
                        help='Threshold for points per meter squared.')

    parser.add_argument('--min_point_thresh', type=float, default=100000,
                        help='Minimum Points Threshold.')
    parser.add_argument('--knn', type=int, required=False,
                        default=6,
                        metavar='K Nearest Neighbors',
                        help='number of neighbors (must be an int)')

    parser.add_argument('--nSigma', type=float, required=False,
                        default=10,
                        help='The number of sigmas under which the points should be kept')

    parser.add_argument('--verbose', action='store_true',
                        help='Print information to console.')

    parser.add_argument('--export', default=True,
                        help='Should the cleaned point clouds be saved to their own folder.',
                        action='store_true')

    args = parser.parse_args()

    try:
        # Create a cleanCloud instance

        cloud_cleaner = cleanCloud(pcd_file=args.pcd_file,
                                   output_dir=args.output_dir,
                                   intensity_thresh=args.intensity_thresh,
                                   density_thresh=args.density_thresh,
                                   min_point_thresh=args.min_point_thresh,
                                   knn=args.knn,
                                   nSigma=args.nSigma,
                                   verbose=args.verbose,
                                   export=args.export)

        # Load point cloud
        cloud_cleaner.load_pcd()

        # Clean the cloud
        cloud_cleaner.clean()
        print("Done.")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()
