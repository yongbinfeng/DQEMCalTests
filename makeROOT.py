from array import array
from ROOT import *
import sys
import os
sys.argv.append('-b')

gROOT.SetBatch(True)

chlist = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
chlist_str = ["00", "01", "02", "03", "04", "05", "06",
              "07", "08", "09", "10", "11", "12", "13", "14", "15"]
ch_calib = [203.7,
            190.8,
            192.3,
            201.1,
            199.1,
            207.2,
            196.2,
            218.2,
            199.0,
            201.0,
            203.7,
            203.7,
            192.9,
            187.7,
            186.5,
            181.5
            ]
calib_mean = sum(ch_calib)/len(ch_calib)


def makeROOT(run):
    # check if file exists
    if not os.path.exists(f"data/Run{run}_list.txt"):
        print(f"File data/Run{run}_list.txt does not exist")
        return

    print(f"Making ROOT file for Run {run}")
    trigID = array('i', [0])
    trigTime = array('d', [0])
    ch_lg = std.vector[int]()
    ch_hg = std.vector[int]()
    ch_lg_calib = std.vector[float]()

    fout = TFile(f"root/Run{run}_list.root", "RECREATE")
    tout = TTree("save", "save")
    tout.SetDirectory(fout)

    tout.Branch('trigID', trigID, 'trigID/I')
    tout.SetBranchAddress("trigID", trigID)

    tout.Branch('trigTime', trigTime, 'trigTime/D')
    tout.SetBranchAddress("trigTime", trigTime)

    tout.Branch('ch_lg', ch_lg)
    tout.SetBranchAddress("ch_lg", ch_lg)

    tout.Branch('ch_hg', ch_hg)
    tout.SetBranchAddress("ch_hg", ch_hg)

    tout.Branch('ch_lg_calib', ch_lg_calib)
    tout.SetBranchAddress("ch_lg_calib", ch_lg_calib)

    nevents = 0

    with open(f"data/Run{run}_list.txt") as infile:

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
                    ch_lg.push_back(int(line.split()[2]))
                    ch_hg.push_back(int(line.split()[3]))
                    ch_lg_calib.push_back(
                        int(line.split()[2])*ch_calib[ch]/calib_mean)

            if (ch_lg.size() == len(chlist)):
                tout.Fill()
                ch_lg.clear()
                ch_hg.clear()
                ch_lg_calib.clear()
                nevents += 1
                if (nevents % 1000 == 0):
                    print(nevents)

    fout.cd()
    tout.Write()
    fout.Save()

    print(f"Total events: {nevents}")
    print(f"ROOT file saved as root/Run{run}_list.root")
    print("\n\n")


for run in range(430, 520):
    makeROOT(run)
