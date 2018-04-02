import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as scisig
import sys

if __name__ == "__main__":

    fname = sys.argv[1]

    with open(fname, "r") as f:
        lines = f.readlines()
    l = lines[0]
    y = [0 if c == "0" else 1 for c in l]

    y = np.array(y)

    k_size = 10
    kernel = np.ones(k_size)
    y = scisig.convolve(y,kernel)
    y = np.where(y>(k_size/2),1,0)

    x = np.arange(y.shape[0])

    plt.plot(x,y)
    plt.show()
