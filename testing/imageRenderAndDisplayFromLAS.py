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

os.environ["_CCTRACE_"]="ON" # only if you want C++ debug traces

from gendata import getSampleCloud, getSampleCloud2, dataDir, dataExtDir, isCoordEqual
import cloudComPy as cc
print(dataDir)
#---render001-begin
cloud1 = cc.loadPointCloud("smallsection-processed_LLS_2024-03-15T051615.010100_0_3.las")
cloud1.setCurrentScalarField(0)
cloud1.setCurrentDisplayedScalarField(0)
cc.addToRenderScene(cloud1)

struct = cc.importFile("smallsection-processed_LLS_2024-03-15T051615.010100_0_3.las")

#
# for cloud in struct[1]:
#     cc.computeNormals([cloud])
#     cloud.showNormals(True)
#     cc.addToRenderScene(cloud)

cc.render(os.path.join(dataDir, "render1.png"), 1280,720)

import cv2

img_1=cv2.imread(os.path.join(dataDir, "render1.png"))

cv2.imshow('image', img_1)
cv2.waitKey(0)

#---render001-end

print(dataDir)

