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
    plt.close()

    return plotImage.getvalue()
