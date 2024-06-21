# collection for all the functions that are used in the main script
import sys


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
    elif run >= 375 and run <= 436:
        return 8.0
    else:
        print(f"Run {run} not found")
        sys.exit(1)


def plotChSum(t, suffix):
    import ROOT
    from .plotStyles import DrawHistos

    h = ROOT.TH1F(f"h_{suffix}", "h", 500, 0, 10000)
    t.Draw(f"Sum$(ch_lg)>>h_{suffix}")

    vmax = h.GetMaximum()
    outname = f"Run{suffix}_sum_ch_lg"

    DrawHistos([h], ["Run "+str(suffix)], 0, 1e4, "Energy [ADC]", 0.1, vmax * 1e2,
               "Counts", outname, dology=True)
