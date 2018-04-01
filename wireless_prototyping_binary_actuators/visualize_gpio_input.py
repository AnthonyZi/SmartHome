import matplotlib.pyplot as plt

if __name__ == "__main__":
    with open("gpio_input.txt", "r") as f:
        lines = f.readlines()

    print(lines)
