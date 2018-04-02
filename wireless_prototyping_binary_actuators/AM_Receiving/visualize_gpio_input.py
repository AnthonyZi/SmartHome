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
    l1 = lines1[0]
    l2 = lines2[0]

    y1 = [0 if c == "0" else 1 for c in l1]
    y2 = [0 if c == "0" else 1 for c in l2]

    y1 = np.array(y1)
    y2 = np.array(y2)

    x = np.arange(y.shape[0])

    plt.plot(x,y1)
    plt.plot(x,y2)
    plt.show()
