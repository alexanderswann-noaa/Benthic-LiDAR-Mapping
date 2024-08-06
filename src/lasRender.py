import math

import os
import glob
import argparse
import traceback

import CloudCompare.cloudComPy as cc
import pandas as pd
from common import announce


# -----------------------------------------------------------------------------------------------------------
# Classes
# -----------------------------------------------------------------------------------------------------------

class lasRender:
    def __init__(self,
                 bin_file,
                 image_dir,
                 output_dir, img_info):
        self.img_info = img_info
        self.output_dir = output_dir
        # Input PCD (las) file, checks
        self.bin_file = bin_file
        self.bin_name = os.path.basename(bin_file)
        self.bin_basename = "".join(self.bin_name.split(".")[:-1])

        print(self.output_dir)

        print(self.bin_file)
        print(self.bin_name)
        print(self.bin_basename)

        assert os.path.exists(self.bin_file), "Error: PCD file doesn't exist"
        assert self.bin_name.lower().endswith(".bin"), "Error: PCD file is not a 'bin' file"


    def render(self):





        entities = cc.importFile(self.bin_file)
        meshes = entities[0]
        clouds = entities[1]
        facets = entities[2]
        polylines = entities[3]
        structure = entities[4]

        print("Clouds")
        for cloud in clouds:
            print(cloud.getName())
            if("Coral Points" in cloud.getName()):
                coralCloud = cloud

        print("Meshes")
        for mesh in meshes:
            print(mesh.getName())

        print("structures")
        for structures in structure:
            print(structures)

        cloud1 = coralCloud
        cloud1.setCurrentScalarField(0)
        cloud1.setCurrentDisplayedScalarField(0)

        dic = cloud1.getScalarFieldDic()
        print(dic)

        sf = cloud1.getScalarField(dic['Intensity'])

        # cloud1.setCurrentDisplayedScalarField(sf)

        colorScalesManager = cc.ccColorScalesManager.GetUniqueInstance()
        scale = colorScalesManager.getDefaultScale(cc.DEFAULT_SCALES.HSV_360_DEG)

        cloud1.getScalarField(cloud1.getScalarFieldDic()['Intensity']).setColorScale(scale)

        cloud1.setCurrentDisplayedScalarField(cloud1.getScalarFieldDic()['Intensity'])
        #
        # cloud1.setCurrentScalarField(cloud1.getScalarFieldDic()['Coord. X'])
        # cloud1.setCurrentDisplayedScalarField(cloud1.getScalarFieldDic()['Coord. X'])
        cloud1.showSFColorsScale(True)

        cc.addToRenderScene(cloud1)
        cc.addToRenderScene(meshes[0])

        cc.setBackgroundColor(False, 255, 255, 255)
        cc.setTextDefaultCol(0, 0, 0)
        cc.setColorScaleShowHistogram(True)

        dataDir = self.output_dir
        #
        # # cc.setOrthoView()
        # cc.setIsoView1()
        # cc.zoomOnSelectedEntity()
        #
        # cc.setOrthoView()
        # cc.setGlobalZoom()
        # cc.render(os.path.join(dataDir, "renderb.png"), 2000, 1500)
        #
        # cc.setFrontView()
        # cc.render(os.path.join(dataDir, "renderFront.png"), 2000, 1500)
        #
        # cc.setBottomView()
        # cc.render(os.path.join(dataDir, "renderBottom.png"), 2000, 1500)
        #
        # cc.setTopView()
        # cc.render(os.path.join(dataDir, "renderTop.png"), 2000, 1500)
        #
        # cc.setBackView()
        # cc.render(os.path.join(dataDir, "renderBack.png"), 2000, 1500)
        #
        # cc.setLeftView()
        # cc.render(os.path.join(dataDir, "renderLeft.png"), 2000, 1500)
        #
        # cc.setRightView()
        # cc.render(os.path.join(dataDir, "renderRight.png"), 2000, 1500)
        #
        # cc.setIsoView1()
        # cc.render(os.path.join(dataDir, "renderIso1.png"), 2000, 1500)
        #
        # cc.setIsoView2()
        # cc.render(os.path.join(dataDir, "renderIso2.png"), 2000, 1500)
        #
        # cc.setCustomView((3., 5., 7.), (1., 2., 3.))
        # cc.render(os.path.join(dataDir, "renderCustom.png"), 2000, 1500)
        #
        # cc.setCameraPos((2., -15, 90.))
        # cc.render(os.path.join(dataDir, "renderCamPos1.png"), 2000, 1500)
        #
        # cc.setCameraPos((15., -15, 90.))
        # cc.render(os.path.join(dataDir, "renderCamPos2.png"), 2000, 1500)
        #
        # #cc.setCameraPos((-53.7, 57.8, 27.7))
        #
        # dist = 20.
        # alphaRad = math.pi / 20.
        # #cc.setCenteredPerspectiveView()
        #
        # #print(self.img_info['location'])
        #
        # print(self.img_info['location'][24])
        #
        # #cc.setRightView()
        # #cc.setCenteredPerspectiveView()
        # cc.setCustomView(( self.img_info['location'][24][0], self.img_info['location'][24][1] , 20 ), (1., 1., 1.))
        # cc.setGlobalZoom()
        # cc.render(os.path.join(self.output_dir, "render1.png"), 1280, 720)
        #
        # cc.setCenteredPerspectiveView()
        # cc.setCustomView((0., 1., 0.), (0., 0., 1.))
        # #cc.setGlobalZoom()
        # cc.render(os.path.join(self.output_dir, "render2.png"), 1280, 720)

        xshift = cloud1.getGlobalShift()[0]
        yshift = cloud1.getGlobalShift()[1]

        print(xshift)
        print(yshift)

        os.makedirs(self.output_dir, exist_ok=True)
        # cc.setCenteredPerspectiveView()
        # for i in range(45):
        #     print((self.img_info['location'][i][0] + xshift, self.img_info['location'][i][1]+ yshift))
        #     #cc.setCustomView((0., math.cos(i * alphaRad), -math.sin(i * alphaRad)), (0., math.sin(i * alphaRad), math.cos(i * alphaRad)))
        #     cc.setOrthoView()
        #     #cc.setGlobalZoom()
        #     cc.setCustomView((0.0, 0.0, -1.0), (1.0, 0.0, 0))
        #     cc.setCameraPos((  self.img_info['location'][i][0] + xshift,self.img_info['location'][i][1]+ yshift , 10 ))
        #     #cc.setCameraPos((self.img_info['location'][i][0], self.img_info['location'][i][1], 100))
        #
        #
        #     cc.render(os.path.join(self.output_dir, "renderangle_%d.png" % i), 2000, 1500, False)

        # for i in range(9):
        #     for j in range(9):
        #         print((i,j))
        #         #cc.setCustomView((0., math.cos(i * alphaRad), -math.sin(i * alphaRad)), (0., math.sin(i * alphaRad), math.cos(i * alphaRad)))
        #         cc.setOrthoView()
        #         #cc.setCenteredPerspectiveView()
        #         cc.setCustomView((0.0, 0.0, -1.0), (1.0, 0.0, 0))
        #         cc.setCameraPos((i, j, 10))
        #         #cc.setCameraPos((self.img_info['location'][i][0], self.img_info['location'][i][1], 100))
        #
        #
        #         cc.render(os.path.join(self.output_dir, "renderangle1_%d_%d.png" % (i, j)), 2000, 900, False)

        # for i in range(9):
        #     for j in range(9):
        #         print((i,j))
        #         #cc.setCustomView((0., math.cos(i * alphaRad), -math.sin(i * alphaRad)), (0., math.sin(i * alphaRad), math.cos(i * alphaRad)))
        #         cc.setCenteredPerspectiveView()
        #         cc.setCustomView((0.0, 0.0, -1.0), (1.0, 0.0, 0))
        #
        #         cc.setCameraPos((i, j, 60))
        #         #cc.setCameraPos((self.img_info['location'][i][0] +i, self.img_info['location'][i][1]+j, 100))
        #
        #
        #         cc.render(os.path.join(self.output_dir, "renderangle2_%d_%d.png" % (i, j)), 2000, 900, False)

        for i in range(len(self.img_info)):
            print((self.img_info['location'][i][0] + xshift, self.img_info['location'][i][1] + yshift))
            #cc.setCustomView((0., math.cos(i * alphaRad), -math.sin(i * alphaRad)), (0., math.sin(i * alphaRad), math.cos(i * alphaRad)))
            cc.setViewerPerspectiveView()
            cc.setCustomView((0.0, 0.0, -1.0), (-1.0, 0.0, 0.0))

            cc.setCameraPos((self.img_info['location'][i][0] + xshift, self.img_info['location'][i][1] + yshift, 60))
            #cc.setCameraPos((self.img_info['location'][i][0] +i, self.img_info['location'][i][1]+j, 100))

            img_name =  ".".join( (self.img_info['file_name'][i]) .split(".")[:-1] )+ "_pcd.png"
            print(img_name)
            cc.render(os.path.join(self.output_dir, img_name ), 2000, 900, False )
            #cc.render(os.path.join(self.output_dir, "renderangle3_%d.png" % i), 2000, 900, False)
        #
        # dist = 20.
        # alphaRad = math.pi / 20.
        # cc.setCenteredPerspectiveView()
        # for i in range(15):
        #     cc.setCustomView((0., math.cos(i * alphaRad), -math.sin(i * alphaRad)),
        #                      (0., math.sin(i * alphaRad), math.cos(i * alphaRad)))
        #     cc.setGlobalZoom()
        #     cc.render(os.path.join(self.output_dir, "renderangle4_%d.png" % i), 2000, 1500, False)




        # img_1=cv2.imread(os.path.join(dataDir, "render1.png"))
        #
        # cv2.imshow('image', img_1)
        # cv2.waitKey(0)

        # ---render-display-end

        announce("rendering")





    def run(self):

        self.render()
        print("Done.")

# ----------------------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------------------

def main():
    """

    """
    parser = argparse.ArgumentParser(description='Process and classify point clouds.')

    parser.add_argument('--bin_file', type=str, required=True,
                        help='Path to point cloud file (las).')

    parser.add_argument('--img_path', type=str, help='Directory containing the image files.')

    parser.add_argument('--output_dir', type=str, default="./data/processed",
                        help='Directory to save the processed files.')


    args = parser.parse_args()

    try:
        tracks = lasRender(bin_file=args.bin_file, image_dir=args.img_dir, output_dir=args.output_dir)

        #tracks.load_pcd()

        tracks.run()
        print("Done.")

    except Exception as e:
        print(f"ERROR: {e}")
        print(traceback.print_exc())


if __name__ == '__main__':
    main()