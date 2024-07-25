from multiprocessing import Pool, current_process
from array import array
import ROOT
import sys
import os
sys.argv.append('-b')

ROOT.gROOT.SetBatch(True)

chlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
chlist_str = ["00", "01", "02", "03", "04", "05", "06",
              "07", "08", "09", "10", "11", "12", "13", "14", "15"]


def convertStrToVal(ch):
    if ch == "-":
        return 0
    else:
        return int(ch)


def makeROOT(run):
    # check if we are on sqtestbench.mit.edu
    if os.getenv('HOSTNAME') == 'sqtestbench':
        data_dir = '/storage/spinquest/emcal'
    else:
        # assume the user has made a local data directory 
        data_dir = 'data'
    # check if file exists
    if not os.path.exists(f"{data_dir}/Run{run}_list.txt"):
        print(f"File {data_dir}/Run{run}_list.txt does not exist")
        return

    pid = current_process().pid

    print(f"Making ROOT file for Run {run} with Process ID: {pid}")
    trigID = array('i', [0])
    trigTime = array('d', [0])
    ch_lg = ROOT.std.vector[int]()
    ch_hg = ROOT.std.vector[int]()

    fout = ROOT.TFile(f"root/Run{run}_list.root", "RECREATE")
    tout = ROOT.TTree("save", "save")
    tout.SetDirectory(fout)

    tout.Branch('trigID', trigID, 'trigID/I')
    tout.SetBranchAddress("trigID", trigID)

    tout.Branch('trigTime', trigTime, 'trigTime/D')
    tout.SetBranchAddress("trigTime", trigTime)

    tout.Branch('ch_lg', ch_lg)
    tout.SetBranchAddress("ch_lg", ch_lg)

    tout.Branch('ch_hg', ch_hg)
    tout.SetBranchAddress("ch_hg", ch_hg)

    nevents = 0

    with open(f"{data_dir}/Run{run}_list.txt") as infile:
        for line in infile:
            if ("//" in line):
                continue
            if ("Tstamp" in line):
                continue

            if ("1  00" in line and len(line.split()) == 7):
                trigID[0] = int(line.split()[5])
                trigTime[0] = float(line.split()[4])

            for ch in chlist:
                if ("1  "+chlist_str[ch] in line):
                    ch_lg.push_back(convertStrToVal(line.split()[2]))
                    ch_hg.push_back(convertStrToVal(line.split()[3]))

            if (ch_lg.size() == len(chlist)):
                tout.Fill()
                ch_lg.clear()
                ch_hg.clear()
                nevents += 1
                if (nevents % 10000 == 0):
                    print(
                        f"Process ID: {pid}, Run {run}, and processed {nevents} events")

    fout.cd()
    tout.Write()
    fout.Save()

    print(f"Total events: {nevents}")
    print(f"ROOT file saved as root/Run{run}_list.root with Process ID: {pid}")
    print("\n\n")


def worker(run):
    makeROOT(run)


if __name__ == "__main__":
    from modules.utils import parseRuns
    run_start, run_end = parseRuns()

    # see if output directory exists
    if not os.path.exists('./root/'):
        print('Output rootfile directory "root/" does not exist, please create first;\n\tmkdir ./root')
        exit()

    with Pool(16) as p:
        p.map(worker, range(run_start, run_end))
