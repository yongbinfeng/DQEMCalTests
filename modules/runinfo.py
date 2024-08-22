import sys
import copy


def GetFitRange(energy, hasAtten, hasFilter, isLinearRegression=False):
    fitmin = 2850.0
    fitmax = 3600.0
    fitranges = {
        # (energy, hasAtten, hasFilter): (min, max, fitmin, fitmax)
        (8,  0, 0): (1000.0, 6000.0, 2850, 3800),
        (4,  0, 0): (0., 3500.0, 1350.0, 1850.0),
        (12, 0, 0): (2000.0, 7000.0, 4500, 5200.),
        (16, 0, 0): (4000.0, 8000.0, 6500.0, 7400.0),
        (30, 0, 0): (6000.0, 14000.0, fitmin * 30.0 / 8.0, fitmax * 30.0 / 8.0),
        (2,  0, 0): (0.0, 2000.0, fitmin/4.0, fitmax/4.0),
        (3,  0, 0): (0.0, 800.0, fitmin / 4.0, fitmax / 4.0),
        (30, 0, 0): (2000.0, 5000.0, 3300.0, 4300.0),

        (2,  1, 0): (0.0, 600.0, 180.0, 350.0),
        (3,  1, 0): (0.0, 800.0, 330.0, 550.0),
        (4,  1, 0): (0.0, 1000.0, 400.0, 680.0),
        (8,  1, 0): (0.0, 1500.0, 950.0, 1250.0),
        (12, 1, 0): (600.0, 2200.0, 1550.0, 1950.0),
        (16, 1, 0): (8000.0, 3000.0, 1800.0, 2300.0),
        (20, 1, 0): (1000.0, 3800.0, 2700.0, 3300.0),
        (30, 1, 0): (2500.0, 5500.0, 4000.0, 4800.0),

        (2,  0, 1): (0.0, 600.0, 230.0, 460.0),
        (3,  0, 1): (0.0, 800.0, 290.0, 430.0),
        (4,  0, 1): (0.0, 1200.0, 600.0, 950.0),
        (8,  0, 1): (0.0, 2500.0, 1300.0, 1800.0),
        (12, 0, 1): (600.0, 2200.0, 1300.0, 1650.0),
        (16, 0, 1): (1500.0, 4000.0, 2800.0, 3500.0),
        (20, 0, 1): (2500.0, 5000.0, 3700.0, 4400.0),
        (30, 0, 1): (3500.0, 8000.0, 5400.0, 6500.0),

        (120, 0, 0): (20000.0, 50000.0, 30000.0, 40000.0),
        (120, 1, 0): (20000.0, 50000.0, 30000.0, 40000.0),
        (120, 0, 1): (20000.0, 50000.0, 30000.0, 40000.0),
    }
    fit_ranges_linear = copy.deepcopy(fitranges)
    fit_ranges_linear[(4, 1, 0)] = (0.0, 1000.0, 400.0, 670.0)
    fit_ranges_linear[(8, 1, 0)] = (0.0, 1500.0, 800.0, 1200.0)
    fit_ranges_linear[(3, 1, 0)] = (0.0, 800.0, 300.0, 480.0)

    try:
        if isLinearRegression:
            return fit_ranges_linear[(energy, hasAtten, hasFilter)]
        return fitranges[(energy, hasAtten, hasFilter)]
    except KeyError:
        print(
            f"Energy {energy}, hasAttenuation {hasAtten}, and hasFilter {hasFilter} not found in fitranges")
        return None


def GetSelectionRange(energy, hasAtten, hasFilter):
    """
    return the sum(ch_lg) range of the Gaussian part, which corresponds to the electron energy deposit,
    in the events. Then used for (non)linear regression
    """
    selections = {
        (8, 0, 0): (2000.0, 3500.0),
        (8, 1, 0): (900.0, 1200.0),
        (8, 0, 1): (1000.0, 1450.0)
    }
    try:
        return selections[(energy, hasAtten, hasFilter)]
    except KeyError:
        print(
            f"Energy {energy}, hasAttenuation {hasAtten}, and hasFilter {hasFilter} not found in selections")
        return None


def GetRegressionGoal(run):
    """
    return the target energy for the linear regression
    """
    goals = {
        (8, 1, 0): 1000.0,
        (8, 0, 0): 2700.0,
        (8, 0, 1): 1200.0,
    }
    energy = GetEnergy(run)
    hasAtten = HasAttenuator(run)
    hasFilter = HasFilter(run)
    try:
        return goals[(energy, hasAtten, hasFilter)]
    except KeyError:
        print(
            f"Energy {energy}, hasAttenuation {hasAtten}, and hasFilter {hasFilter} not found in goals")
        return None


def GetMIPFitRange(run):
    a = (100, 1100, 200, 1050)
    b = (500, 2000, 650, 1700)
    if run != 655:
        return a
    # run 655 does not have any attenuator or filter
    return b


runinfo = {
    # run: (energy x 8 GeV), with attenuation ? with neutral density filter ? is muon run?)
    # without attenuation, without filter
    369: (1.0, 0, 0, 0),
    370: (0.5, 0, 0, 0),
    371: (1.5, 0, 0, 0),
    372: (2.0, 0, 0, 0),
    373: (30.0 / 8.0, 0, 0, 0),
    374: (0.25, 0, 0, 0),
    375: (1.0, 0, 0, 0),
    376: (1.0, 0, 0, 0),
    377: (1.0, 0, 0, 0),
    378: (1.0, 0, 0, 0),
    379: (1.0, 0, 0, 0),
    # added attenuation
    493: (0.5, 1, 0, 0),
    494: (0.5, 1, 0, 0),
    495: (1.0, 1, 0, 0),
    496: (1.0, 1, 0, 0),
    500: (1.0, 1, 0, 0),
    501: (1.0, 1, 0, 0),
    502: (1.0, 1, 0, 0),
    503: (1.0, 1, 0, 0),
    504: (1.0, 1, 0, 0),
    505: (1.0, 1, 0, 0),
    506: (1.0, 1, 0, 0),
    507: (1.0, 1, 0, 0),
    # run 508: 8 GeV, with attenuation, without filter, muon run
    508: (1.0, 1, 0, 1),
    509: (1.0, 1, 0, 0),
    513: (1.0, 1, 0, 0),
    510: (1.0, 1, 0, 0),
    511: (1.0, 1, 0, 0),
    512: (1.0, 1, 0, 0),
    513: (1.0, 1, 0, 0),
    514: (0.375, 1, 0, 0),
    515: (0.375, 1, 0, 0),
    516: (3.75, 1, 0, 0),
    517: (3.75, 1, 0, 0),
    # muon mode. 8 GeV, with attenuation, without filter, muon run
    521: (3.75, 1, 0, 1),
    522: (3.75, 1, 0, 1),
    523: (3.75, 1, 0, 1),
    525: (3.75, 1, 0, 1),
    526: (3.75, 1, 0, 1),
    527: (1.0, 1, 0, 0),
    # 528 is cosmic run outside of the beam
    529: (0.25, 1, 0, 0),
    530: (0.25, 1, 0, 0),
    531: (0.25, 1, 0, 0),
    532: (1.5, 1, 0, 0),
    533: (1.5, 1, 0, 0),
    534: (2.5, 1, 0, 0),
    535: (2.5, 1, 0, 0),
    537: (2.5, 1, 0, 0),
    538: (2.5, 1, 0, 0),
    540: (30.0/8.0, 1, 0, 0),
    541: (30.0/8.0, 1, 0, 0),
    542: (30.0/8.0, 1, 0, 0),
    543: (30.0/8.0, 1, 0, 0),
    544: (30.0/8.0, 1, 0, 0),
    # take out attenuation, add filter
    # 561 and 562 are cosmic runs outside of the beam
    563: (0.25, 0, 1, 0),
    564: (0.25, 0, 1, 0),
    565: (0.25, 0, 1, 0),
    566: (0.25, 0, 1, 0),
    567: (0.25, 0, 1, 0),
    568: (0.5, 0, 1, 0),
    569: (0.5, 0, 1, 0),
    570: (0.5, 0, 1, 0),
    571: (0.5, 0, 1, 0),
    572: (0.5, 0, 1, 0),
    573: (0.5, 0, 1, 0),
    574: (0.5, 0, 1, 0),
    575: (0.5, 0, 1, 0),
    576: (0.5, 0, 1, 0),
    577: (0.5, 0, 1, 0),
    578: (0.5, 0, 1, 0),
    579: (0.5, 0, 1, 0),
    581: (0.5, 0, 1, 0),
    582: (0.5, 0, 1, 0),
    583: (0.5, 0, 1, 0),
    584: (0.5, 0, 1, 0),
    585: (1.0, 0, 1, 0),
    586: (1.0, 0, 1, 0),
    587: (1.0, 0, 1, 0),
    588: (1.0, 0, 1, 0),
    589: (1.0, 0, 1, 0),
    590: (2.0, 0, 1, 0),
    591: (2.0, 0, 1, 0),
    592: (2.0, 0, 1, 0),
    593: (2.0, 0, 1, 0),
    594: (2.0, 0, 1, 0),
    595: (2.5, 0, 1, 0),
    596: (2.5, 0, 1, 0),
    597: (2.5, 0, 1, 0),
    598: (2.5, 0, 1, 0),
    599: (2.5, 0, 1, 0),
    600: (2.5, 0, 1, 0),
    601: (2.5, 0, 1, 0),
    602: (2.5, 0, 1, 0),
    604: (3.75, 0, 1, 0),
    605: (3.75, 0, 1, 0),
    607: (3.75, 0, 1, 0),
    609: (3.75, 0, 1, 0),
    610: (3.75, 0, 1, 0),
    611: (3.75, 0, 1, 0),
    612: (3.75, 0, 1, 0),
    # start muon mode
    614: (3.75, 0, 1, 1),
    615: (3.75, 0, 1, 1),
    616: (3.75, 0, 1, 1),
    617: (3.75, 0, 1, 1),
    618: (3.75, 0, 1, 1),
    # 619, 620, 621 are proton runs
    619: (15.0, 0, 1, 0),
    620: (15.0, 0, 1, 0),
    621: (15.0, 0, 1, 0),
    # took out filter, no attenuation
    # 639 is cosmic run outside of the beam
    642: (1.0, 0, 0, 0),
    643: (1.0, 0, 0, 0),
    644: (1.0, 0, 0, 0),
    645: (1.0, 0, 0, 0),
    646: (1.0, 0, 0, 0),
    647: (1.0, 0, 0, 0),
    648: (1.0, 0, 0, 0),
    649: (2.0, 0, 0, 0),
    650: (2.0, 0, 0, 0),
    651: (2.0, 0, 0, 0),
    652: (2.0, 0, 0, 0),
    653: (2.0, 0, 0, 0),
    654: (2.0, 0, 0, 0),
    # 655 is in muon mode
    655: (2.0, 0, 0, 1),
    # from 656: i think we have the attenuation in the data
    # need to confirm in the log
    656: (0.5, 1, 0, 0),
    657: (0.5, 1, 0, 0),
    658: (0.5, 1, 0, 0),
    659: (0.5, 1, 0, 0),
    660: (0.5, 1, 0, 0),
    661: (1.0, 1, 0, 0),
    662: (1.0, 1, 0, 0),
    663: (1.0, 1, 0, 0),
    664: (1.0, 1, 0, 0),
    665: (1.0, 1, 0, 0),
    666: (1.5, 1, 0, 0),
    667: (1.5, 1, 0, 0),
    668: (1.5, 1, 0, 0),
    669: (1.5, 1, 0, 0),
    670: (1.5, 1, 0, 0),
    671: (2.0, 1, 0, 0),
    672: (2.0, 1, 0, 0),
    673: (2.0, 1, 0, 0),
    674: (2.0, 1, 0, 0),
    675: (2.0, 1, 0, 0),
    # 676 is in muon mode
    676: (3.75, 1, 0, 1),
    677: (3.75, 1, 0, 0),
    678: (3.75, 1, 0, 0),
    679: (3.75, 1, 0, 0),
    680: (3.75, 1, 0, 0),
    682: (3.75, 1, 0, 0),
    683: (3.75, 1, 0, 0),
    684: (3.75, 1, 0, 0),
    685: (2.5, 1, 0, 0),
    686: (2.5, 1, 0, 0),
    687: (2.5, 1, 0, 0),
    688: (2.5, 1, 0, 0),
    689: (2.5, 1, 0, 0),
    690: (2.5, 1, 0, 0),
    691: (2.5, 1, 0, 0),
    692: (2.5, 1, 0, 0),
    693: (2.5, 1, 0, 0),
    694: (2.5, 1, 0, 0),
    695: (2.5, 1, 0, 0),
    # run after 696 are for some tests of janus daq system as far as i can tell
}

for run in range(375, 492):
    runinfo[run] = (1.0, 0, 0, 0)


def GetRunInfo(run):
    run = int(run)
    if run not in runinfo:
        print(f"Run {run} not found in runinfo")
        return None
    return runinfo[run]


def CheckRunExists(run):
    try:
        run = int(run)
        info = GetRunInfo(run)
        if info is None:
            return False
        return True
    except ValueError:
        print(f"Run {run} is not a number")
        return False


def GetEnergy(run):
    info = GetRunInfo(run)
    if info is None:
        return None
    return info[0] * 8.0


def HasAttenuator(run):
    info = GetRunInfo(run)
    if info is None:
        return None
    return info[1]


def HasFilter(run):
    info = GetRunInfo(run)
    if info is None:
        return None
    return info[2]


def IsMuonRun(run):
    info = GetRunInfo(run)
    if info is None:
        return None
    return info[3]


def GetTitle(run, run_end=None):
    if not CheckRunExists(run):
        return None
    energy = GetEnergy(run)
    hasAtten = HasAttenuator(run)
    hasFilter = HasFilter(run)
    isMuon = IsMuonRun(run)

    title = f"Run {run}"
    if run_end is not None:
        title += f" to {run_end}"
    title += f", {energy} GeV"
    if hasAtten:
        title += ", with attenuator"
    if hasFilter:
        title += ", with filter"
    if isMuon:
        title += ", muon run"
    return title
