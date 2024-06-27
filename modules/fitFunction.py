import numpy as np
import json
import ROOT
from .runinfo import GetEnergy, HasAttenuator, HasFilter, IsMuonRun
import os


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


def runFit(h, suffix, mean=3100.0, xmin=0.0, xmax=7500.0, xfitmin=2950.0, xfitmax=3400.0, be=1.0, hasAtten=False, outdir="plots/fits"):
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

    vmean = ROOT.RooRealVar("vmean_" + suffix, "vmean",
                            xmean, xmean-2*xrms, xmean+2*xrms, "ADCCount")
    vsigma = ROOT.RooRealVar("vsigma_" + suffix, "vsigma",
                             xrms, 0.1, 2*xrms, "ADCCount")
    pdf = ROOT.RooGaussian("pdf_" + suffix, "pdf", var, vmean, vsigma)

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
    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextColor(1)
    latex.SetTextSize(tsize)
    latex.SetTextFont(42)
    latex.DrawLatexNDC(0.20, 0.80, "#chi^{2}/ndf = %.2f" % (chi2))
    latex.DrawLatexNDC(0.20, 0.75, "#mu = %.2f #pm %.2f" %
                       (vmean.getVal(), vmean.getError()))
    latex.DrawLatexNDC(0.20, 0.70, "#sigma = %.2f #pm %.2f" %
                       (vsigma.getVal(), vsigma.getError()))
    latex.DrawLatexNDC(0.20, 0.65, "#sigma / #mu = %.1f%%" %
                       (vsigma.getVal()/vmean.getVal()*100.))

    # extra information
    run = int(suffix.split("_")[1])
    yval = 0.80
    xval = 0.70
    latex.DrawLatexNDC(xval, yval, f"Run {run}")
    yval -= 0.05
    latex.DrawLatexNDC(xval, yval, f"E = {GetEnergy(run)} GeV")
    yval -= 0.05
    if HasAttenuator(run):
        latex.DrawLatexNDC(xval, yval, "with attenuator")
        yval -= 0.05
    if HasFilter(run):
        latex.DrawLatexNDC(xval, yval, "with filter")
        yval -= 0.05
    if IsMuonRun(run):
        latex.DrawLatexNDC(xval, yval, "muon run")
        yval -= 0.05
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

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    c.SaveAs(f"{outdir}/fit_{suffix}.pdf")
    c.SaveAs(f"{outdir}/fit_{suffix}.png")

    print("nevents: ", h.Integral(0, h.GetNbinsX()+1))

    return (vmean.getVal(), vmean.getError()), (vsigma.getVal(), vsigma.getError())
