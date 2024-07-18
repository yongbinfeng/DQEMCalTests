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


def runMIPFit(h, suffix, xmin=0.0, xmax=7500.0, xfitmin=2950.0, xfitmax=3400.0, outdir="plots/MIPFits"):
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

    # crystal ball for signal
    vmean = ROOT.RooRealVar("vmean_" + suffix, "vmean",
                            xmean, xmean-2*xrms, xmean+2*xrms, "ADCCount")
    vsigmaL = ROOT.RooRealVar(
        "vsigmaL_" + suffix, "vsigmaL", xrms, 0.1, 1.5*xrms, "ADCCount")
    vsigmaR = ROOT.RooRealVar(
        "vsigmaR_" + suffix, "vsigmaR", xrms, 0.1, 2*xrms, "ADCCount")
    alphaL = ROOT.RooRealVar("alphaL_" + suffix, "alphaL", 1.0, 0.0, 10.0)
    alphaR = ROOT.RooRealVar("alphaR_" + suffix, "alphaR", 1.0, 0.0, 10.0)
    nL = ROOT.RooRealVar("nL_" + suffix, "nL", 1.0, 0.0, 10.0)
    nR = ROOT.RooRealVar("nR_" + suffix, "nR", 1.0, 0.0, 10.0)
    # pdf_sig = ROOT.RooCrystalBall("pdfsig_" + suffix, "pdfsig",
    #                              var, vmean, vsigmaL, vsigmaR, alphaL, nL, alphaR, nR)
    pdf_sig = ROOT.RooCrystalBall(
        "pdfsig_" + suffix, "pdfsig", var, vmean, vsigmaL, alphaL, nL, alphaR, nR)

    # exp for bkg
    v0 = ROOT.RooRealVar("v0_" + suffix, "v0", -0.0, -10.0, 0.0)
    pdf_bkg = ROOT.RooExponential("pdfbkg_" + suffix, "pdfbkg", var, v0)

    frac = ROOT.RooRealVar("frac_" + suffix, "frac", 0.5, 0.0, 1.0)
    pdf = ROOT.RooAddPdf("pdf_" + suffix, "pdf",
                         ROOT.RooArgList(pdf_sig, pdf_bkg), ROOT.RooArgList(frac))

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
    pdf.plotOn(frame, ROOT.RooFit.Components("pdfsig_" + suffix),
               ROOT.RooFit.LineStyle(2), ROOT.RooFit.LineColor(2))
    pdf.plotOn(frame, ROOT.RooFit.Components("pdfbkg_" + suffix),
               ROOT.RooFit.LineStyle(2), ROOT.RooFit.LineColor(3))
    pdf.plotOn(frame, ROOT.RooFit.LineStyle(1), ROOT.RooFit.LineColor(4))
    frame.SetTitle("EMCal Test beam")
    frame.GetXaxis().SetTitleSize(0.)
    frame.GetXaxis().SetLabelSize(0.)
    frame.GetYaxis().SetRangeUser(10.0, 100*datahist.sumEntries())
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
                       (vsigmaL.getVal(), vsigmaL.getError()))
    # latex.DrawLatexNDC(0.20, 0.65, "#sigmaR = %.2f #pm %.2f" %
    #                   (vsigmaR.getVal(), vsigmaR.getError()))
    latex.DrawLatexNDC(0.20, 0.65, "#sigma / #mu = %.1f%%" %
                       (vsigmaL.getVal()/vmean.getVal()*100.))

    # extra information
    def getRunNumber(suffix, isEnd=False):
        idx = 1 if not isEnd else 2
        run = suffix.split("_")[idx]
        if run.startswith("Run"):
            run = run[3:]
        return int(run)

    run_start = getRunNumber(suffix)
    run_end = getRunNumber(suffix, isEnd=True)
    runstr = f"Run {run_start}"
    if run_end != run_start:
        runstr += f" - {run_end}"
    yval = 0.80
    xval = 0.70
    latex.DrawLatexNDC(xval, yval, runstr)
    yval -= 0.05
    latex.DrawLatexNDC(xval, yval, f"E = {GetEnergy(run_start)} GeV")
    yval -= 0.05
    if HasAttenuator(run_start):
        latex.DrawLatexNDC(xval, yval, "with attenuator")
        yval -= 0.05
    if HasFilter(run_start):
        latex.DrawLatexNDC(xval, yval, "with filter")
        yval -= 0.05
    if IsMuonRun(run_start):
        latex.DrawLatexNDC(xval, yval, "muon run")
        yval -= 0.05
    chName = suffix.split("_")[-1]
    latex.DrawLatexNDC(xval, yval, f"Channel {chName}")
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
    frame2.GetYaxis().SetRangeUser(-4.2, 4.2)

    paddown.cd()
    frame2.Draw()

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    c.SaveAs(f"{outdir}/fit_{suffix}.pdf")
    c.SaveAs(f"{outdir}/fit_{suffix}.png")

    print("nevents: ", h.Integral(0, h.GetNbinsX()+1))

    return (vmean.getVal(), vmean.getError()), (vsigmaL.getVal(), vsigmaL.getError())
