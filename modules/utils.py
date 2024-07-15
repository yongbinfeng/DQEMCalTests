# collection for all the functions that are used in the main script
import sys
import os
from collections import OrderedDict
from .runinfo import runinfo, GetFitRange, GetEnergy, GetTitle
from .plotStyles import DrawHistos
import ROOT


def plotChSum(t, suffix):
    energy = GetEnergy(suffix)
    be, atte, _, _ = runinfo[suffix]
    _, xmax, _, _ = GetFitRange(energy, atte)

    xmax = 5000

    h = ROOT.TH1F(f"h_{suffix}", "h", 500, 0, xmax)
    t.Draw(f"Sum$(ch_lg)>>h_{suffix}")

    vmax = h.GetMaximum()
    outname = f"Run{suffix}_sum_ch_lg"

    DrawHistos([h], ["Run "+str(suffix)], 0, xmax, "Energy [ADC]", 0.1, vmax * 1e2,
               "Counts", outname, dology=True, outdir="plots/ChSum")


def getChannelMap(chan):
    chanMap = {
        15: (0, 0),
        14: (0, 1),
        13: (1, 0),
        12: (1, 1),
        11: (0, 2),
        10: (0, 3),
        9: (1, 2),
        8: (1, 3),
        7: (2, 0),
        6: (2, 1),
        5: (3, 0),
        4: (3, 1),
        3: (2, 2),
        2: (2, 3),
        1: (3, 2),
        0: (3, 3)
    }
    return chanMap[chan]


def plotChMap(outdir="plots/ChMap"):
    """
    plot the channel map
    """
    h2D = ROOT.TH2F("h_Chs", "h", 4, -0.5, 3.5, 4, -0.5, 3.5)
    for ch in range(16):
        x, y = getChannelMap(ch)
        h2D.Fill(x, y, ch)

    DrawHistos([h2D], [], -0.5, 3.5, "X", -0.5, 3.5, "Y",
               "ChMap", dology=False, drawoptions="text", dologz=False, legendPos=(0.30, 0.87, 0.70, 0.97), lheader="Channel Map", outdir=outdir, zmin=0.0, zmax=15.0, textformat=".0f")


def plotCh2D(t, run, plotAvg=True, applySel=True):
    # use RDF such that the loop is only needed once
    rdf = ROOT.RDataFrame(t)

    energy = GetEnergy(run)

    if applySel:
        be, atte, _, _ = runinfo[run]
        _, _, fitmin, fitmax = GetFitRange(energy, atte)
        # fitmin and fitmax are basically the electron dominated region
        rdf = rdf.Define("ADCSum", "Sum(ch_lg)").Filter(
            f"ADCSum > {fitmin}").Filter(f'ADCSum < {fitmax}')

    nEvents = rdf.Count().GetValue()

    histos = OrderedDict()
    for ch in range(16):
        x, y = getChannelMap(ch)
        rdf = rdf.Define(f"x_{ch}", str(x)).Define(f"y_{ch}", str(
            y)).Define(f"count_{run}_{ch}", f"ch_lg[{ch}]")

        histos[ch] = rdf.Histo2D(
            (f"h_Chs_{run}_{ch}", "h", 4, -0.5, 3.5, 4, -0.5, 3.5), f"x_{ch}", f"y_{ch}", f"count_{run}_{ch}")

    h2D = ROOT.TH2F(f"h_Chs_{run}", "h", 4, -0.5, 3.5, 4, -0.5, 3.5)
    for ch in range(16):
        h2D.Add(histos[ch].GetValue())

    if plotAvg:
        h2D.Scale(1.0 / (nEvents+0.001))

    leg = f"Run {run}, E = {GetEnergy(run)} GeV"

    DrawHistos([h2D], [], -0.5, 3.5, "X", -0.5, 3.5, "Y",
               f"Run{run}_ch_lg_2D", dology=False, drawoptions="colz,text", dologz=True, legendPos=(0.30, 0.87, 0.70, 0.97), lheader=leg, outdir="plots/Ch2D", zmin=1.0, zmax=2e3)


def plotCh1D(t, suffix, plotAvg=True, applySel=False, makePlots=True, xmin=0, xmax=1000, xbins=100):
    rdf = ROOT.RDataFrame(t)

    energy = GetEnergy(suffix)

    if applySel:
        be, atte = runinfo[suffix]
        _, _, fitmin, fitmax = GetFitRange(energy, atte)
        rdf = rdf.Define("ADCSum", "Sum(ch_lg)").Filter(
            f"ADCSum > {fitmin}").Filter(f'ADCSum < {fitmax}')

    nEvents = rdf.Count().GetValue()

    histos_hg = OrderedDict()
    histos_lg = OrderedDict()
    for ch in range(16):
        rdf = rdf.Define(f"ch_hg_{ch}", f"ch_hg[{ch}]").Define(
            f"ch_lg_{ch}", f"ch_lg[{ch}]")
        histos_hg[ch] = rdf.Histo1D(
            (f"h_Chs_hg_{suffix}_{ch}", "h", xbins, xmin, xmax), f"ch_hg_{ch}")
        histos_lg[ch] = rdf.Histo1D(
            (f"h_Chs_lg_{suffix}_{ch}", "h", xbins, xmin, xmax), f"ch_lg_{ch}")

    if plotAvg:
        for ch in range(16):
            histos_hg[ch].Scale(1.0 / (nEvents+0.001))
            histos_lg[ch].Scale(1.0 / (nEvents+0.001))

    if makePlots:
        # make the actual plots
        title = GetTitle(suffix)

        ltitle = ROOT.TLatex(0.20, 0.95, title)
        ltitle.SetNDC()
        ltitle.SetTextFont(42)
        ltitle.SetTextSize(0.04)

        mycolors = [15 + i*5 for i in range(16)]

        DrawHistos([histos_hg[ch].GetValue() for ch in range(16)], [f"Ch {ch}" for ch in range(16)], xmin, xmax, "High Gain ADC", 1e-6, 1e3, "Counts",
                   f"Run{suffix}_ch_hg_1D", dology=True, outdir="plots/Ch1D/hg", legendPos=(0.35, 0.70, 0.90, 0.90), mycolors=mycolors, extraToDraws=[ltitle], legendNCols=4, addOverflow=True)
        DrawHistos([histos_lg[ch].GetValue() for ch in range(16)], [f"Ch {ch}" for ch in range(16)], xmin, xmax, "Low Gain ADC", 1e-6, 1e3, "Counts",
                   f"Run{suffix}_ch_lg_1D", dology=True, outdir="plots/Ch1D/lg", legendPos=(0.35, 0.70, 0.90, 0.90), mycolors=mycolors, extraToDraws=[ltitle], legendNCols=4, addOverflow=True)

    for ch in range(16):
        histos_hg[ch] = histos_hg[ch].GetValue()
        histos_hg[ch].SetDirectory(0)
        histos_lg[ch] = histos_lg[ch].GetValue()
        histos_lg[ch].SetDirectory(0)

    return histos_hg, histos_lg


def plotWeight(run):
    """
    plot the weights from the regression.
    works only for regressed files with CNN
    """
    fname = f"regressed/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return
    f = ROOT.TFile(fname)
    h2D = f.Get("hweights")
    DrawHistos([h2D], [], -0.5, 3.5, "X", -0.5, 3.5, "Y", f"Run{run}_weights", dology=False, drawoptions="colz,text,ERROR", dologz=False, legendPos=(
        0.30, 0.87, 0.70, 0.97), lheader=f"Run {run}, E = {GetEnergy(run)} GeV", outdir="plots/Weights", zmin=0.70, zmax=1.10)


def parseRuns():
    import argparse
    parser = argparse.ArgumentParser(description="Make ROOT files")
    parser.add_argument("-s", "--start", type=int,
                        default=329, help="Run number to start")
    parser.add_argument("-e", "--end", type=int,
                        default=528, help="Run number to end")
    args, unknown = parser.parse_known_args()
    run_start, run_end = args.start, args.end + 1
    print(f"Selecting runs from {run_start} to {run_end-1}")
    return run_start, run_end
