import sys


def main():
    inputs = []
    ##################################################
    # data massage
    for file in sys.argv[1:]:
        tmp = []
        with open(file, "r") as f:
            lines = f.readlines()
            tmp = [line.rstrip().split(" ") for line in lines]
        inputs.append(tmp)
    probInputs, sensInputs = inputs
    probDict = dict()
    for l in probInputs:
        probDict[l[0] + " " + l[1]] = float(l[2])
    ##################################################


if __name__ == '__main__':
    main()