import numpy as np
import json


def fitFunction(chans, scales):
    predictions = np.dot(chans, scales[:-1])
    return predictions


def saveResults(result, outname="results.json"):
    with open(outname, "w") as f:
        json.dump(result, f)


def loadResults(outname="results.json"):
    with open(outname, "r") as f:
        result = json.load(f)
    return result
