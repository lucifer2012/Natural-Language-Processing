import argparse
import sys
import random
import math

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-gen", dest="testFile")
    args = parser.parse_args(sys.argv[2:])
    testFile = args.testFile
    trainFile = sys.argv[1]

    # read in the trainFile
    inpStrings = []
    with open(trainFile, "r") as f:
        lines = f.readlines()
        for line in lines:
            inpStrings.append(line.rstrip())
    data = []
    for line in inpStrings:
        tmp = line.split()
        data.append([element.lower() for element in tmp])

    # to create unigrams and bigrams
    unigrams = {"phi": len(data)}
    bigrams_no_smooth = {}

    for line in data:
        for word in line:
            if word in unigrams: unigrams[word] += 1
            else: unigrams[word] = 1

    for line in data:
        line = ["phi"] + line
        biwords = zip(line[:-1], line[1:])
        for w in biwords:
            word = " ".join([w[0], w[1]])
            if word in bigrams_no_smooth:
                bigrams_no_smooth[word] += 1
            else:
                bigrams_no_smooth[word] = 1
    seeds = []
    with open(testFile, "rb") as f:
        for line in f.readlines():
            seeds.append(line.rstrip())
    outputSeeds = []
    for seed in seeds:
        outputSeeds.append("Seed = " + seed)
        for i in range(0, 10):
            s = []
            newSeed = seed
            while newSeed not in ["!", ".", "?"]:
                s.append(newSeed)
                newSeed = generator(newSeed, bigrams_no_smooth)
                if len(s) == 10:
                    break
            s.append(newSeed)
            # print "Sentence " + str(i)+": " + " ".join(s)
            outputSeeds.append("Sentence " + str(i) + ": " + " ".join(s))
    for op in outputSeeds:
        print op
    with open("genOutput.trace", "w") as f:
        for op in outputSeeds:
            f.write(op + "\n")

def generator(seed, bigrams):
    """return next word given the seed"""
    total = 0
    candidates = []
    for key in bigrams.keys():
        if key.split()[0] == seed.lower():
            total += bigrams[key]
            key = key.split(" ")
            candidates.append((key[1], total))
    candidates = sorted(candidates, key=lambda x:x[1])
    randomNumber = random.random()
    for a, b in candidates:
        b = float(b) / total
        if randomNumber < b:
            return a
    return "."



def dealSentence(sentence):
    sentence = sentence.split()
    s = [w.lower() for w in sentence]
    return s

def plusPhi(sentence):
    sentence = ["phi"] + sentence
    return sentence

def getUnigramProb(sentence, unigrams):
    size = 0
    for key in unigrams.keys():
        size += unigrams[key]
    size -= unigrams["phi"]
    P = 0
    for word in sentence:
        P += math.log(float(unigrams[word.lower()]) / size, 2)
    return P

def getRegBigramsProb(sentence, unigrams, bigrams):
    P = 0
    newBigram = zip(sentence[:-1], sentence[1:])
    for nb in newBigram:
        if " ".join([nb[0], nb[1]]) not in bigrams:
            return "undefined"
        else:
            P += math.log(float(bigrams[nb[0]+" "+nb[1]]) / unigrams[nb[0]], 2)
    return P


if __name__ == "__main__":
    main()