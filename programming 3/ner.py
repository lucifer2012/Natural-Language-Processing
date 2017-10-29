import sys

isWord = False
isWordCon = False
isPos = False
isPosCon = False
isAbbr = False
isCap = False
isLocation = False
appearedWords = set()
appearedPos = set()

labelDict = {
    "O":0,
    "B-PER":1,
    "I-PER":2,
    "B-LOC":3,
    "I-LOC":4,
    "B-ORG":5,
    "I-ORG":6
}

def main():
    # data processing in the first place
    # inputData[0] contains all the sentences in the training set
    # inputData[1] contains all the sentences in the test set
    # inputData[1] contains all the locations in the locs set
    ftypes = sys.argv[4:]
    dealTypes(ftypes)
    inputData = [[], [], []]
    for i in range(3):
        with open(sys.argv[i+1], "r") as f:
            lines = f.readlines()
            if i < 2: inputData[i] = sentenceBreak(lines)
            else:
                inputData[i] = [line.rstrip().split()[0].lower() for line in lines]
    locations = inputData[2]
    setDifference(inputData[0], inputData[1])
    trainReadable = toString(produceReadable(inputData[0], locations))
    testReadable = toString(produceReadable(inputData[1], locations))
    with open("train.txt.readable", "w") as f:
        for tr in trainReadable:
            for t in tr:
                f.write(t+"\n")
            f.write("\n")
    with open("test.txt.readable", "w") as f:
        for tr in testReadable:
            for t in tr:
                f.write(t+"\n")
            f.write("\n")
    features = produceFeatures(inputData[0], inputData[1])
    trainVectors = produceFeaVectors(features, inputData[0], appearedWords, appearedPos, locations)
    testVectors = produceFeaVectors(features, inputData[1], appearedWords, appearedPos, locations)
    with open("train.txt.vector", "w") as f:
        for line in trainVectors:
            f.write(vectorsToString(line) + "\n")
    with open("test.txt.vector", "w") as f:
        for line in testVectors:
            f.write(vectorsToString(line) + "\n")
    print "Over~"

def vectorsToString(line):
    # format each line to printable type
    temp = [line[0]]
    temp += sorted(line[1:], key=lambda x:x[0])
    s = ""
    for e in temp:
        if type(e) is int:
            s += str(e) + " "
        else:
            s += str(e[0]) + ":" + str(e[1]) + " "
    return s

def produceFeaVectors(features, dataset, appearedWords, appearedPos, locations):
    # to generate the feature vectors needed in the examples
    global isWord, isWordCon, isPos, isPosCon, isAbbr, isCap, isLocation
    res = []
    for s in dataset:
        for i in range(len(s)):
            temp = []
            # add label
            temp.append(labelDict[s[i][0]])
            if isWord:
                if s[i][2] in appearedWords: temp.append([features.index("word-UNK"), 1])
                else: temp.append([features.index("word-"+s[i][2]), 1])
            if isWordCon:
                prev = "PHI"; next = "OMEGA"
                if i == 0:
                    next = s[i+1][2] if s[i+1][2] not in appearedWords else "UNK"
                elif i == len(s) - 1:
                    prev = s[i-1][2] if s[i-1][2] not in appearedWords else "UNK"
                else:
                    prev = s[i - 1][2] if s[i - 1][2] not in appearedWords else "UNK"
                    next = s[i + 1][2] if s[i + 1][2] not in appearedWords else "UNK"
                temp.append([features.index("prev-word-" + prev), 1])
                temp.append([features.index("next-word-" + next), 1])
            if isPos:
                if s[i][1] in appearedPos: temp.append([features.index("pos-UNKPOS"), 1])
                else: temp.append([features.index("pos-" + s[i][1]), 1])
            if isPosCon:
                # pos = s[i][1] if s[i][1] not in appearedPos else "UNKPOS"
                prev = "PHIPOS"; next = "OMEGAPOS"
                if i == 0:
                    next = s[i+1][1] if s[i+1][1] not in appearedPos else "UNKPOS"
                elif i == len(s) - 1:
                    prev = s[i-1][1] if s[i-1][1] not in appearedPos else "UNKPOS"
                else:
                    prev = s[i - 1][1] if s[i - 1][1] not in appearedPos else "UNKPOS"
                    next = s[i + 1][1] if s[i + 1][1] not in appearedPos else "UNKPOS"
                temp.append([features.index("prev-pos-" + prev), 1])
                temp.append([features.index("next-pos-" + next), 1])
            if isAbbr:
                if len(s[i][2]) < 5 and s[i][2][-1] == "." and isValid(s[i][2]): temp.append([features.index("Abbr"), 1])
            if isCap:
                if s[i][2][0].isalpha() and s[i][2][0].upper() == s[i][2][0]: temp.append([features.index("Cap"), 1])
            if isLocation:
                if s[i][2].lower() in locations: temp.append([features.index("Location"), 1])
            res.append(temp)
    return res


def produceFeatures(train, test):
    # to produce the vector of features, the indices of which could be used as the IDs
    global isWord, isWordCon, isPos, isPosCon, isAbbr, isCap, isLocation
    dataset = train + test
    wordSet = set(["word-UNK"])
    wordConSet  = set(["prev-word-UNK", "next-word-UNK", "prev-word-PHI", "next-word-OMEGA"])
    posSet = set(["pos-UNKPOS", "pos-PHIPOS", "pos-OMEGAPOS"])
    posConSet = set(["prev-pos-PHIPOS", "next-pos-OMEGAPOS", "prev-pos-UNKPOS", "next-pos-UNKPOS"])
    feaset = []
    # construct wordSet
    for s in dataset:
        for ele in s:
            wordSet.add("word-"+ele[2])
            wordConSet.add("prev-word-"+ele[2])
            wordConSet.add("next-word-"+ele[2])
            posSet.add("pos-"+ele[1])
            posConSet.add("prev-pos-"+ele[1])
            posConSet.add("next-pos-"+ele[1])
    if isWord: feaset += list(wordSet)
    if isWordCon: feaset += list(wordConSet)
    if isPos: feaset += list(posSet)
    if isPosCon: feaset += list(posConSet)
    if isAbbr: feaset += ["Abbr"]
    if isCap: feaset += ["Cap"]
    if isLocation: feaset += ["Location"]
    return feaset


def setDifference(trainset, testset):
    # to produce the set of words that appear in the testset but not in the trainset
    global appearedWords, appearedPos
    words = set()
    poses = set()
    for sentence in trainset:
        for s in sentence:
            poses.add(s[1])
            words.add(s[2])
    for sentence in testset:
        for s in sentence:
            if s[2] not in words: appearedWords.add(s[2])
            if s[1] not in poses: appearedPos.add(s[1])


def toString(dataset):
    global isWord, isWordCon, isPos, isPosCon, isAbbr, isCap, isLocation
    res = []
    for d in dataset:
        temp = []
        temp.append("WORD: " + d[0] if isWord else "WORD: n/a")
        temp.append("WORDCON: " + d[1][0] + " " + d[1][1] if isWordCon else "WORDCON: n/a")
        temp.append("POS: " + d[2] if isPos else "POS: n/a")
        temp.append("POSCON: " + d[3][0] + " " + d[3][1] if isPosCon else "POSCON: n/a")
        temp.append("ABBR: " + d[4] if isAbbr else "ABBR: n/a")
        temp.append("CAP: " + d[5] if isCap else "CAP: n/a")
        temp.append("LOCATION: " + d[6] if isLocation else "LOCATION: n/a")
        res.append(temp)
    return res



def produceReadable(data, locations):
    # flag is used to indicate whether it's the train or test dataset
    global appearedWords, appearedPos
    res = []
    for sentence in data:
        for i in range(len(sentence)):
            temp = []
            # add word
            word = sentence[i][2]
            if word in appearedWords: temp.append("UNK")
            else: temp.append(word)
            if i == 0:
                # add wordcon
                word = None
                if sentence[i+1][2] in appearedWords: word = "UNK"
                else: word = sentence[i+1][2]
                temp.append(["PHI", word])
                # add POS
                if sentence[i][1] in appearedPos: temp.append("UNKPOS")
                else: temp.append(sentence[i][1])
                # add pos con
                if sentence[i+1][1] in appearedPos: temp.append(["PHIPOS", "UNKPOS"])
                else: temp.append(["PHIPOS", sentence[i + 1][1]])
            elif i == len(sentence) - 1:
                if sentence[i-1][2] in appearedWords: temp.append(["UNK", "OMEGA"])
                else: temp.append([sentence[i-1][2], "OMEGA"])
                if sentence[i][1] in appearedPos: temp.append("UNKPOS")
                else: temp.append(sentence[i][1])
                if sentence[i-1][1] in appearedPos: temp.append(["UNKPOS", "OMEGAPOS"])
                else: temp.append([sentence[i-1][1], "OMEGAPOS"])
            else:
                word_left, word_right = sentence[i-1][2], sentence[i+1][2]
                if word_left in appearedWords: word_left = "UNK"
                if word_right in appearedWords: word_right = "UNK"
                temp.append([word_left, word_right])
                pos = sentence[i][1]
                if pos in appearedPos: pos = "UNKPOS"
                temp.append(pos)
                pos_left, pos_right = sentence[i-1][1], sentence[i+1][1]
                if pos_left in appearedPos: pos_left = "UNKPOS"
                if pos_right in appearedPos: pos_right = "UNKPOS"
                temp.append([pos_left, pos_right])
            # add ABBR
            if len(sentence[i][2]) < 5 and sentence[i][2][-1] == "." and isValid(sentence[i][2]):
                temp.append("yes")
            else: temp.append("no")
            # add CAP
            if sentence[i][2][0].isalpha() and sentence[i][2][0].upper() == sentence[i][2][0]:
                temp.append("yes")
            else: temp.append("no")
            # add location
            if sentence[i][2].lower() in locations:
                temp.append("yes")
            else:
                temp.append("no")
            res.append(temp)
    return res


def isValid(s):
    num = 0
    for c in s:
        if c.isalpha(): continue
        elif c == ".": num += 1
        else: return False
    return num > 0

def sentenceBreak(data):
    res = []
    temp = []
    for d in data:
        if d.strip():
            temp.append(d.rstrip().split())
        else:
            if temp: res.append(temp)
            temp = []
    return res


def dealTypes(ftypes):
    global isWord, isWordCon, isPos, isPosCon, isAbbr, isCap, isLocation
    for type in ftypes:
        if type == "WORD": isWord = True
        elif type == "WORDCON": isWordCon = True
        elif type == "POS": isPos = True
        elif type == "POSCON": isPosCon = True
        elif type == "ABBR": isAbbr = True
        elif type == "CAP": isCap = True
        else: isLocation = True

if __name__ == '__main__':
    main()