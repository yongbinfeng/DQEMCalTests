import ROOT
import sys
import os
import numpy as np
import json

ROOT.gROOT.SetBatch(True)


if __name__ == "__main__":
    from modules.utils import parseRuns
    run_start, run_end = parseRuns()

    from modules.runinfo import runinfo, GetFitRange
    from modules.fitFunction import runFit

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
