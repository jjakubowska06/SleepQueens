import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne
import yasa

import sys
import os

import copy



edf_sig = '/content/drive/MyDrive/ HACKATON HEROS/ST7112J0-PSG.edf'
sig = mne.io.read_raw_edf(edf_sig, preload=True, verbose=True)


# yasa
# https://github.com/jjakubowska06/yasa/tree/master/notebooks

# yasa staging
sls = yasa.SleepStaging(sig, eeg_name="EEG Fpz-Cz", metadata=dict(age=21, male=False))

hypno = sls.predict()


# checking cycles
cycles_stamps_smooth = []
threshold = 35

for i,state in enumerate(hypno):
  if len(hypno) == 1:
    continue

  # jesli poprzedni rem, a aktualny nie rem, to koniec cyklu
  if state != 'R' and hypno[i-1] == 'R':
    cycles_stamps_smooth.append(i)

  # smooth out hypno
  elif state == 'R':
    # check if previous state was R
    if hypno[i-1] == 'R':
      # cycles_stamps.append(i)
      continue

    # threshold 15 min?
    elif 'R' in hypno[i-threshold:i-1]:
      cycles_stamps_smooth.pop(-1)



# convert to numbers

hypno_num = hypno.copy()
hypno_num[hypno=='W'] = 5
hypno_num[hypno=='R'] = 4
hypno_num[hypno=='N1'] = 3
hypno_num[hypno=='N2'] = 2
hypno_num[hypno=='N3'] = 1

t = np.arange(0, 1022)/120


step_size=20
rysuj_hypno = np.zeros(len(hypno))
a = 0
custom_labels = {1: 'N3', 2: 'N2', 3: 'N1', 4:'REM', 5:'WAKE'}

for i in range(0, len(hypno_num), step_size):
    fig = plt.figure(figsize=(20,3))
    for stamp in cycles_stamps_smooth:
      if stamp <= i+step_size:
        if stamp == cycles_stamps_smooth[-1]:
          break
        plt.vlines(stamp, 0, 5, color='#f5bebd')

    range_i = []
    rysuj_hypno[:i + step_size] = hypno_num[:i + step_size]
    plt.plot(rysuj_hypno, color = '#5e6697')
    plt.yticks(ticks=list(custom_labels.keys()), labels=list(custom_labels.values()))

    max_sample = 1022
    samples_per_hour = 120
    hour_ticks = np.arange(0, max_sample + 1, samples_per_hour)  # Hour ticks
    hour_labels = [f'{tick // samples_per_hour:.1f}h' for tick in hour_ticks]  # Convert ticks to hours
    plt.xticks(ticks=hour_ticks, labels=hour_labels)

    plt.xlim(0, 1022)
    plt.ylim(0,5.5)
    plt.xticks()

    # plt.show()
    plt.savefig(f'results5/it_{i}.png')
