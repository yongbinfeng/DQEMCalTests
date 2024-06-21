import ROOT
import sys
import os
from collections import OrderedDict
import numpy as np
import json


def runFit(h, suffix, mean=3100.0, xmin=0.0, xmax=7500.0, xfitmin=2950.0, xfitmax=3400.0, be=1.0, atte=1.0):
    xmean = h.GetMean()
    xrms = h.GetRMS()
    xbins = h.GetNbinsX()

    print("xmean = ", xmean)
    print("xrms = ", xrms)
    print("xbins = ", xbins)

    var = ROOT.RooRealVar("energy_" + suffix, "energy", xmin, xmax, "ADCCount")
    var.setRange("r1", xfitmin, xfitmax)
    datahist = ROOT.RooDataHist("datahist_" + suffix, "datahist",
                                ROOT.RooArgList(var, "argdatahist"), h)

    mean = ROOT.RooRealVar("mean_" + suffix,  "mean",   3000.0*be*atte,
                           2400.*be*atte,   3600.*be*atte,   "GeV")
    sigma = ROOT.RooRealVar("sigma_" + suffix, "sigma",  250.0*be*atte,
                            50.*be*atte,  400.*be*atte,   "GeV")
    pdf = ROOT.RooGaussian("pdf_" + suffix, "pdf", var, mean, sigma)

    # run the fit
    pdf.fitTo(datahist, ROOT.RooFit.Range("r1"))

    # make plots
    tsize = 0.045

    ROOT.gStyle.SetPadLeftMargin(0.14)
    ROOT.gStyle.SetPadRightMargin(0.04)
    c = ROOT.TCanvas("c_" + suffix, "c", 800, 1000)
    c.SetLeftMargin(0.15)
    c.SetRightMargin(0.05)
    padsize1 = 0.67
    padsize2 = 0.33
    paddown = ROOT.TPad('bottompad_' + suffix,
                        'bottompad', 0.0, 0.0, 1, padsize2)
    padtop = ROOT.TPad('toppad_' + suffix, 'toppad', 0.0, padsize2, 1, 1)
    padtop.SetTopMargin(0.05*0.667/(padsize1*padsize1))
    padtop.SetBottomMargin(0.012/padsize1)
    paddown.SetTopMargin(0.010/padsize2)
    paddown.SetBottomMargin(0.13/padsize2)
    paddown.SetGridy(1)
    c.cd()
    paddown.Draw()
    padtop.Draw()

    padtop.cd()
    padtop.SetLogy()
    frame = var.frame()
    frame.GetXaxis().SetTitle("energy [ADCCount]")
    datahist.plotOn(frame)
    pdf.plotOn(frame)
    frame.SetTitle("EMCal Test beam")
    frame.GetXaxis().SetTitleSize(0.)
    frame.GetXaxis().SetLabelSize(0.)
    frame.GetYaxis().SetRangeUser(1.0, datahist.sumEntries())
    frame.GetYaxis().SetLabelSize(tsize)
    frame.GetYaxis().SetTitleSize(tsize*1.25)
    frame.GetYaxis().SetTitleOffset(1.1)
    frame.Draw()

    chi2 = frame.chiSquare()
    ndf = frame.GetNbinsX() - 2
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextSize(tsize)
    latex.SetTextFont(42)
    latex.DrawLatexNDC(0.20, 0.80, "#chi^{2}/ndf = %.2f" % (chi2))
    latex.DrawLatexNDC(0.20, 0.75, "#mu = %.2f #pm %.2f" %
                       (mean.getVal(), mean.getError()))
    latex.DrawLatexNDC(0.20, 0.70, "#sigma = %.2f #pm %.2f" %
                       (sigma.getVal(), sigma.getError()))
    latex.DrawLatexNDC(0.20, 0.65, "#sigma / #mu = %.1f%%" %
                       (sigma.getVal()/mean.getVal()*100.))

    # extra information
    run = int(suffix.split("_")[1])
    energy = be * 8.0
    latex.DrawLatexNDC(0.65, 0.80, f"Run {run}")
    latex.DrawLatexNDC(0.65, 0.75, f"E = {energy} GeV")
    frame.addObject(latex)

    # make pull histograms
    hpull = frame.pullHist()
    frame2 = var.frame()
    frame2.SetTitle("")
    frame2.addPlotable(hpull, "P")
    frame2.GetXaxis().SetTitle("Energy [ADCCount]")
    frame2.GetYaxis().SetTitle("Pull")
    frame2.GetYaxis().CenterTitle()
    frame2.GetYaxis().SetNdivisions(505)
    frame2.GetYaxis().SetLabelSize(tsize*2)
    frame2.GetYaxis().SetTitleSize(tsize*2.5)
    frame2.GetYaxis().SetTitleOffset(0.5)
    frame2.GetXaxis().SetTitleOffset(1.2)
    frame2.GetXaxis().SetLabelSize(tsize*2)
    frame2.GetXaxis().SetTitleSize(tsize*2.5)

    paddown.cd()
    frame2.Draw()

    c.SaveAs(f"plots/fit_{suffix}.pdf")
    c.SaveAs(f"plots/fit_{suffix}.png")

    print("nevents: ", h.Integral(0, h.GetNbinsX()+1))

    return (mean.getVal(), mean.getError()), (sigma.getVal(), sigma.getError())


fitmin = 2850.0
fitmax = 3600.0

fitranges = {
    370: (0.0, 3500.0, 1350.0, 1850.0, 0.5, 1.0),
    371: (2000.0, 7000.0, 4500, 5200.0, 1.5, 1.0),
    372: (4000.0, 8000.0, 6000.0, 7200.0, 2.0, 1.0),
    373: (6000.0, 14000.0, fitmin * 30.0 / 8.0, fitmax * 30.0 / 8.0, 30.0 / 8.0, 1.0),
    374: (0, 2000.0, fitmin / 4.0, fitmax / 4.0, 0.25, 1.0),
    375: (1000.0, 6000.0, fitmin, fitmax, 1.0, 1.0),
    376: (1000.0, 6000.0, fitmin, fitmax, 1.0, 1.0),
    377: (1000.0, 6000.0, fitmin, fitmax, 1.0, 1.0),
    378: (1000.0, 6000.0, fitmin, fitmax, 1.0, 1.0),
    379: (1000.0, 6000.0, fitmin, fitmax, 1.0, 1.0),

    500: (0.0, 2000.0, 1100.0, 1400.0, 1.0, 0.4),
    501: (0.0, 2000.0, 1100.0, 1400.0, 1.0, 0.4),
    502: (0.0, 2000.0, 1100.0, 1400.0, 1.0, 0.4),
    503: (0.0, 2000.0, 1100.0, 1400.0, 1.0, 0.4),
    504: (0.0, 2000.0, 1100.0, 1400.0, 1.0, 0.4),
    505: (0.0, 2000.0, 1100.0, 1400.0, 1.0, 0.4),
    506: (0.0, 2000.0, 1100.0, 1400.0, 1.0, 0.4),
    507: (0.0, 2000.0, 1100.0, 1400.0, 1.0, 0.4),
}

mus = OrderedDict()
muEs = OrderedDict()
sigmas = OrderedDict()
sigmaEs = OrderedDict()

for run in range(500, 508):
    fname = f"regressed/Run{run}_list.root"

    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        continue

    f = ROOT.TFile(fname)
    hcal = f.Get("hcal")
    hcal_unc = f.Get("hcal_unc")

    (mu, muE), (sigma, sigmaE) = runFit(hcal, f"cal_{run}", xmin=fitranges[run][0], xmax=fitranges[run][1],
                                        xfitmin=fitranges[run][2], xfitmax=fitranges[run][3], be=fitranges[run][4], atte=fitranges[run][5])
    runFit(hcal_unc, f"uncal_{run}", xmin=fitranges[run][0], xmax=fitranges[run][1],
           xfitmin=fitranges[run][2], xfitmax=fitranges[run][3], be=fitranges[run][4], atte=fitranges[run][5])

    energy = fitranges[run][4] * 8.0
    mus[energy] = mu
    muEs[energy] = muE
    sigmas[energy] = sigma / mu
    sigmaEs[energy] = sigmaE / mu

energys = np.array(list(mus.keys()))
mus = np.array(list(mus.values()))
muEs = np.array(list(muEs.values()))
sigmas = np.array(list(sigmas.values()))
sigmaEs = np.array(list(sigmaEs.values()))

fitresults = {
    "energys": energys.tolist(),
    "mus": mus.tolist(),
    "muEs": muEs.tolist(),
    "sigmas": sigmas.tolist(),
    "sigmaEs": sigmaEs.tolist()
}

with open("fitresults.json", "w") as f:
    json.dump(fitresults, f)

print("energys = ", energys)
print("mus = ", mus)
print("muEs = ", muEs)
print("sigmas = ", sigmas)
print("sigmaEs = ", sigmaEs)
