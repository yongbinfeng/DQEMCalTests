from modules.plotStyles import DrawHistos
import ROOT
import json
import numpy as np

with open("fitresults.json", "r") as f:
    fitresults = json.load(f)

runs = np.array(fitresults["runs"])

energys = np.array(fitresults["energys"])
mus = np.array(fitresults["mus"])
muEs = np.array(fitresults["muEs"])
sigmas = np.array(fitresults["sigmas"])
sigmaEs = np.array(fitresults["sigmaEs"])

gMean = ROOT.TGraphErrors(len(energys), energys, mus,
                          np.zeros(len(energys)), muEs)
gSigma = ROOT.TGraphErrors(len(energys), energys,
                           sigmas, np.zeros(len(energys)), sigmaEs)

gMean.SetMarkerStyle(20)
gMean.SetMarkerSize(1.0)
gMean.SetMarkerColor(2)
gMean.SetLineColor(2)


# def myScale(x, par):
#    return par[0] + par[1] * x[0]
#
#
# fitFunc1 = ROOT.TF1("fitFunc1", myScale, 1.0, 35, 2)
# fitFunc1.SetParameters(0.0, 0.0)
# Fit the function to the data
# gMean.Fit(fitFunc1, "R")


gSigma.SetMarkerStyle(20)
gSigma.SetMarkerSize(1.0)
gSigma.SetMarkerColor(ROOT.kRed)
gSigma.SetLineColor(ROOT.kRed)


def myFunction(x, par):
    return np.sqrt(par[0]*par[0] + par[1]*par[1] / x[0])


# fitFunc = ROOT.TF1("fitFunc", myFunction, 3.0, 20, 2)
# fitFunc.SetParameters(3.0, 0.1)
# Fit the function to the data
# gSigma.Fit(fitFunc, "R")


def substractBeamResol(x, par):
    resol = fitFunc.Eval(x[0])
    return np.sqrt(resol*resol - 0.025 * 0.025)


def AddRunInfo(g):
    extraToDraws = []
    npoints = g.GetN()
    for i in range(npoints):
        x = np.array([0.])
        y = np.array([0.])
        g.GetPoint(i, x, y)
        runNum = runs[i]
        l = ROOT.TLatex(x, y, f"Run {int(runNum)}")
        l.SetTextSize(0.02)
        l.SetTextColor(2)
        l.SetTextAngle(20)
        extraToDraws.append(l)
    return extraToDraws


# fResol = ROOT.TF1("fResol", substractBeamResol, 3.0, 20, 0)
# fResol.SetLineColor(3)
# fResol.SetMarkerColor(3)
# fResol.SetLineWidth(4)
# fResol.SetLineStyle(3)


# def BNLResol(x, par):
#    a = 0.021
#    b = 0.081
#    return np.sqrt(a*a + b*b / x[0])
#
#
fBNLResol = ROOT.TF1(
    "fBNLResol", "sqrt(0.021*0.021 + 0.081*0.081/x)", 3.0, 20, 0)
fBNLResol.SetLineColor(4)
fBNLResol.SetMarkerColor(4)
fBNLResol.SetLineWidth(4)
fBNLResol.SetLineStyle(3)


extraToDraws = AddRunInfo(gMean)
DrawHistos([gMean], ["Data Mean"], 0, 35, "Energy [GeV]", 0,
           6e3, "Mean [ADCCount]", "fit_mean", dology=False, drawoptions="P", legendoptions="P", legendPos=[0.45, 0.80, 0.8, 0.85], nMaxDigits=3)

extraToDraws = AddRunInfo(gSigma)
DrawHistos([gSigma, fBNLResol], ["Data resolution", "BNL Testbeam Results"], 0, 35, "Energy [GeV]",
           0, 0.18, "#sigma/#mu", "fit_sigma", dology=False, drawoptions=["P", "L"], legendoptions=["P", "L"], legendPos=[0.45, 0.70, 0.8, 0.85],  extraToDraws=extraToDraws)
