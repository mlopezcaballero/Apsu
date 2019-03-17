#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 08:12:26 2019

@author: miguelcaballero
"""

# STD lib imports
import os
import sys

# Third party libs
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def corr_heatmap(data):
    correlations = data.corr()

    # Create color map ranging between two colors
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    fig, ax = plt.subplots(figsize=(12,12))
    sns.heatmap(correlations, cmap=cmap, vmax=1.0, center=0, fmt='.2f',
                square=True, linewidths=.5, annot=True, cbar_kws={"shrink": .75})
    plt.show()