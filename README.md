# Benthic (LiDAR) Mapping

![sharks with](./figures/sharknado.webp)

---

This project is used to further process LiDAR collected by AUVs in the large MDBC initiative. The data, being referred 
to as "micro bathymetry", is collected using underwater laser scanners with imaging payloads and post-processed by 
[Voyis](https://voyis.com/).

This repo does the following:
- Cleaning Raw Point Clouds
- Segmenting Fish out of Point Clouds
- Segmenting Corals and other organisms out of Point Clouds
- Creating a Sea Floor DEM
- Assign Images to Specific Point Clouds
- Render Images of Point Cloud Track

## Getting Started

Follow the steps below to set up your `anaconda` environment, install dependencies, and run a simple unit test to
validate proper installation.

### Install

Before getting started, install [`minconda`](https://docs.anaconda.com/miniconda/) on your machine if it's not already. 
Then follow the steps below to install the python dependencies:


 Copy this and run, do not change env name
```bash
conda create --name CloudComPy310 python=3.10 -y
```

Next Activate the conda environment
```bash
conda activate CloudComPy310
```

Now we update conda. If your conda is not up to date this could take a moment
```bash
conda update -n base -c defaults conda -y
```
Now we add the conda forge channel, this is where we will download our packages from
```bash
conda config --add channels conda-forge
```

Next we set the channel priority to strict.
```bash
conda config --set channel_priority strict
```

When installing packages a solver is used to determine the prerequisite packages needed.

The default solver often takes a long time and occasionally fails, so we install the libmamba solver
```bash
conda install -n base conda-libmamba-solver -y
```

Now we set libmamba as the solver
```bash
conda config --set solver libmamba
```

To get this repository on your computer we will use git.

This install assumes you do not have git on your computer so we need to install it.
```bash
conda install git -y
```




Now cd to where you would like the repository to live.

Commonly GitHub repositories are stored in a folder named GitHub within your Documents folder.


### EXAMPLE: cd Documents\GitHub



Now we use the git clone command to get the repository on your computer
```bash
git clone https://github.com/alexanderswann-noaa/Benthic-LiDAR-Mapping.git
```

Use the cd command to get into the repository
```bash
cd Benthic-LiDAR-Mapping
```

Within the repository there is a requirements.txt file with all of the conda packages needed to run the code.

This could take a moment.
```bash
conda install --file requirements.txt -y
```

The build.py script extracts the CloudCompare Python Binary
To extract this binary we need to install py7zr via pip

FUTURE: see why we cannot use conda to install because it is available from conda [check here](https://github.com/miurahr/py7zr)
```bash
pip install py7zr
```


After installing the required packages, run the `build.py` script, which **expects that the `binaries` are already in `./build`**; if 
they're not, download them [here](https://www.simulation.openfields.fr/index.php/cloudcompy-downloads/3-cloudcompy-binaries/5-windows-cloudcompy-binaries/106-cloudcompy310-20240613) and place the `.7z` file in the `./build` folder.

Run build.py the script
```bash

python build.py
```
Change directories, enter the CloudComPy310 folder
```bash 
cd build\CloudComPy310
```
Once in the folder run this script

This script sets specific PYTHONPATH varialbes so that python knows where to access CloudComPy
```bash

envCloudComPy.bat
```

The expected output from the `envCloudComPy.bat` file is:
```bash
# Expected output:
Checking environment, Python test: import cloudComPy
Environment OK!
```

If you do not receive this message, contact `Jordan` or `Xander`. Finally, update you `PYTHONPATH` to have the directory 
of `CloudCompare`:


### Update the following to your specific path... (don't just copy and paste)
### EXAMPLE: conda env config vars set PYTHONPATH=C:/Users/your.name/.../Benthic-LiDAR-Mapping/build/CloudComPy310/CloudCompare

```bash
conda activate CloudComPy310
```

### Running

Now, try running the app:

```bash
# cmd

python app.py
```

### Common Issues

One of the most common issues is getting this error from running `envCloudComPy.bat`:

```bash

    from _cloudComPy import *
ModuleNotFoundError: No module named '_cloudComPy'
```

Luckily this is very easy to fix, Navigate to the `CloudComPy310` folder and run the `envCloudComPy.bat` file. This will 
reset the `PYTHONPATH`s which should make your computer be able to locate the CloudCompare module

```bash
# cmd

cd <path install>\CloudComPy310
envCloudComPy.bat
```
Now running `app.py` and `main.py` should work.

## Use

Below is an example for how the driving script, `app.py`, can be used:

![GUI Image](./figures/gui_pic.PNG)

### Extra

To run SfM on a folder of images, `Metashape` needs to be installed:

```bash
# cmd

pip install packages/Metashape-2.0.2-cp37.cp38.cp39.cp310.cp311-none-win_amd64.whl
```

The license is expected to be stored as the variable `METASHAPE_LICENSE` on your computer.
