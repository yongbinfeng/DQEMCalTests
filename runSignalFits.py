import ROOT
import sys
import os
from collections import OrderedDict
import numpy as np
import json

ROOT.gROOT.SetBatch(True)


def runFit(h, suffix, mean=3100.0, xmin=0.0, xmax=7500.0, xfitmin=2950.0, xfitmax=3400.0, be=1.0, hasAtten=False):
    xmean = h.GetMean()
    xrms = h.GetRMS()
    xbins = h.GetNbinsX()

    if hasAtten:
        atte = 0.33
    else:
        atte = 1.0

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

    c.SaveAs(f"plots/fits/fit_{suffix}.pdf")
    c.SaveAs(f"plots/fits/fit_{suffix}.png")

    print("nevents: ", h.Integral(0, h.GetNbinsX()+1))

    return (mean.getVal(), mean.getError()), (sigma.getVal(), sigma.getError())


if __name__ == "__main__":
    from modules.utils import parseRuns
    run_start, run_end = parseRuns()

    from modules.runinfo import runinfo, GetFitRange

    runs = []
    energys = []
    mus = []
    muEs = []
    sigmas = []
    sigmaEs = []

    for run in range(run_start, run_end):
        fname = f"regressed/Run{run}_list.root"

        if not os.path.exists(fname):
            print(f"File {fname} does not exist")
            continue

        if run not in runinfo:
            print(f"Run {run} not in run info")
            continue

        be, hasAtten = runinfo[run]
        print(f"Run {run} has energy {be*8.0} GeV and attenuation {hasAtten}")
        fitranges = GetFitRange(be*8.0, hasAtten)
        print(f"Fit ranges: {fitranges}")

        f = ROOT.TFile(fname)
        hcal = f.Get("hcal")
        hcal_linear = f.Get("hcal_linear")
        hcal_unc = f.Get("hcal_unc")

        energy = be * 8.0
        if energy == 8.0:
            hcal.Rebin(2)
            hcal_linear.Rebin(2)
            hcal_unc.Rebin(2)
        elif energy == 12.0:
            hcal.Rebin(4)
            hcal_linear.Rebin(4)
            hcal_unc.Rebin(4)
        elif energy >= 20.0:
            hcal.Rebin(5)
            hcal_linear.Rebin(5)
            hcal_unc.Rebin(5)

        (mu, muE), (sigma, sigmaE) = runFit(hcal, f"cal_{run}", xmin=fitranges[0], xmax=fitranges[1],
                                            xfitmin=fitranges[2], xfitmax=fitranges[3], be=be, hasAtten=hasAtten)
        runFit(hcal_linear, f"linear_{run}",
               xmin=fitranges[0], xmax=fitranges[1], xfitmin=fitranges[2], xfitmax=fitranges[3], be=be, hasAtten=hasAtten)
        runFit(hcal_unc, f"uncal_{run}", xmin=fitranges[0], xmax=fitranges[1],
               xfitmin=fitranges[2], xfitmax=fitranges[3], be=be, hasAtten=hasAtten)

        runs.append(run)
        energys.append(energy)
        mus.append(mu)
        muEs.append(muE)
        sigmas.append(sigma / mu)
        sigmaEs.append(sigmaE / mu)

    fitresults = {
        "runs": runs,
        "energys": energys,
        "mus": mus,
        "muEs": muEs,
        "sigmas": sigmas,
        "sigmaEs": sigmaEs
    }

    with open("fitresults.json", "w") as f:
        json.dump(fitresults, f)

    print("energys = ", energys)
    print("mus = ", mus)
    print("muEs = ", muEs)
    print("sigmas = ", sigmas)
    print("sigmaEs = ", sigmaEs)
