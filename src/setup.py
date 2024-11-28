# System
import copy
import csv
import sys
import os
import watermark
import pickle
import itertools
import random
import zipfile
from collections import defaultdict
import pprint
pp = pprint.PrettyPrinter(indent=4)
from tqdm.notebook import tqdm
import warnings
import shutil

# Math/Data
import math
import numpy as np
import pandas as pd

# Network
import igraph as ig
import networkx as nx

# Plotting
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib
from matplotlib.collections import PatchCollection
from matplotlib.ticker import MaxNLocator

# Geo
import osmnx as ox
ox.settings.log_file = True
ox.settings.requests_timeout = 300
ox.settings.logs_folder = PATH["logs"]
import fiona
import shapely
from osgeo import gdal, osr
from haversine import haversine, haversine_vector
import pyproj
from pyproj import Transformer
from shapely.geometry import Point, MultiPoint, LineString, Polygon, MultiLineString, MultiPolygon
import shapely.ops as ops
import geopandas as gpd
import geojson



     
# dict of placeid:placeinfo
# If a city has a proper shapefile through nominatim
# In case no (False), manual download of shapefile is necessary, see below
cities = {}
with open(PATH["parameters"] + 'cities.csv') as f:
    csvreader = csv.DictReader(f, delimiter=';')
    for row in csvreader:
        if row['placeid'] not in ['bern', 'montreal', 'copenhagen']:
            continue
        cities[row['placeid']] = {}
        for field in csvreader.fieldnames[1:]:
            cities[row['placeid']][field] = row[field]     
if debug:
    print("\n\n=== Cities ===")
    pp.pprint(cities)
    print("==============\n\n")

# Create city subfolders  
for placeid, placeinfo in cities.items():
    for subfolder in ["data", "plots", "plots_networks", "results", "exports", "exports_json", "videos"]:
        placepath = PATH[subfolder] + placeid + "/"
        if not os.path.exists(placepath):
            os.makedirs(placepath)
            print("Successfully created folder " + placepath)

from IPython.display import Audio
sound_file = '../dingding.mp3'

print("Setup finished.\n")
