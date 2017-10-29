import sys
import collections

def main():
    data = []
    # data[0] -> prediction, data[1] -> gold
    with open(sys.argv[1], "r") as f:
        words = f.readlines()[0].split()
        data.append([(words[i], words[i+1]) for i in range(0, len(words) - 1, 2)])
    with open(sys.argv[2], "r") as f:
        data.append([tuple(line.rstrip().split()) for line in f.readlines()])
    pGroup = group(data[0])
    gGroup = group(data[1])
    order = {"PER": "PERSON", "LOC": "LOCATION", "ORG": "ORGANIZATION"}
    recallTotal, precisionTotal = 0,0
    recalls, precisions = 0, 0
    with open("eval.txt", "w") as f:
        for key in ["PER", "LOC", "ORG"]:
            r, p = getRecallPrecision(pGroup, gGroup, order[key])
            recalls += r; recallTotal += len(gGroup[order[key]])
            precisions += p; precisionTotal += len(pGroup[order[key]])
            f.write("Correct " + key + " = " + toString(pGroup, gGroup, order[key]))
            f.write("\n")
            if len(gGroup[order[key]]) == 0: f.write("Recall " + key + " = n/a")
            else: f.write("Recall "+ key + " = " + str(r) + "/" + str(len(gGroup[order[key]])))
            f.write("\n")
            if len(pGroup[order[key]]) == 0: f.write("Precision " + key + " = n/a")
            else: f.write("Precision "+ key + " = " + str(p) + "/" + str(len(pGroup[order[key]])))
            f.write("\n"*2)
        if recallTotal > 0: f.write("Average Recall = " + str(recalls) + "/" + str(recallTotal)+ "\n")
        else: f.write("Average Recall = n/a \n")
        if precisionTotal > 0: f.write("Average Precision = " + str(precisions) + "/" + str(precisionTotal)+ "\n")
        else: f.write("Average Precision = n/a \n")

def toString(pGroup, gGroup, key):
    lines = []
    for x in pGroup[key]:
        if x in gGroup[key]:
            lines.append(x)
    res = []
    for val in lines:
        res.append(" ".join(val[0]) + "[" + str(val[1][0]) + "-" + str(val[1][1]) + "]")
    return " | ".join(res) if res else "NONE"


def getRecallPrecision(pGroup, gGroup, key):
    preds = pGroup[key]
    golds = gGroup[key]
    recall, precision = 0, 0
    for val in golds:
        if val in preds: recall += 1
    for val in preds:
        if val in golds: precision += 1
    return recall, precision

def group(data):
    maps = collections.defaultdict(list)
    for key in ["LOCATION", "ORGANIZATION", "PERSON"]:
        maps[key] = list()
    i = 0
    while i < len(data):
        if data[i][0].startswith("B"):
            start, end = i, i
            wordList = [data[i][1]]
            while data[end+1][0].startswith("I"):
                wordList.append(data[end+1][1])
                end += 1
            if "LOC" in data[start][0]: maps["LOCATION"].append([wordList, (start+1, end+1)])
            if "PER" in data[start][0]: maps["PERSON"].append([wordList, (start+1, end+1)])
            if "ORG" in data[start][0]: maps["ORGANIZATION"].append([wordList, (start+1, end+1)])
        i += 1
    return maps

if __name__ == '__main__':
    main()