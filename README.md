# Benthic (LiDAR) Mapping

![shark](./figures/shark.jfif)

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

conda create env --name lidar python=3.10 -y
conda activate lidar

conda config --add channels conda-forge
conda config --set channel_priority strict

conda install -n base conda-libmamba-solver
conda config --set solver libmamba   

# This will take a while, go grab a cup of coffee ☕
conda install -f requirements.txt -y
```

After this is done, run the `build.py` script, which **expects that the `binaries` are already in `./build`**; if 
they're not, download them [here](https://www.simulation.openfields.fr/index.php/cloudcompy-downloads/3-cloudcompy-binaries/5-windows-cloudcompy-binaries/106-cloudcompy310-20240613)
and place the `.7z` file in the `./build` folder.

```bash
# cmd

pip install py7zr
python build.py

./build/CloudComPy310/envCloudComPy.bat
```

### Tests

Now try running the test:

```bash
# Instructions



```

If successful, it should output the following:
- asdf
- asdf
- asdf

## Use

Below is an example for how the driving script, `main.py`, can be used:

![GUI Image Here]()

```bash
# Instructions



```