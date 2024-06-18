import os

import sys
import math
import psutil




#os.environ["_CCTRACE_"]="ON"
import cloudComPy as cc

from gendata import getSampleCloud, dataDir

cc.initCC()

cloud1 = cc.loadPointCloud(getSampleCloud(5.0))


cloud = cc.loadPointCloud("smallsection-processed_LLS_2024-03-15T051615.010100_0_3.las")


tr3 = cc.ccGLMatrix()
tr3.initFromParameters(0., (0., 0., 0.), (3.0, 0.0, 4.0))
cylinder = cc.ccCylinder(0.5, 3.0, tr3, 'aCylinder', 48)

nbCpu = psutil.cpu_count()
bestOctreeLevel = cc.DistanceComputationTools.determineBestOctreeLevel(cloud, cylinder)
params = cc.Cloud2MeshDistancesComputationParams()
params.maxThreadCount=nbCpu
params.octreeLevel=bestOctreeLevel

#%%time
cc.DistanceComputationTools.computeCloud2MeshDistances(cloud, cylinder, params)

#%matplotlib inline
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors

dic = cloud.getScalarFieldDic()
sf=cloud.getScalarField(dic['C2M absolute distances'])
asf= sf.toNpArray()

(n, bins, patches) = plt.hist(asf, bins=256, density=1) # histogram for matplotlib
fracs = bins / bins.max()
norm = colors.Normalize(fracs.min(), fracs.max())
for thisfrac, thispatch in zip(fracs, patches):
    color = plt.cm.rainbow(norm(thisfrac))
    thispatch.set_facecolor(color)

plt.show()
