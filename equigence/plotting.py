import matplotlib
matplotlib.use('Agg')  # Sets matplotlib to use a non-GUI backend

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO


def plotchart(y_axis, x_axis, plot_type, y_label, x_label, title):
    plt.figure()
    if plot_type == 'line':
        plt.plot(x_axis, y_axis)
    elif plot_type == 'scatter':
        plt.scatter(x_axis, y_axis)
    elif plot_type == 'bar':
        plt.bar(x_axis, y_axis)
    else:
        raise ValueError("Invalid plot type")
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plotImage = BytesIO()
    plt.savefig(plotImage, format='png')
    plotImage.seek(0)
    plt.close()
    return plotImage.getvalue()

def plotComparisonChart(comparisonData, x_axis, plot_type, y_label, x_label, title):
    fig, ax = plt.subplots()
    bar_width = 0.2
    index = np.arange(len(x_axis))

    for i, (symbol, values) in enumerate(comparisonData.items()):
        plt.bar(index + bar_width * i, values, bar_width, label=symbol)

    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.xticks(index + bar_width * (len(comparisonData) / 2), x_axis)
    plt.legend()

    plotImage = BytesIO()
    plt.savefig(plotImage, format='png')
    plotImage.seek(0)
    plt.close()
    
    return plotImage.getvalue()
