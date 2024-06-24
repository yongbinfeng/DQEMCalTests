import ROOT
from .tdrStyle import setTDRStyle
import os


def AddOverflowsTH1(h1, dolastbin=True):
    assert isinstance(h1, ROOT.TH1), "input must be a ROOT.TH1"
    nbins = h1.GetNbinsX()
    if dolastbin:
        # merge overflow bin to the last bin
        h1.SetBinContent(nbins, h1.GetBinContent(
            nbins)+h1.GetBinContent(nbins+1))
        # treat the uncertainties as uncorrelated
        h1.SetBinError(nbins, ROOT.TMath.Sqrt(
            (h1.GetBinError(nbins))**2 + (h1.GetBinError(nbins+1))**2))
        # clean the old bins
        h1.SetBinContent(nbins + 1, 0)
        h1.SetBinError(nbins + 1, 0)
    else:
        h1.SetBinContent(1, h1.GetBinContent(0)+h1.GetBinContent(1))
        # treat the uncertainties as uncorrelated
        h1.SetBinError(1, ROOT.TMath.Sqrt(
            (h1.GetBinError(1))**2 + (h1.GetBinError(0))**2))
        # clean the old bins
        h1.SetBinContent(0, 0)
        h1.SetBinError(0, 0)


def AddOverflows(hinput, dolastbin=True):
    '''
    move the over/under flow bin to the last/first bin
    '''
    if isinstance(hinput, ROOT.TH1):
        AddOverflowsTH1(hinput, dolastbin)

    if isinstance(hinput, ROOT.THStack):
        # do the AddOverflowsTH1 for all the histograms in THStack
        hlist = list(hinput.GetHists())
        list(map(AddOverflowsTH1, hlist, [dolastbin]*len(hlist)))

    else:
        print("input must be a ROOT.TH1 or ROOT.THStack for Over/Underflows")


def DrawHistos(myhistos, mylabels, xmin, xmax, xlabel, ymin, ymax, ylabel, outputname, dology=True, showratio=False, dologx=False, lheader=None, donormalize=False, binomialratio=False, yrmax=2.0, yrmin=0.0, yrlabel=None, leftlegend=False, mycolors=None, legendPos=None, legendNCols=1, linestyles=None, markerstyles=None, showpull=False, ypullmin=-3.99, ypullmax=3.99, drawashist=False, padsize=(2, 0.9, 1.1), setGridx=False, setGridy=False, drawoptions=None, legendoptions=None, ratiooptions=None, dologz=False, ratiobase=0, redrawihist=-1, nMaxDigits=None, addOverflow=False, addUnderflow=False, hratiopanel=None, doratios=None, hpulls=None, W_ref=600, outdir="plots", savepdf=True, zmin=0, zmax=2, extraToDraws=[]):
    # python feature: for immutable objects, default values are evaluated only once
    # need to be cautious when using mutable objects as default values
    # https://docs.python.org/3/reference/compound_stmts.html#function-definitions
    if mycolors is None:
        mycolors = []
    if legendPos is None:
        legendPos = []
    if linestyles is None:
        linestyles = []
    if markerstyles is None:
        markerstyles = []
    if drawoptions is None:
        drawoptions = []
    if legendoptions is None:
        legendoptions = []
    if ratiooptions is None:
        ratiooptions = []

    # set the tdr style
    setTDRStyle()
    # not sure why need this...
    ROOT.gStyle.SetErrorX(0.5)

    ROOT.gStyle.SetPalette(1)
    ROOT.gStyle.SetPaintTextFormat(".1f")

    if nMaxDigits:
        # print(f"set the maximum number of digits {nMaxDigits}")
        ROOT.TGaxis.SetMaxDigits(nMaxDigits)
    else:
        # default val
        ROOT.TGaxis.SetMaxDigits(5)

    if ymax == None:
        ymax = max([h.GetMaximum() for h in myhistos]) * 1.25
    if ymin == None:
        ymin = min([h.GetMinimum() for h in myhistos]) * 0.75

    H_ref = 500
    W = W_ref
    H = H_ref

    npads = 1 + showratio + showpull

    if npads == 2:
        canvas = ROOT.TCanvas("c2"+outputname, "c2", 50, 50, W, 600)
        padsize1 = float(padsize[0])/(padsize[0]+padsize[1])
        padsize2 = float(padsize[1])/(padsize[0]+padsize[1])
        padsize3 = 0.
    elif npads == 1:
        canvas = ROOT.TCanvas("c2"+outputname, "c2", 50, 50, W, 600)
        canvas.SetGrid(setGridx, setGridy)
        canvas.SetTicks(1, 1)
        padsize1 = 1.0
        padsize2 = 0.
        padsize3 = 0.
        canvas.cd()
    else:
        canvas = ROOT.TCanvas("c2"+outputname, "c2", 50, 50, W, 800)
        padsize1 = float(padsize[0])/(padsize[0]+padsize[1]+padsize[2])
        padsize2 = float(padsize[1])/(padsize[0]+padsize[1]+padsize[2])
        padsize3 = float(padsize[2])/(padsize[0]+padsize[1]+padsize[2])

    if dology:
        # print "set y axis to log scale"
        canvas.SetLogy()
    if dologx:
        # print "set x axis to log scale"
        canvas.SetLogx()
    if dologz:
        # print "set z axis to log scale"
        canvas.SetLogz()

    if npads == 1:
        canvas.SetLeftMargin(0.15)
        canvas.SetBottomMargin(0.13)
        canvas.SetTopMargin(0.06)

        doth2 = False
        if isinstance(myhistos[0], ROOT.TH2):
            doth2 = True
            canvas.SetRightMargin(0.15)
            canvas.SetTopMargin(0.15)
            canvas.SetLeftMargin(0.12)
            canvas.SetBottomMargin(0.12)

    if npads == 2:
        pad1 = ROOT.TPad("pad1" + outputname, "pad1", 0, padsize2, 1, 1)
        pad2 = ROOT.TPad("pad2" + outputname, "pad1", 0, 0, 1, padsize2)
        pad1.SetTopMargin(0.06/padsize1)
        pad1.SetBottomMargin(0.012/padsize1)
        pad1.SetLeftMargin(0.15 * (600.0)/W)
        pad2.SetTopMargin(0.010/padsize2)
        pad2.SetBottomMargin(0.13/padsize2)
        pad2.SetLeftMargin(0.15 * (600.0)/W)
        pad2.SetGridy(1)
        pad2.SetTicks(1, 1)
        pad1.Draw()
        pad2.Draw()

    if npads == 3:
        pad1 = ROOT.TPad("pad1" + outputname, "pad1", 0, 1-padsize1, 1, 1)
        pad2 = ROOT.TPad("pad2" + outputname, "pad2",
                         0, padsize3, 1, 1-padsize1)
        pad3 = ROOT.TPad("pad3" + outputname, "pad3", 0, 0.,   1, padsize3)
        pad1.SetTopMargin(0.06/(padsize1+padsize3))
        pad1.SetBottomMargin(0.012/padsize1)
        pad1.SetLeftMargin(0.15 * (600.0)/W)
        pad2.SetTopMargin(0.010/padsize2)
        pad2.SetBottomMargin(0.02/padsize2)
        pad2.SetLeftMargin(0.15 * (600.0)/W)
        pad2.SetGridy(1)
        pad2.SetTicks(1, 1)
        pad3.SetTopMargin(0.01/padsize3)
        pad3.SetBottomMargin(0.13/padsize3)
        pad3.SetLeftMargin(0.15 * (600.0)/W)
        pad3.SetGridy(1)
        pad3.SetTicks(1, 1)
        pad1.Draw()
        pad2.Draw()
        pad3.Draw()

    if npads > 1:
        pad1.cd()
        pad1.SetGrid(setGridx, setGridy)
        pad1.SetTicks(1, 1)
        if dology:
            pad1.SetLogy()
        if dologx:
            pad1.SetLogx()

    if not doth2:
        h1 = ROOT.TH1F("h1" + outputname, "h1", 80, xmin, xmax)
        h1.SetMinimum(ymin)
        h1.SetMaximum(ymax)
    else:
        h1 = ROOT.TH2F("h2" + outputname, "h2", 80, xmin, xmax, 80, ymin, ymax)
        if zmin != None and zmax != None:
            print(f"configuring z range to {zmin}, {zmax}")
            h1.GetZaxis().SetRangeUser(zmin, zmax)

    # print "xmin : %f xmax : %f"%(xmin, xmax)

    h1.GetXaxis().SetNdivisions(6, 5, 0)
    h1.GetYaxis().SetNdivisions(6, 5, 0)
    h1.GetYaxis().SetTitle("%s" % ylabel)
    h1.GetYaxis().SetTitleSize(0.050/(padsize1+padsize3))
    h1.GetYaxis().SetLabelSize(0.045/(padsize1+padsize3))
    h1.GetXaxis().SetTitleSize(0.050/(padsize1+padsize3))
    h1.GetXaxis().SetLabelSize(0.045/(padsize1+padsize3))
    h1.GetYaxis().SetTitleOffset(1.2*(padsize1+padsize3)*(600.0/W))
    h1.GetXaxis().SetTitleOffset(1.1*(padsize1+padsize3))

    if showratio or showpull:
        h1.GetXaxis().SetLabelSize(0)
    else:
        h1.GetXaxis().SetTitle("%s" % xlabel)

    h1.Draw()

    x1_l = 0.92
    y1_l = 0.88

    # dx_l = 0.20
    dy_l = 0.22*0.66/padsize1
    dx_l = 0.35*0.66/padsize1
    x0_l = x1_l-dx_l
    y0_l = y1_l-dy_l

    if len(legendPos) == 4:
        x0_l = legendPos[0]
        y0_l = legendPos[1]
        x1_l = legendPos[2]
        y1_l = legendPos[3]

    if npads > 2:
        y1_l -= 0.03
        y0_l -= 0.03

    if not leftlegend:
        legend = ROOT.TLegend(x0_l, y0_l, x1_l, y1_l)
    else:
        legend = ROOT.TLegend(x0_l-0.40, y0_l, x1_l-0.40, y1_l)
    if lheader and lheader != "":
        legend.SetHeader(lheader)
    legend.SetNColumns(legendNCols)
    legend.SetBorderSize(0)
    legend.SetTextSize(0.04)
    legend.SetTextFont(42)
    legend.SetFillColor(0)

    myf = []

    myhistos_clone = []
    for ihisto in myhistos:
        # clone the histogram for plotting,
        # so the original histogram is unchanged
        ihcolone = ihisto.Clone("%s_Clone" % ihisto.GetName())
        # ihcolone.SetDirectory(0)
        myhistos_clone.append(ihcolone)

    if drawashist:
        drawoptions = ["HIST" for i in range(len(myhistos_clone))]
        legendoptions = ['L' for i in range(len(myhistos_clone))]

    if drawoptions and not isinstance(drawoptions, list):
        # copy the option n times
        tmp = [drawoptions for i in range(len(myhistos_clone))]
        drawoptions = tmp
    if not isinstance(legendoptions, list):
        tmp = [legendoptions for i in range(len(myhistos_clone))]
        legendoptions = tmp

    # print(("legend options ", legendoptions))

    ileg = 0
    for idx in range(0, len(myhistos_clone)):
        if addOverflow:
            # include overflow bin
            AddOverflows(myhistos_clone[idx])
        if addUnderflow:
            # include underflow bin
            AddOverflows(myhistos_clone[idx], dolastbin=False)
        if len(mycolors) == len(myhistos_clone):
            myhistos_clone[idx].SetLineColor(mycolors[idx])
            myhistos_clone[idx].SetMarkerColor(mycolors[idx])
        if len(linestyles) == len(myhistos_clone):
            myhistos_clone[idx].SetLineStyle(linestyles[idx])
        if len(markerstyles) == len(myhistos_clone):
            myhistos_clone[idx].SetMarkerStyle(markerstyles[idx])
        if isinstance(myhistos_clone[idx], ROOT.TH1):
            myhistos_clone[idx].SetLineWidth(3)
        # myhistos_clone[idx].GetXaxis().SetRangeUser(xmin, xmax)
        if donormalize:
            Normalize(myhistos_clone[idx])
        if idx >= len(drawoptions):
            drawoptions.append("EL")
        if idx >= len(legendoptions):
            if isinstance(myhistos_clone[idx], ROOT.TH1) and myhistos_clone[idx].GetMarkerStyle() != 1:
                legendoptions.append("LP")
            else:
                legendoptions.append("LE")
        if isinstance(myhistos_clone[idx], ROOT.THStack):
            drawoptions[idx] = 'HIST'
            legendoptions[idx] = "F"
        myhistos_clone[idx].Draw(
            " ".join(filter(None, [drawoptions[idx], "same"])))

        if ileg < len(mylabels):
            # number of labels might be different from number of histograms.
            # do the match logically
            if isinstance(myhistos_clone[idx], ROOT.THStack):
                hlist = list(myhistos_clone[idx].GetHists())
                for hist in reversed(hlist):
                    legend.AddEntry(
                        hist, str(mylabels[ileg]), legendoptions[idx])
                    ileg += 1
            else:
                legend.AddEntry(myhistos_clone[idx], str(
                    mylabels[ileg]), legendoptions[idx])
                ileg += 1

    # print("draw options ", drawoptions)
    # print("legend options ", legendoptions)

    if showratio and hratiopanel:
        legend.AddEntry(hratiopanel, "Uncertainty", "F")

    for extraToDraw in extraToDraws:
        extraToDraw.Draw("same")

    if redrawihist >= 0:
        myhistos_clone[redrawihist].Draw(
            " ".join(filter(None, [drawoptions[redrawihist], "same"])))

        pad1.Update()
        pad1.RedrawAxis()
        # frame = pad1.GetFrame()
        # frame.Draw()
        if len(mylabels) or lheader:
            legend.Draw()
        pad1.Update()

    else:
        canvas.cd()
        canvas.Update()
        canvas.RedrawAxis()
        canvas.RedrawAxis("G")
        # frame = canvas.GetFrame()
        # frame.Draw()
        if len(mylabels) or lheader:
            legend.Draw()
        canvas.Update()

    ##
    # ration plot
    ##
    if showratio or showpull:
        hden = myhistos_clone[ratiobase].Clone("hden_%s" % idx)

    if showratio:
        hratios = {}
        for idx in range(0, len(myhistos_clone)):
            if doratios != None and doratios[idx] == False:
                continue
            if idx == ratiobase:
                continue
            hratios[idx] = myhistos_clone[idx].Clone("hratios_%s" % idx)
            if binomialratio:
                hratios[idx].Divide(hratios[idx], hden, 1.0, 1.0, "b")
            else:
                hratios[idx].Divide(hden)

    if showpull:
        if hpulls == None:
            hpulls = []
            for idx in range(0, len(myhistos_clone)):
                if idx == ratiobase:
                    continue
                hpull = myhistos_clone[idx].Clone("hpullsnew_%s" % idx)
                hpulls.append(hpull)

    if npads > 1:
        pad2.cd()
        if dologx:
            pad2.SetLogx()

        h2 = ROOT.TH1F("h2", "h2", 80, xmin, xmax)
        h2.GetXaxis().SetTitleSize(0.050/(padsize2+0.3*padsize3))
        h2.GetXaxis().SetLabelSize(0.045/(padsize2+0.3*padsize3))
        h2.GetYaxis().SetTitleSize(0.050/(padsize2+0.3*padsize3))
        h2.GetYaxis().SetLabelSize(0.045/(padsize2+0.3*padsize3))
        h2.GetYaxis().SetTitleOffset(1.35*(padsize2+0.35*padsize3)*(600.0/W))

        h2.GetYaxis().SetNdivisions(8)
        h2.GetYaxis().CenterTitle()
        if yrlabel:
            ytitle = yrlabel
        elif showratio:
            ytitle = "Ratio"
        else:
            ytitle = "Pull"
        h2.GetYaxis().SetTitle(ytitle)
        h2.SetMaximum(yrmax if showratio else ypullmax)
        h2.SetMinimum(yrmin if showratio else ypullmin)

        if npads == 2:
            h2.GetXaxis().SetTitle("%s" % xlabel)
            h2.GetXaxis().SetTitleOffset(1.1)
        else:
            h2.GetXaxis().SetTitleSize(0.0)
            h2.GetXaxis().SetLabelSize(0)

        h2.Draw()

        if showratio:
            if hratiopanel:
                # print("draw hratiopanel")
                # hratiopanel.SetFillColor(15)
                hratiopanel.SetFillColorAlpha(15, 0.5)
                hratiopanel.SetLineColor(0)
                # hratiopanel.SetLineColor(2)
                hratiopanel.SetMarkerSize(0)
                hratiopanel.Draw("E2 same")
                # hratiopanel.Draw("HIST same")
                # for ibin in xrange(1, hratiopanel.GetNbinsX()+1):
                #    print("bin content ", hratiopanel.GetBinContent(ibin), " error ", hratiopanel.GetBinError(ibin))
                h2.Draw("same")
            idx = 0
            for hratio in list(hratios.values()):
                if idx >= len(ratiooptions):
                    if drawashist:
                        ratiooptions.append("HIST")
                    else:
                        ratiooptions.append("")
                hratio.SetFillColor(0)
                hratio.Draw(ratiooptions[idx] + " same")
                idx += 1
        elif showpull:
            for hpull in hpulls:
                hpull.Draw("HIST same")

        pad2.RedrawAxis("G")
        pad2.Update()

    if npads > 2:
        pad3.cd()
        if dologx:
            pad3.SetLogx()

        h3 = ROOT.TH1F("h3", "h3", 80, xmin, xmax)
        h3.GetXaxis().SetTitle("%s" % xlabel)
        h3.GetXaxis().SetTitleOffset(1.1)
        h3.GetXaxis().SetTitleSize(0.050/(padsize3+0.3*padsize2))
        h3.GetXaxis().SetLabelSize(0.045/(padsize3+0.3*padsize2))
        h3.GetYaxis().SetTitleSize(0.050/(padsize3+0.3*padsize2))
        h3.GetYaxis().SetLabelSize(0.045/(padsize3+0.3*padsize2))
        h3.GetYaxis().SetTitleOffset(1.35*(padsize3+0.35*padsize2)*(600.0/W))
        h3.GetYaxis().SetNdivisions(5)
        h3.GetYaxis().CenterTitle()
        # h3.GetYaxis().SetTitle("#frac{Obs. - Exp.}{Err}")
        h3.GetYaxis().SetTitle("Pull")

        h3.SetMaximum(ypullmax)
        h3.SetMinimum(ypullmin)
        h3.Draw()

        for hpull in hpulls:
            hpull.SetFillColorAlpha(2, 0.6)
            hpull.SetLineWidth(1)
            hpull.SetLineColor(1)
            hpull.Draw("HIST same")

        pad3.Update()

    canvas.Update()

    if "/" not in outputname:
        # path not included; by default put to plots/outputname
        outputname = outdir + "/" + outputname

    dirpath = outputname.rpartition('/')[0]
    if not os.path.exists(dirpath):
        print(f"Make the directory {dirpath}")
        os.makedirs(dirpath)

    if savepdf:
        # print("save plot to %s.pdf" % outputname)
        # canvas.Print("%s.C"%outputname)
        canvas.Print("%s.pdf" % outputname)
        canvas.Print("%s.png" % outputname)
        # canvas.Print("%s.root" % outputname)
    return hratios if showratio else None
