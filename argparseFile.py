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

# os.environ["_CCTRACE_"]="ON" # only if you want C++ debug traces

#from gendata import getSampleCloud, getSampleCloud2, dataDir, dataExtDir, isCoordEqual
import CloudCompare.cloudComPy as cc
import CloudCompare.cloudComPy.CSF


def octreeLevel(octree, cellSize):
    for elem in range(11, 6, -1):
        if octree.getCellSize(elem) > cellSize:
            print(str(octree.getCellSize(elem)) + " : " + str(elem))
            print(str(octree.getCellSize(elem + 1)) + " : " + str(elem + 1))
            print(str(octree.getCellSize(elem - 1)) + " : " + str(elem - 1))
            return elem


def filterLargeClouds(listOfClouds, maxPts):
    for i in range(40):
        if listOfClouds[1][i].size() < maxPts:
            return i


def clean_classify(path, filename, output_dir):
    cloud1 = cc.loadPointCloud(os.path.join(path, filename))
    cloud1.setName("Original Point Cloud")

    res = cloud1.exportCoordToSF(True, True, True)
    sfx = cloud1.getScalarField(3)
    sfy = cloud1.getScalarField(4)
    sfz = cloud1.getScalarField(5)

    dic = cloud1.getScalarFieldDic()
    print(dic)

    sf = cloud1.getScalarField(dic['Intensity'])

    # filter out lowest intensity values---begin
    cloud1.setCurrentScalarField(0)

    cloud2 = cc.filterBySFValue(100, sf.getMax(), cloud1)
    # filter out lowest intensity values---end

    # filter out lowest z values with csh plugin --- begin

    clouds = cc.CSF.computeCSF(cloud2)

    low_points = clouds[0]
    new_cloud = clouds[1]
    # filter out lowest z values with csh plugin---end

    # remove-statistical-outliers---begin
    cloudRef = cc.CloudSamplingTools.sorFilter(knn=6, nSigma=10, cloud=new_cloud)
    (cloud3, res) = new_cloud.partialClone(cloudRef)
    cloud3.setName("Cleaned Point Cloud")
    # remove-statistical-outliers---end

    ## select-octree-lvl-for - fish--begin
    octree = cloud3.computeOctree(progressCb=None, autoAddChild=True)
    level = octreeLevel(octree, .06)
    ## select-octree-lvl-for-fish--end

    # ---extractFish-begin
    res1 = cc.ExtractConnectedComponents(clouds=[cloud3],
                                         minComponentSize=10,
                                         octreeLevel=level,
                                         randomColors=True)
    print(res1)

    res4 = [res1[1][0]]
    res3 = res1[2] + res4

    cloud4 = cc.MergeEntities(res3, createSFcloudIndex=True)
    cloud4.setName("Ground Points: V1")

    cloud7 = cc.MergeEntities(res4, createSFcloudIndex=True)
    cloud7.setName("Ground Points: V1-base")

    cloud6 = cc.MergeEntities(res1[2], createSFcloudIndex=True)
    cloud6.setName("Ground Points: V1-extra")

    cloud5 = cc.MergeEntities(res1[1][1:], createSFcloudIndex=True)
    cloud5.setName("Fish Points : V1 | " + str(
        len(res1[1][1:])) + " total fish | Utilized Octree Level for fish segmentation: " + str(level))

    print(str(len(res1[1][1:])) + " total fish")

    res1 = None
    res3 = None
    res4 = None
    # ---extractFish-end

    # --- create DEM --- begin
    seafloorDEM = cc.RasterizeToMesh(cloud4,
                                     outputRasterZ=True,
                                     gridStep=.07,
                                     emptyCellFillStrategy=cc.EmptyCellFillOption.KRIGING,
                                     projectionType=cc.ProjectionType.PROJ_MINIMUM_VALUE,
                                     outputRasterSFs=True)
    cc.ccMesh.showSF(seafloorDEM, True)
    # --- create DEM --- end

    # --- compute cloud to mesh distance ---start
    nbCpu = psutil.cpu_count()
    bestOctreeLevel = cc.DistanceComputationTools.determineBestOctreeLevel(cloud7, seafloorDEM)
    params = cc.Cloud2MeshDistancesComputationParams()
    params.signedDistances = True
    params.maxThreadCount = nbCpu
    params.octreeLevel = bestOctreeLevel

    cc.DistanceComputationTools.computeCloud2MeshDistances(pointCloud=cloud7, mesh=seafloorDEM, params=params)
    # ---- compute cloud to mesh distance --- end

    # --- create cloud with all points greater than .08m above sea floor ---begin
    dic2 = cloud7.getScalarFieldDic()
    print(dic2)

    sf3 = cloud7.getScalarField(dic2['C2M signed distances'])
    cloud7.setCurrentScalarField(dic2['C2M signed distances'])

    cloud8 = cc.filterBySFValue(.08, sf3.getMax(), cloud7)
    cloud8.setName("greater than .08m above sea floor")

    dic3 = cloud8.getScalarFieldDic()
    sf4 = cloud8.getScalarField(dic3['C2M signed distances'])
    cloud8.setCurrentScalarField(dic3['C2M signed distances'])
    cloud8.setCurrentDisplayedScalarField(dic3['C2M signed distances'])
    # --- create cloud with all points greater than .08m above sea floor ---end

    # filter out highest intensity values---begin
    sf2 = cloud7.getScalarField(dic2['Intensity'])
    cloud7.setCurrentScalarField(dic2['Intensity'])

    cloud9 = cc.filterBySFValue(sf2.getMin(), 320, cloud7)
    cloud9.setName("Below 320 Intensity")
    dic4 = cloud9.getScalarFieldDic()

    sf5 = cloud9.getScalarField(dic4['Intensity'])
    cloud9.setCurrentScalarField(dic4['Intensity'])
    cloud9.setCurrentDisplayedScalarField(dic4['Intensity'])
    # filter out highest intensity values---end

    ## combine the two previously created clouds -- start
    cloud10 = cc.MergeEntities([cloud8, cloud9], createSFcloudIndex=True)
    cloud10.setName("possible corals and other things above the sea floor")
    ## combine the two previously created clouds -- end

    ## combine the two previously created clouds -- start
    cloud11 = cc.MergeEntities([cloud10, cloud7], createSFcloudIndex=True)
    cloud11.setName("everything combined")
    ## combine the two previously created clouds -- end

    ## crop out the messy stuff -- start
    dic5 = cloud10.getScalarFieldDic()
    sf6 = cloud10.getScalarField(dic5['Coord. Y'])
    sf7 = cloud10.getScalarField(dic5['Coord. X'])
    cloud10.setCurrentScalarField(dic5['Coord. Y'])

    cloud12 = cc.filterBySFValue(sf6.getMin() + .7, sf6.getMax() - .7, cloud10)
    cloud12.setName("Cropped")
    dic6 = cloud12.getScalarFieldDic()

    cloud12.setCurrentScalarField(dic6['Intensity'])
    cloud12.setCurrentDisplayedScalarField(dic6['Intensity'])
    ## crop out the messy stuff --end

    ## select-octree-lvl-for - coral--begin
    octree2 = cloud12.computeOctree(progressCb=None, autoAddChild=True)
    level2 = octreeLevel(octree2, .02)
    ## select-octree-lvl-for-coral--end

    # ---extractcoral-begin
    res12 = cc.ExtractConnectedComponents(clouds=[cloud12],
                                          minComponentSize=10,
                                          octreeLevel=level2,
                                          randomColors=True,
                                          maxNumberComponents=100000)
    print(res12)

    print(str(len(res12[1])) + " total coral")

    cloud72 = cc.MergeEntities(res12[2], createSFcloudIndex=True)
    cloud72.setName("Not Coral Points")

    print("Section is " + str(sf6.getMin()) + "m by " + str(sf6.getMax()) + "m or " + str(
        sf6.getMax() - sf6.getMin()) + "m wide")

    print("Section is " + str(sf7.getMin()) + "m by " + str(sf7.getMax()) + "m or " + str(
        sf7.getMax() - sf7.getMin()) + "m long")

    print("Area of section is " + str((sf7.getMax() - sf7.getMin()) * (sf6.getMax() - sf6.getMin())) + "m^2")

    res43 = res12[2] + res12[1]
    cloud62 = cc.MergeEntities(res43, createSFcloudIndex=True)
    cloud62.setName("All Coral + Non Coral points")

    lowerBound = filterLargeClouds(res12, 5000)

    cloud52 = cc.MergeEntities(res12[1][lowerBound:], createSFcloudIndex=True)
    cloud52.setName("Coral Points : V1 | " + str(
        len(res12[1][lowerBound:])) + " total coral | Utilized Octree Level for coral segmentation: " + str(level2))

    cloud42 = cc.MergeEntities(res12[1][:lowerBound], createSFcloudIndex=True)

    if len(res12[1][:lowerBound]) > 1:
        cloud42.setName("Big Coral Points : V1 | " + str(
            len(res12[1][:lowerBound])) + " total coral | Utilized Octree Level for coral segmentation: " + str(level2))

    print(str(len(res12[1])) + " total coral")

    res12 = None
    res43 = None
    # ---extractcoral-end

    # export clouds and meshes
    final_cloud = cloud2
    cloud3.setCurrentScalarField(0)
    cloud4.setCurrentScalarField(0)
    cloud5.setCurrentScalarField(0)
    cloud6.setCurrentScalarField(0)
    cloud7.setCurrentScalarField(0)

    dic = cloud7.getScalarFieldDic()
    print(dic)

    colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
    scale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)
    scale2 = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HIGH_CONTRAST)

    cloud3.getScalarField(0).setColorScale(scale)
    cloud4.getScalarField(0).setColorScale(scale)
    cloud5.getScalarField(0).setColorScale(scale)
    cloud6.getScalarField(0).setColorScale(scale)
    cloud7.getScalarField(0).setColorScale(scale)
    cloud9.getScalarField(0).setColorScale(scale)
    cloud10.getScalarField(0).setColorScale(scale)
    cloud11.getScalarField(0).setColorScale(scale)
    cloud12.getScalarField(0).setColorScale(scale)

    if lowerBound > 1:
        cloud42.getScalarField(cloud42.getScalarFieldDic()['Original cloud index']).setColorScale(scale2)
    cloud52.getScalarField(cloud52.getScalarFieldDic()['Original cloud index']).setColorScale(scale2)
    cloud62.getScalarField(0).setColorScale(scale)
    cloud72.getScalarField(0).setColorScale(scale)

    cloud3.setCurrentDisplayedScalarField(0)
    cloud4.setCurrentDisplayedScalarField(0)
    cloud5.setCurrentDisplayedScalarField(0)
    cloud6.setCurrentDisplayedScalarField(0)
    cloud7.setCurrentDisplayedScalarField(0)
    cloud10.setCurrentDisplayedScalarField(0)
    cloud11.setCurrentDisplayedScalarField(0)

    if lowerBound > 1:
        cloud42.setCurrentDisplayedScalarField(cloud42.getScalarFieldDic()['Original cloud index'])
    cloud52.setCurrentDisplayedScalarField(cloud52.getScalarFieldDic()['Original cloud index'])
    cloud62.setCurrentDisplayedScalarField(0)
    cloud72.setCurrentDisplayedScalarField(0)

    output_file = os.path.join(output_dir, "CLEAN" + filename[:-4] + ".bin")

    if lowerBound > 1:
        res = cc.SaveEntities(
            [cloud1, cloud3, cloud5, cloud4, cloud6, cloud7, cloud8, cloud9, cloud10, cloud11, cloud12, cloud62,
             cloud72, cloud42, cloud52, seafloorDEM], output_file)
    else:
        res = cc.SaveEntities(
            [cloud1, cloud3, cloud5, cloud4, cloud6, cloud7, cloud8, cloud9, cloud10, cloud11, cloud12, cloud62,
             cloud72, cloud52, seafloorDEM], output_file)

    small_output_dir = os.path.join(output_dir, "smallClean")
    if not os.path.exists(small_output_dir):
        os.makedirs(small_output_dir)

    small_output_file = os.path.join(small_output_dir, "SMALL" + filename[:-4] + ".bin")
    res0 = cc.SaveEntities([cloud5, cloud7, cloud52, seafloorDEM], small_output_file)


def main():
    parser = argparse.ArgumentParser(description='Process and classify point clouds.')
    parser.add_argument('path', type=str, help='Directory containing the LAS files.')
    parser.add_argument('--output_dir', type=str, default='.', help='Directory to save the processed files.')

    args = parser.parse_args()

    path = args.path
    output_dir = args.output_dir

    dir_list = os.listdir(path)
    print("Files and directories in '", path, "' :")
    print(dir_list)

    for file in dir_list:
        if file.endswith(".las"):
            print("Processing file:", file)
            clean_classify(path, file, output_dir)


if __name__ == "__main__":
    main()



