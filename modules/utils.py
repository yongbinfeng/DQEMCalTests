# collection for all the functions that are used in the main script
import sys
from collections import OrderedDict


def getEnergy(run):
    if run <= 369:
        return 8.0
    elif run == 370:
        return 4.0
    elif run == 371:
        return 12.0
    elif run == 372:
        return 16.0
    elif run == 373:
        return 30.0
    elif run == 374:
        return 2.0
    elif run >= 375 and run <= 491:
        return 8.0
    elif run == 492:
        return 8.0
    elif run >= 493 and run <= 495:
        return 4
    elif run == 496:
        return 8.0
    elif run >= 498 and run <= 499:
        return 16.0
    elif run >= 500 and run <= 507:
        return 8.0
    elif run == 508:
        print("Caution Caution Caution. This is muon mode")
        return 8.0
    elif run >= 509 and run <= 513:
        return 8.0
    elif run >= 514 and run <= 515:
        return 3.0
    elif run >= 516 and run <= 517:
        return 30.0
    elif run >= 521 and run <= 526:
        print("Caution Caution Caution. This is muon mode")
        return 30.0
    else:
        print(f"Run {run} not found in the energy information collector")
        sys.exit(1)


def plotChSum(t, suffix):
    import ROOT
    from .plotStyles import DrawHistos

    h = ROOT.TH1F(f"h_{suffix}", "h", 500, 0, 10000)
    t.Draw(f"Sum$(ch_lg)>>h_{suffix}")

    vmax = h.GetMaximum()
    outname = f"Run{suffix}_sum_ch_lg"

    DrawHistos([h], ["Run "+str(suffix)], 0, 1e4, "Energy [ADC]", 0.1, vmax * 1e2,
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


def plotCh2D(t, suffix, plotAvg=True):
    import ROOT
    from .plotStyles import DrawHistos

    # use RDF such that the loop is only needed once
    rdf = ROOT.RDataFrame(t)

    histos = OrderedDict()
    for ch in range(16):
        x, y = getChannelMap(ch)
        rdf = rdf.Define(f"x_{ch}", str(x)).Define(f"y_{ch}", str(
            y)).Define(f"count_{suffix}_{ch}", f"ch_lg[{ch}]")
        histos[ch] = rdf.Histo2D(
            (f"h_Chs_{suffix}_{ch}", "h", 4, -0.5, 3.5, 4, -0.5, 3.5), f"x_{ch}", f"y_{ch}", f"count_{suffix}_{ch}")

    h2D = ROOT.TH2F(f"h_Chs_{suffix}", "h", 4, -0.5, 3.5, 4, -0.5, 3.5)
    for ch in range(16):
        h2D.Add(histos[ch].GetValue())

    if plotAvg:
        h2D.Scale(1.0 / (t.GetEntries()+0.001))

    leg = f"Run {suffix}, E = {getEnergy(suffix)} GeV"

    DrawHistos([h2D], [], -0.5, 3.5, "X", -0.5, 3.5, "Y",
               f"Run{suffix}_ch_lg_2D", dology=False, drawoptions="colz,text", dologz=True, legendPos=(0.30, 0.87, 0.70, 0.97), lheader=leg, outdir="plots/Ch2D", zmin=1.0, zmax=2e3)


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
