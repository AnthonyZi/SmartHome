import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as scisig
import sys

if __name__ == "__main__":

    f1 = "fp1"
    f2 = "fp2"

    with open(f1, "r") as f:
        lines1 = f.readlines()
    with open(f2, "r") as f:
        lines2 = f.readlines()

    y1 = lines1[0].split(" ")
    y2 = lines2[0].split(" ")

    y1 = [c for c in y1 if not c == ""]
    y2 = [c for c in y2 if not c == ""]

    y1 = np.array(y1).astype(int)
    y2 = np.array(y2).astype(int)

    y1 = y1
    y2 = y2/5

    y1 = np.array(y1).astype(int)
    y2 = np.array(y2).astype(int)

    x1 = np.arange(y1.shape[0])
    x2 = np.arange(y2.shape[0])

    plt.plot(x1,y1, 'g')
    plt.plot(x2,y2, 'r')
    plt.show()
