# fit 16D data to 1D data with ROOT

import ROOT
import os
import numpy as np
from scipy.stats import norm
from modules.fitFunction import fitFunction
from modules.utils import getChannelMap, parseRuns
from modules.CNNModel import buildCNNModel
from modules.runinfo import GetRegressionGoal
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau


ROOT.gROOT.SetBatch(True)


def RunCNNRegression(run_start, run_end):
    t = ROOT.TChain("save")
    for run in range(run_start, run_end):
        fname = f"root_selected/Run{run}_list_selected.root"
        if not os.path.exists(fname):
            print(f"File {fname} does not exist")
            continue
        t.Add(fname)

    nentries = t.GetEntries()
    print(f"Number of entries: {nentries}")

    chans = np.zeros((nentries, 4, 4, 1), dtype=np.float32)

    for i in range(nentries):
        t.GetEntry(i)
        for j in range(16):
            x, y = getChannelMap(j)
            chans[i][x][y][0] = t.ch_lg[j]

    def trainCNNModel(chans, energys):
        model = buildCNNModel()
        model.summary()
        # Compile the model with a custom learning rate
        initial_learning_rate = 0.005  # Initial learning rate
        optimizer = tf.keras.optimizers.Adam(
            learning_rate=initial_learning_rate)
        model.compile(optimizer=optimizer, loss='mean_absolute_error')

        checkpoint = ModelCheckpoint(
            f'results/best_model_Run{run_start}_Run{run_end}.keras', monitor='loss', save_best_only=True, mode='min')
        early_stopping = EarlyStopping(
            monitor='loss', patience=5, mode='min', verbose=1)
        lr_scheduler = ReduceLROnPlateau(
            monitor='loss', factor=0.5, patience=3, min_lr=1e-6, verbose=1)
        model.fit(chans, energys, epochs=20, batch_size=32,
                  callbacks=[checkpoint, early_stopping, lr_scheduler])
        return model

    # target = 3100.0 * 0.3
    target = GetRegressionGoal(run_start)
    print(f"Regression goal: {target}")
    energys = np.random.normal(target, target * 0.01, nentries)
    result = trainCNNModel(chans, energys)

    # predictions = fitFunction(chans, result.x)
    predictions = result.predict(chans)
    print("predictions after trainng: ", predictions)
    mu, std = norm.fit(predictions)
    print(f"mu = {mu}, std = {std}, relative std = {std/mu}")
    predictions = predictions.astype(np.float64)

    # sum
    chans = chans.reshape(nentries, 16)
    predictions_unc = fitFunction(chans, np.ones(17))
    mu_unc, std_unc = norm.fit(predictions_unc)
    print(
        f"mu_unc = {mu_unc}, std_unc = {std_unc}, relative std = {std_unc/mu_unc}")

    # run the predictions
    ofile = ROOT.TFile(
        f"root_selected/Run_list_selected_CNNcalibrated_Run{run_start}_{run_end}.root", "RECREATE")
    hcal = ROOT.TH1F("hcal", "Calibrated Energy",
                     200, target-1000, target+1000)
    hcal.FillN(nentries, predictions, np.ones(nentries))
    hcal.Write()
    hcal_unc = ROOT.TH1F("hcal_unc", "Uncalibrated Energy",
                         200, target-1000, target+1000)
    hcal_unc.FillN(nentries, predictions_unc, np.ones(nentries))
    hcal_unc.Write()
    ofile.Close()


if __name__ == "__main__":
    run_start, run_end = parseRuns()
    RunCNNRegression(run_start, run_end)
