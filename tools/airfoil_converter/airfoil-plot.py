#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
from airfoil2xfoil import read_airfoil
import argparse

def get_args():
    parser = argparse.ArgumentParser(description='Plot an airfoil')
    parser.add_argument('dat_in', type=str, help="The name of the file to convert", nargs='+')
    args = parser.parse_args()
    return args

def main():
    args = get_args()
    for fn in args.dat_in:
        name, airfoil = read_airfoil(fn)
        airfoil = np.array(airfoil)
        plt.plot(airfoil[:,0], airfoil[:,1], "-", label=f"{fn}: {name}")
    plt.axis('equal')
    plt.legend()
    plt.show()


if __name__=="__main__":
    main()

