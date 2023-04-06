import os
import re
import csv
import traceback
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

samples = {}

def parse_row(row):
    print(0)

def parse_sample_name(inst):
    m = re.search(r'(?P<year>[0-9]{2})(?P<location>[A-Za-z]+)(?P<samplenum>[0-9]{2,3})(?P<inclusion>[I]?)-(?P<crystalnum>[A-Za-z0-9]+)([\-]{1})?(?P<distance>[a-zA-Z0-9]+)?([\-]{1})?(?P<duplicate>[0-3]+)?', inst)
    m2 = re.search(r'ALMA-PL([AG]?){0,2}(?P<crystalnum>[0-9]{2})', inst)

    if m:
        return {
            "year": m.group('year'), 
            "location": m.group('location'), 
            "sample_num": m.group('samplenum'), 
            "crystal_num": m.group('crystalnum'),
            "distance": m.group('distance'),
            "duplicate": m.group('duplicate'),
            "inclusion": m.group('inclusion') == "I"
        }

    if m2:
        return {
            "sample_num": "ALMA", 
            "crystal_num": m2.group('crystalnum')
        }


def sample_to_string(sample):
    if sample is None:
        return ""
    if sample["sample_num"] == "ALMA":
        return sample["sample_num"] + sample["crystal_num"]
    else:
        name = sample["year"] + sample["location"] + sample["sample_num"] 

        if sample["inclusion"]:
            name += "I"

        name += "-" + sample["crystal_num"]

        if sample["duplicate"] is not None:
            name += "-" + sample["duplicate"]

        return name


def graph(data, sample_name):
    fig, ax = plt.subplots()

    ax.plot(*zip(*data), 'o-', linewidth=2.0)
    
    plt.title(sample_name, fontsize=28)
    ax.set_ylabel('An')
    ax.set_xlabel('Distance μm')

    # Set the title font size
    ax.xaxis.label.set_fontsize(22)
    ax.yaxis.label.set_fontsize(22)

    # Set the tick label font size
    ax.tick_params(axis='both', which='major', labelsize=20)

    # set image size 
    fig.set_size_inches(7, 7)

    # set graph size margins 
    plt.subplots_adjust(left=0.13, bottom=0.11, right=0.95, top=.92, wspace=0.2, hspace=0.2)

    ax.set_xlim(xmin=0)
    ax.set_ylim([40, 100])

    # set font to times new roman 
    plt.rcParams['font.family'] = 'Times New Roman' 

    plt.savefig(os.path.join("output", sample_name + '.png'))


# iterate over the rows in an excel sheet 

source = pd.read_excel("Matlab Plag Format.xlsx", sheet_name="Sheet2")
dr = pd.DataFrame(source)

# delete all .png files in output folder
for file in os.listdir("output"):
    if file.endswith(".png"):
        os.remove(os.path.join("output", file))

for index, row in dr.iterrows():
    try:

        # continue if row is empty
        if type(row[1]) == str:
            continue

        # continue if row is NaN
        if row[0] != row[0]:
            continue

        name = sample_to_string(parse_sample_name(str(row[0])))
        
        if name not in samples:
            samples[name] = []

        samples[name].append((int(row[1]), int(row[2])))

    except Exception as e:
        if row[0] != '':
            print("Bad row: " + str(row[0]) + str(e) + str(traceback.print_exc(e)))
        continue

for sample in samples:
    graph(samples[sample], sample)