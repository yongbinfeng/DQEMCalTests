import ROOT
import os
import sys

ROOT.gROOT.SetBatch(True)


def select(run):
    fname = f"root/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return
    f = ROOT.TFile(fname)
    t = f.Get("save")
    nentries = t.GetEntries()

    # make plots of sum of ch_lg
    h = ROOT.TH1F(f"h_{run}", "h", 500, 0, 10000)
    t.Draw(f"Sum$(ch_lg)>>h_{run}")
    c = ROOT.TCanvas(f"c_{run}", f"c_{run}", 800, 600)
    c.SetLogy()
    h.SetTitle(f"Run {run}")
    h.GetXaxis().SetTitle("Energy [ADC]")
    h.GetYaxis().SetTitle("Counts")
    h.Draw()
    c.SaveAs(f"plots/Run{run}_sum_ch_lg.png")

    # create a new file
    fout = ROOT.TFile(f"root_selected/Run{run}_list_selected.root", "RECREATE")
    tout = t.CloneTree(0)

    nevts = 0
    for i in range(nentries):
        t.GetEntry(i)
        if sum(t.ch_lg) > 2600 and sum(t.ch_lg) < 3400:
            tout.Fill()
            nevts += 1

    tout.Write()
    fout.Close()
    f.Close()

    print(
        f"Selected {nevts} out of {nentries} events for Run {run}, efficiency = {nevts/nentries:.2f}")


if __name__ == "__main__":
    for i in range(360, 370):
        select(i)
