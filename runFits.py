import ROOT
import sys


def runFit(h, suffix):
    xmin = h.GetXaxis().GetXmin()
    xmax = h.GetXaxis().GetXmax()
    xmean = h.GetMean()
    xrms = h.GetRMS()
    xbins = h.GetNbinsX()

    print("xmin = ", xmin)
    print("xmax = ", xmax)
    print("xmean = ", xmean)
    print("xrms = ", xrms)
    print("xbins = ", xbins)

    be = 1.0
    xfitmin = 2950 * be
    xfitmax = 3400 * be

    var = ROOT.RooRealVar("energy_" + suffix, "energy", xmin, 7500, "ADCCount")
    var.setRange("r1", xfitmin, xfitmax)
    datahist = ROOT.RooDataHist("datahist_" + suffix, "datahist",
                                ROOT.RooArgList(var, "argdatahist"), h)

    mean = ROOT.RooRealVar("mean_" + suffix,  "mean",   3000.0*be,
                           2500.*be,   3500.*be,   "GeV")
    sigma = ROOT.RooRealVar("sigma_" + suffix, "sigma",  250.0*be,
                            100.*be,  400.*be,   "GeV")
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


fname = "root_selected/Run_list_selected_calibrated.root"
# fname = "h_lgcl0_Run347_new4.root"
f = ROOT.TFile(fname)
hcal = f.Get("hcal")
hcal_unc = f.Get("hcal_unc")
hcal_reg = f.Get("hcal_reg")

runFit(hcal, "cal")
runFit(hcal_unc, "uncal")
runFit(hcal_reg, "reg")
