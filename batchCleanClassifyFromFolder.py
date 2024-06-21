
import os
import sys
import math
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors

# os.environ["_CCTRACE_"]="ON" # only if you want C++ debug traces

from gendata import getSampleCloud, getSampleCloud2, dataDir, dataExtDir, isCoordEqual
import cloudComPy as cc
import cloudComPy.CSF

input_file_name = "smallsection-processed_LLS_2024-03-15T051615.010100_0_3.las"


def octreeLevel(octree):
    for elem in range(11, 6, -1):
        if octree.getCellSize(elem) > .06 :
            return elem


def clean_classify(path, filename):
    cloud1 = cc.loadPointCloud(path + "/"+filename)

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

    # remove-statisitcal-outliers---begin

    cloudRef = cc.CloudSamplingTools.sorFilter(knn=6, nSigma=10, cloud=new_cloud)
    (cloud3, res) = new_cloud.partialClone(cloudRef)
    cloud3.setName("cloud3")

    # remove-statisitcal-outliers---end

    ## select-octree-lvl---begin


    octree = cloud3.computeOctree(progressCb=None, autoAddChild=True)

    level = octreeLevel(octree)


    ## select-octree-lvl--end


    # ---extractFish-begin

    res1 = cc.ExtractConnectedComponents(clouds=[cloud3],
                                         minComponentSize=10,
                                         octreeLevel = level,
                                         randomColors=True)
    print(res1)

    # cloud01 = cc.MergeEntities(res1[1], createSFcloudIndex=True)
    # cloud01.setName("pump_Extract_Components")
    # cloud02 = cc.MergeEntities(res1[2], createSFcloudIndex=True)
    # cloud02.setName("pump_residual_Components")
    # res2 = res1[1] + res1[2] # connected components plus regrouped residual components
    # cloud2 = cc.MergeEntities(res2, createSFcloudIndex=True)
    # cloud2.setName("pump_extract_Residual_Components")
    # cloud3 = cc.MergeEntities(res2, deleteOriginalClouds=True)
    # cloud3.setName("pump_extract_Residual_Components")

    res4 = [res1[1][0]]
    res3 = res1[2] + res4

    cloud4 = cc.MergeEntities(res3, createSFcloudIndex=True)
    cloud4.setName("Rough ground")

    cloud5 = cc.MergeEntities(res1[1][1:], createSFcloudIndex=True)
    cloud5.setName("Rough fish " + str(len(res1[1][1:])) + " total: Octree Level " + str(level))

    print(str(len(res1[1][1:])) + " total fish")

    res1 = None
    # ---extractFish-end

    # --- create DEM --- begin
    cloud4.setCurrentScalarField(5)
    seafloorDEM = cc.RasterizeToMesh(cloud4,
                                     gridStep=.07,
                                     emptyCellFillStrategy=cc.EmptyCellFillOption.KRIGING,
                                     projectionType=cc.ProjectionType.PROJ_MINIMUM_VALUE)

    # --- create DEM --- end

    final_cloud = cloud2
    # cloud01, cloud02, cloud2, cloud3,
    # ---export-files-begin
    res = cc.SaveEntities([cloud3,cloud4, cloud5, seafloorDEM], "CLEAN"+ filename[:-4] + ".bin")

    # --- export-files-end



path = "B:\Xander\Good Data"
dir_list = os.listdir(path)
print("Files and directories in '", path, "' :")
print(dir_list)


for file in dir_list:
    if file.endswith(".las"):
        # Prints only text file present in My Folder
        print(file)
        clean_classify(path, file )



#clean_classify("processed_LLS_2024-03-15T051615.010100_0_1.las")


