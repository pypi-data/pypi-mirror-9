# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from pyicane import pyicane


def main():
    census = pyicane.TimeSeries.get('census-series-1900-2001')
    data = census.data_as_dataframe()
    noja = data[data['Municipios'] == unicode(' 39047 - Noja')]
    arnuero = data[data['Municipios'] == unicode(' 39006 - Arnuero')]
    noja_plot = noja.plot()
    arnuero.plot(ax=noja_plot,
                 title='Population evolution in Noja vs Arnuero')
    print noja
    print arnuero
    plt.show()

if __name__ == '__main__':
    main()