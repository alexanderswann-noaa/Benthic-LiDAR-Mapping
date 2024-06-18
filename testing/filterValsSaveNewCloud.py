import cloudComPy as cc                                                # import the CloudComPy module
cc.initCC()                                                            # to do once before dealing with plugins

cloud = cc.loadPointCloud("smallsection-processed_LLS_2024-03-15T051615.010100_0_3.las")                               # read a point cloud from a file
print("cloud name: %s"%cloud.getName())

res=cc.computeCurvature(cc.CurvatureType.GAUSSIAN_CURV, 0.05, [cloud]) # compute curvature as a scalar field
nsf = cloud.getNumberOfScalarFields()
sfCurv=cloud.getScalarField(nsf-1)
cloud.setCurrentOutScalarField(nsf-1)
filteredCloud=cc.filterBySFValue(0.01, sfCurv.getMax(), cloud)         # keep only the points above a given curvature

ok = filteredCloud.exportCoordToSF(False, False, True)                 # Z coordinate as a scalar Field
nsf = cloud.getNumberOfScalarFields()
sf1=filteredCloud.getScalarField(nsf-1)
mean, var = sf1.computeMeanAndVariance()

# using Numpy...
# using Numpy...
# using Numpy...

coordinates = filteredCloud.toNpArrayCopy()                            # coordinates as a numpy array
x=coordinates[:,0]                                                     # x column
y=coordinates[:,1]
z=coordinates[:,2]

f=(2*x-y)*(x+3*y)                                                      # elementwise operation on arrays

asf1=sf1.toNpArray()                                                   # scalar field as a numpy array
sf1.fromNpArrayCopy(f)                                                 # replace scalar field values by a numpy array

res=cc.SavePointCloud(filteredCloud,"myModifiedCloud1.bin")             #save the point cloud to a file
res=cc.SavePointCloud(filteredCloud,"myModifiedCloud1.las")