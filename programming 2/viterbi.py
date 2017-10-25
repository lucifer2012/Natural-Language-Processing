import sys
import math

tags = ["verb", "noun", "prep", "inf"]
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
    for i in range(len(probInputs)):
        probDict[probInputs[i][0] + " " + probInputs[i][1]] = float(probInputs[i][2])
    ##################################################

    #to process the data with viterbi
    with open("viterbi-trace.txt", "w") as f:
        for sen in sensInputs:
            f.write("PROCESSING SENTENCE: " + " ".join(sen) + "")
            path, scores, backPtr, wordsDict = viterbi(probDict, sen)
            f.write("FINAL VITERBI NETWORK\n")
            for key,val in wordsDict.items():
                f.write("P(%s)=%.4f\n"%(key, val))
            f.write("FINAL BACKPTR NETWORK\n")
            for i in range(len(path)):
                ele = path[i]
                f.write("Backptr(%s=%s) = %s\n" % (sen[ele[0]], tags[ele[1]], tags[ele[2]]))
            f.write("BEST TAG SEQUENCE HAS LOG PROBABILITY=%.4f\n"%max([wordsDict[key] for key in wordsDict.keys() if key.startswith(sen[-1])]))
            for i in range(len(sen)):
                f.write(sen[i] + " -> " + tags[backPtr[i]]+"\n")
            f.write("FORWARD ALGORITHM RESULTS\n")
            seqsum = forward(probDict, sen)
            for w in range(len(sen)):
                total = sum(seqsum[key] for key in seqsum.keys() if key.endswith(str(w)))
                for i in range(len(tags)):
                    f.write("P(%s=%s)=" % (sen[w], tags[i]))
                    f.write(format(seqsum[str(i) + str(w)] / total, ".4f"))
                    f.write("\n")
            f.write("\n")

    ##################################################
    # to process data with forward




def viterbi(probs, sentence):
    global tags
    # initialization
    wordsDict = dict()
    scores = dict()
    backPtr = []
    seq = 0;
    seqMax = float("-inf")
    path = []
    for i in range(len(tags)):
        val = getProb(sentence[0] + " " + tags[i], probs) * getProb(tags[i]+" "+ "phi", probs)
        scores[str(i) + "0"] = val
        wordsDict[sentence[0]+"="+tags[i]] = math.log(val, 2)
        if getProb(sentence[0] + " " + tags[i], probs) * getProb(tags[i]+" "+ "phi", probs) > seqMax:
            seqMax = getProb(sentence[0] + " " + tags[i], probs) * getProb(tags[i]+" "+ "phi", probs)
            seq = i
    backPtr.append(seq)
    for w in range(1, len(sentence)):
        seq = 0
        seqMax = float('-inf')
        for t in range(len(tags)):
            idx, maxProb = getScoreK(t,w,scores,tags,probs)
            path.append((w,t,idx))
            val = getProb(sentence[w]+" "+tags[t], probs) * maxProb
            if val > seqMax: seq = t; seqMax = val
            scores[str(t) + str(w)] = val
            wordsDict[sentence[w]+"="+tags[t]] = math.log(val,2)
        backPtr.append(seq)

    return path, scores, backPtr, wordsDict

def getScoreK(t, w, scores, tags, probs):
    maxProb = 0
    idx = 0
    for k in range(len(tags)):
        prob = scores[str(k)+ str(w-1)] * getProb(tags[t] + " " + tags[k], probs)
        if prob > maxProb: maxProb = prob; idx = k
    return idx, maxProb

def getProb(key, probs):
    return probs[key] if key in probs else 0.0001

def forward(probs, sentence):
    global tags
    seqSum = dict()
    for i in range(len(tags)):
        seqSum[str(i)+"0"] = getProb(sentence[0]+" "+ tags[i], probs) * getProb(tags[i]+" "+ "phi", probs)
    for w in range(1, len(sentence)):
        for t in range(len(tags)):
            seqSum[str(t) + str(w)] = getProb(sentence[w]+" "+tags[t], probs) * getSum(t, w, seqSum, probs)
    return seqSum

def getSum(t, w, seqSum, probs):
    global tags
    return sum([seqSum[str(j)+str(w-1)] * getProb(tags[t]+" "+ tags[j], probs) for j in range(len(tags))])

if __name__ == '__main__':
    main()