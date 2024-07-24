

import cloudComPy as cc
import os
import cloudComPy.CSF


def octreeLevel(octree):
    for elem in range(7, 11):
        if octree.getCellSize(elem) < .1:
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

    # octree level selection--begin
    print(filename)

    octree = cloud3.computeOctree(progressCb=None, autoAddChild=True)

    index = octreeLevel(octree)



    print(index)

    print(octree.getCellSize(7))
    print(octree.getCellSize(8))
    print(octree.getCellSize(9))
    print(octree.getCellSize(10))
    print(octree.getCellSize(11))
    print("___________________________")

    #octree level selection---end

path = "B:\Xander\Good Data"
dir_list = os.listdir(path)
print("Files and directories in '", path, "' :")
print(dir_list)


for file in dir_list:
    if file.endswith(".las"):
        clean_classify(path, file )






