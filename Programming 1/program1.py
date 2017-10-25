import sys
#from string import punctuation
import math
import random

def main():
    files = sys.argv[1:]
    inp = []
    for file in files:
        with open(file, "rb") as f:
            d = f.readlines()
            for line in d:
                inp.append(line.rstrip())

    # to remove punctuations and convert input to list of words
    data = []
    for line in inp:
        tmp = line.split()
        data.append([element.lower() for element in tmp])

    unigrams = {"phi": len(data)}
    bigrams_no_smooth = {}
    bigrams_smooth = {}

    for line in data:
        for word in line:
            if word in unigrams: unigrams[word] += 1
            else: unigrams[word] = 1

    for line in data:
        # line[0] = "phi " + line[0]
        line = ["phi"] + line
        biwords = zip(line[:-1], line[1:])
        for w in biwords:
            word = " ".join([w[0], w[1]])
            if word in bigrams_no_smooth:
                bigrams_no_smooth[word] += 1
                bigrams_smooth[word] += 1
            else:
                bigrams_no_smooth[word] = 1
                bigrams_smooth[word] = 2
    # unigram, bigrams w/ and w/o construction complete
    # {word: frequency}
    ##############################################
    # Q1 done
    test = []
    with open("test.txt", "rb") as f:
        for line in f.readlines():
            test.append(line.rstrip())

    # to calculate probability in the testfile
    outputNGrams = []
    for s in test:
        outputNGrams.append("S = <%s>" % s)
        sen = dealSentence(s)
        outputNGrams.append("Unsmoothed Unigrams, logprob(S) = %.4f" % getUnigramProb(sen, unigrams))
        sen = plusPhi(sen)
        if isinstance(getRegBigramsProb(sen, unigrams, bigrams_no_smooth), basestring):
            outputNGrams.append("Unsmoothed Bigrams, logprob(S) = undefined")
        else: outputNGrams.append("Unsmoothed Bigrams, logprob(S) = %.4f" % getRegBigramsProb(sen, unigrams, bigrams_no_smooth))
        outputNGrams.append("Smoothed Bigrams, logprob(S) = %.4f" % getSmuBigramsProb(sen, unigrams, bigrams_smooth))

    with open("ngrams-test.trace", "w") as f:
        for op in outputNGrams:
            f.write(op + "\n")
    # with open("ngrams-test.trace", "r") as f:
    #     lines = f.readlines()
    #     for line in lines:
    #         print line

    ##############################################
    #Q2 to be completed
    seeds = []
    with open("seeds.txt", "rb") as f:
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
            outputSeeds.append("Sentence " + str(i)+": " + " ".join(s))
    with open("ngrams-gen.trace", "w") as f:
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


def getSmuBigramsProb(sen, unigrams, bigrams):
    P = 0
    V = len(unigrams)
    newBigram = zip(sen[:-1], sen[1:])
    for nb in newBigram:
        if " ".join([nb[0], nb[1]]) not in bigrams:
            P += math.log(float(1) / (unigrams[nb[0]] + V), 2)
        else:
            P += math.log(float(bigrams[nb[0] + " " + nb[1]]) / (unigrams[nb[0]]+V), 2)
    return P

if __name__ == "__main__":
    main()