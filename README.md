# Benthic (LiDAR) Mapping

![sharks with](./figures/freakin_lasers.webp)

---

This project is used to further process LiDAR collected by AUVs in the large MDBC initiative. The data, being referred 
to as "micro bathymetry", is collected using underwater laser scanners with imaging payloads and post-processed by 
[Voyis](https://voyis.com/).

This repo does the follow:
- asdf
- asdf
- asdf
- asdf

## Getting Started

Follow the steps below to set up your `anaconda` environment, install dependencies, and run a simple unit test to
validate proper installation.

### Install

Before getting started, install [`minconda`](https://docs.anaconda.com/miniconda/) on your machine if it's not already. 
Then follow the steps below to install the python dependencies:

```bash
# cmd

# Copy this and run, do not change env name
conda create --name CloudComPy310 python=3.10 -y
conda activate CloudComPy310

conda update -n base -c defaults conda -y
conda config --add channels conda-forge
conda config --set channel_priority strict

conda install -n base conda-libmamba-solver -y
conda config --set solver libmamba

conda install git -y


git clone https://github.com/alexanderswann-noaa/Benthic-LiDAR-Mapping.git

# This will take a while, go grab a cup of coffee ☕
conda install --file requirements.txt -y
```

After this is done, run the `build.py` script, which **expects that the `binaries` are already in `./build`**; if 
they're not, download them [here](https://www.simulation.openfields.fr/index.php/cloudcompy-downloads/3-cloudcompy-binaries/5-windows-cloudcompy-binaries/106-cloudcompy310-20240613) and place the `.7z` file in the `./build` folder.

```bash
# cmd

pip install py7zr
python build.py


cd <path install>\CloudComPy310
# Run the following
envCloudComPy.bat

# Expected output:
Checking environment, Python test: import cloudComPy
Environment OK!
```

Finally, update you `PYTHONPATH` to have the directory of `CloudCompare`:

```bash
# cmd

conda env config vars set PYTHONPATH=C:/Users/your.name/.../Benthic-LiDAR-Mapping/build/CloudComPy310/CloudCompare
conda activate CloudComPy310
```


### Tests (not up to date)

Now try running the test:

```bash
# cmd

python src/features/argParse.py data/raw --output-dir data/processed
```


If successful, it should output processed `bin` files in `data/processed`


### Common Issues

One of the most common issues is getting this error

```bash

    from _cloudComPy import *
ModuleNotFoundError: No module named '_cloudComPy'
```

Luckily this is very easy to fix, Navigate to the `CloudComPy310` folder and run the `envCloudComPy.bat` file.

This will reset the `PYTHONPATH`s which should make your computer be able to locate the cloudcompare module

```bash
# cmd

cd <path install>\CloudComPy310
envCloudComPy.bat
```
Now running `app.py` and `main.py` should work.




## Use

Below is an example for how the driving script, `app.py`, can be used:

![GUI Image](./figures/gui_pic.PNG)


```bash
# Instructions



```
