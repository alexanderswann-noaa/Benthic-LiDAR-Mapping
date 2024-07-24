#!/usr/bin/env python3

##########################################################################
#                                                                        #
#                              CloudComPy                                #
#                                                                        #
#  This program is free software; you can redistribute it and/or modify  #
#  it under the terms of the GNU General Public License as published by  #
#  the Free Software Foundation; either version 3 of the License, or     #
#  any later version.                                                    #
#                                                                        #
#  This program is distributed in the hope that it will be useful,       #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of        #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the          #
#  GNU General Public License for more details.                          #
#                                                                        #
#  You should have received a copy of the GNU General Public License     #
#  along with this program. If not, see <https://www.gnu.org/licenses/>. #
#                                                                        #
#          Copyright 2020-2021 Paul RASCLE www.openfields.fr             #
#                                                                        #
##########################################################################

import os
import sys
import math
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors

#os.environ["_CCTRACE_"]="ON" # only if you want C++ debug traces

#from gendata import getSampleCloud, getSampleCloud2, dataDir, dataExtDir, isCoordEqual
import cloudComPy as cc
# print(dataDir)

dataDir = r"C:\Users\Alexander.Swann\Desktop"


entities = cc.importFile(r"Z:\NCCOS-temp\Swann\data\processed\all14processed\binFiles\SMALLprocessed_LLS_2024-03-15T051615.010100_0_3.bin")
meshes = entities[0]
clouds = entities[1]
facets = entities[2]
polylines = entities[3]
structure = entities[4]


for cloud in clouds:
    print(cloud.getName())




cloud1 = cc.loadPointCloud(r"Z:\NCCOS-temp\Swann\data\processed\all14processed\lasFiles\SMALLprocessed_LLS_2024-03-15T051615.010100_0_3.las")
cloud1.setCurrentScalarField(0)
cloud1.setCurrentDisplayedScalarField(0)

dic = cloud1.getScalarFieldDic()
sf=cloud1.getScalarField(dic['Intensity'])

#cloud1.setCurrentDisplayedScalarField(sf)

colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
scale=colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)



cloud1.getScalarField(cloud1.getScalarFieldDic()['Intensity']).setColorScale(scale)


cloud1.setCurrentDisplayedScalarField(cloud1.getScalarFieldDic()['Intensity'])

cc.addToRenderScene(cloud1)



# #---intesity hist start
# dic = cloud1.getScalarFieldDic()
# sf=cloud1.getScalarField(dic['Intensity'])
# asf= sf.toNpArray()
#
# (n, bins, patches) = plt.hist(asf, bins=256, density=1) # histogram for matplotlib
# fracs = bins / bins.max()
# norm = colors.Normalize(fracs.min(), fracs.max())
# for thisfrac, thispatch in zip(fracs, patches):
#     color = plt.cm.rainbow(norm(thisfrac))
#     thispatch.set_facecolor(color)
#
# plt.show()
# #---intesity hist end



#---render-display-begin

#struct = cc.importFile(r"Z:\NCCOS-temp\Swann\data\processed\all14processed\lasFiles\SMALLprocessed_LLS_2024-03-15T051615.010100_0_3.las")

#
# for cloud in struct[1]:
#     cc.computeNormals([cloud])
#     cloud.showNormals(True)
#     cc.addToRenderScene(cloud)






# res = cloud1.exportCoordToSF(True, True, True)
# sfx=cloud1.getScalarField(0)
# sfy=cloud1.getScalarField(1)
# sfz=cloud1.getScalarField(2)
#
# colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
# scale=colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)
# sf.setColorScale(scale)


#cc.setOrthoView()
cc.setIsoView1()
cc.zoomOnSelectedEntity()


#cc.setCameraPos((-53.7, 57.8, 27.7))
cc.render(os.path.join(dataDir, "render1.png"), 1280,720)



# img_1=cv2.imread(os.path.join(dataDir, "render1.png"))
#
# cv2.imshow('image', img_1)
# cv2.waitKey(0)

#---render-display-end


