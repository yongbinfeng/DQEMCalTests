from modules.plotStyles import DrawHistos
import ROOT
import json
import numpy as np
import os


fBNLResol = ROOT.TF1(
    "fBNLResol", "sqrt(0.021*0.021 + 0.081*0.081/x)", 1.0, 32, 0)
fBNLResol.SetLineColor(4)
fBNLResol.SetMarkerColor(4)
fBNLResol.SetLineWidth(4)
fBNLResol.SetLineStyle(3)

fSTARResol = ROOT.TF1(
    "fSTARResol", "sqrt(0.0112*0.00112 + 0.115*0.115/x)", 1.0, 32, 0)
fSTARResol.SetLineColor(8)
fSTARResol.SetMarkerColor(8)
fSTARResol.SetLineWidth(4)
fSTARResol.SetLineStyle(3)


def AddOneGraph(fname, color, marker, label, offset=0):
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return None

    with open(fname, "r") as f:
        fitresults = json.load(f)

    runs = np.array(fitresults["runs"])

    energys = np.array(fitresults["energys"])
    # apply offset for plotting
    energys += offset
    mus = np.array(fitresults["mus"])
    muEs = np.array(fitresults["muEs"])
    sigmas = np.array(fitresults["sigmas"])
    sigmaEs = np.array(fitresults["sigmaEs"])

    gMean = ROOT.TGraphErrors(len(energys), energys, mus,
                              np.zeros(len(energys)), muEs)
    gSigma = ROOT.TGraphErrors(len(energys), energys,
                               sigmas, np.zeros(len(energys)), np.zeros(len(energys)))

    gMean.SetMarkerStyle(marker)
    gMean.SetMarkerSize(1.0)
    gMean.SetMarkerColor(color)
    gMean.SetLineColor(color)

    fitFunc1 = ROOT.TF1("fitFunc1", "[0] * x", 0, 35, 2)
    fitFunc1.SetParameters(0.0, 0.0)
    fitFunc1.SetLineColor(color)
    # Fit the function to the data
    gMean.Fit(fitFunc1, "R")

    gSigma.SetMarkerStyle(marker)
    gSigma.SetMarkerSize(1.0)
    gSigma.SetMarkerColor(color)
    gSigma.SetLineColor(color)

    fitFunc = ROOT.TF1("fitFunc", "[0] + [1] / x", 3.0, 20, 2)
    fitFunc.SetParameters(3.0, 0.1)
    fitFunc.SetLineColor(color)
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
            l.SetTextColor(color)
            l.SetTextAngle(20)
            extraToDraws.append(l)
        return extraToDraws

    suffix = label.replace(" ", "_")

    extraToDraws_mean = AddRunInfo(gMean)
    DrawHistos([gMean.Clone()], [label], 0, 35, "Energy [GeV]", 0,
               1e4, "Mean [ADCCount]", "fit_mean_"+suffix, dology=False, drawoptions=["P"], legendoptions=["P"], legendPos=[0.20, 0.80, 0.45, 0.85], nMaxDigits=3, extraToDraws=extraToDraws_mean)

    extraToDraws_sigma = AddRunInfo(gSigma)
    DrawHistos([gSigma.Clone(), fBNLResol, fSTARResol], [label, "BNL Testbeam Results", "STAR Results"], 0, 35, "Energy [GeV]",
               0, 0.18, "#sigma/#mu", "fit_sigma_"+suffix, dology=False, drawoptions=["P", "L", "L"], legendoptions=["P", "L", "L"], legendPos=[0.45, 0.70, 0.8, 0.85],  extraToDraws=extraToDraws_sigma)

    return gMean, gSigma


infos = [
    ("fitresults_Run493_544.json", 2, 20, "With Attenuator"),
    ("fitresults_Run563_612.json", 3, 21, "With Filter"),
    ("fitresults_Run642_654.json", 6, 22, "Without anything")
]

to_draws_means = []
to_draws_sigmas = []
legends = []

idx = 0
for fname, color, marker, label in infos:
    gMean, gSigma = AddOneGraph(
        "results/"+fname, color, marker, label, offset=idx*0.2)
    to_draws_means.append(gMean)
    to_draws_sigmas.append(gSigma)

    legends.append(label)
    idx += 1

nGraphs = len(to_draws_means)

# fResol = ROOT.TF1("fResol", substractBeamResol, 3.0, 20, 0)
# fResol.SetLineColor(3)
# fResol.SetMarkerColor(3)
# fResol.SetLineWidth(4)
# fResol.SetLineStyle(3)

DrawHistos(to_draws_means, legends, 0, 35, "Energy [GeV]", 0,
           1e4, "Mean [ADCCount]", "fit_mean", dology=False, drawoptions=["P"]*nGraphs, legendoptions=["P"]*nGraphs, legendPos=[0.20, 0.68, 0.45, 0.85], nMaxDigits=3)

DrawHistos(to_draws_sigmas+[fBNLResol, fSTARResol], legends + ["BNL Testbeam Results", "STAR Results"], 0, 35, "Energy [GeV]",
           0, 0.18, "#sigma/#mu", "fit_sigma", dology=False, drawoptions=["P"]*nGraphs+["L", "L"], legendoptions=["P"]*nGraphs+["L", "L"], legendPos=[0.45, 0.68, 0.8, 0.85])
