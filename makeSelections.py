import ROOT
import os, sys

def select(run):
    fname = f"root/Run{run}_list.root"
    if not os.path.exists(fname):
        print(f"File {fname} does not exist")
        return
    f = ROOT.TFile(fname)
    t = f.Get("save")
    nentries = t.GetEntries()
    
    # create a new file
    fout = ROOT.TFile(f"root_selected/Run{run}_list_selected.root","RECREATE")
    tout = t.CloneTree(0)
    
    nevts = 0
    for i in range(nentries):
        t.GetEntry(i)
        if sum(t.ch_lg) > 2800 and sum(t.ch_lg) < 3500:
            tout.Fill()
            nevts += 1
            
    tout.Write()
    fout.Close()
    f.Close()
    
    print(f"Selected {nevts} out of {nentries} events for Run {run}, efficiency = {nevts/nentries:.2f}")
    
if __name__ == "__main__":
    for i in range(350, 359):
        select(i)
    