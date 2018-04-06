import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as scisig
import sys
import os

if __name__ == "__main__":

    files = [f for f in os.listdir(".") if "fp" in f]
    files = sorted(files)
    for f in files:

        with open(f, "r") as ff:
            lines = ff.readlines()

        l = lines[0].replace(" ", "")

        y = [0 if c == "0" else 1 for c in l]

        y = np.array(y)

        x = np.arange(y.shape[0])

        print(f)
        plt.figure()
        plt.plot(x,y, 'g')
        plt.show()
