'''
Jessica Heeman
11 Octobre 2022

based on:
https://stackoverflow.com/questions/51809979/analysis-of-eye-tracking-data-in-python-eye-link
information on Eye Link 1000 line formats:
http://sr-research.jp/support/EyeLink%201000%20User%20Manual%201.5.0.pdf
'''
# clear memory
from IPython import get_ipython
get_ipython().run_line_magic('reset', '-sf')

# relevant packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import csv

#%%
def ASC2pandasframe(file_name):
# location of data files
os.chdir('C:/Users/HP/Documents/Psychologie UU jaar 4/Data')

'''
read the file and store, depending on the messages in the data

This function takes a directory from which it tries to read in ASCII files containing eyetracking data
It returns
eye_data: A pandas dataframe containing all samples
event_data: A pandas datafram containing all events
'''
# dataframes
eye_data   = []     # maak het dataframe van de samples
event_data = []
all_data   = []

# headers
eye_header   = {0: 'tijd',1: 'pup'}
event_header = {0: 'tijd', 1: 'event'}
all_header = {0: 'tijd', 1: 'event'}

start_reading = False
in_blink      = False

# timestamps
blink_timestamps = []

# additional info
sample_rate_info = []
sample_rate = 0

# The first character in each line identifies what the line is:
#       <no token>    --> Blank line     --skip
#       # or ; or /   --> Comment line   --skip
#       *             --> Preamble line  --skip
#       Digit (0..9)  --> Data sample line
#       Letter (A..Z) --> Event or Specification line

# structure of the .asc data files:
# 1) Preamble, lines starting with '*'
# 2) Messages starting with 'MSG' containing information about callibration/
#    validation/corrections etc.
# 3) General information about the recording (see manual for more information)
#    START <timestamp>    LEFT    SAMPLES EVENTS
#    PRESCALER
#    VPRESCALER
#    PUPIL AREA
#    EVENTS	GAZE	LEFT	RATE	1000.00	TRACKING	CR	FILTER	2	INPUT
#    SAMPLES	GAZE	LEFT	RATE	1000.00	TRACKING	CR	FILTER	2	INPUT
# 4) the actual data:
#       Eye link standard lines (see manual)
#       Data samples: <time> <xp> <yp> <ps> <xv> <yv>
#       SFIX <eye> <time>
#       EFIX <eye> <stime> <etime> <dur> <axp> <ayp> <aps>
#       SSACC <eye> <time>
#       ESACC <eye> <stime> <etime> <dur> <sxp> <syp> <exp> <eyp> <ampl> <pv>
#       SBLINK <eye> <time>
#       EBLINK <eye> <stime> <etime> <dur>
#       MSG <time> TRIALSTART
#       MSG <time> TRIALEND
#       MSG <time> DISPLAY ON
#   Custom messages labeled with TAG:
#       MSG <time> TAG: practicenr: ../10
#       MSG <time> TAG: trialnr: ../33
#       MSG <time> TAG: condtion csPlus csmin
#       MSG <time> TAG: stimDur ..., fixDur ..., shockDel ...
#       MSG <time> TAG: fix onset
#       MSG <time> TAG: stim onset
#       MSG <time> TAG: shock onset
#       MSG <time> TAG: exp end
#       MSG <time> TAG: prac end

with open(file_name) as f:
csv_reader = csv.reader(f, delimiter ='\t')
for i, row in enumerate(csv_reader):
if any('PARSESTART' in item for item in row): # only start reading after this message
start_reading = True
elif any('SBLINK' in item for item in row):  # stop reading here because blinks contain NaN
in_blink = True
elif any('EBLINK' in item for item in row):  # start reading again, blink ended
blink_timestamps.append ([row[0].split()[2],row[1]])
in_blink = False
elif start_reading and not in_blink:  # start adding data to the dataframes
if row[0].isdigit():  # if the row is sample data
# add sample to dataframe and convert to numbers
for i, item in enumerate(row):
if item.isdigit():
row[i] = float(item)
eye_data.append([row[0], row[3]])  # do not include '...' at the end op sampledata
all_data.append([row[0], row[3]])
elif row[0].isalpha():  # if the row is an event
if any('TAG:' in item for item in row):
# remove 1st element 'MSG', remove 'TAG:' and keep the event
row = row[1].split('TAG:')
event_data.append([float(row[0]), row[1][1:]]) # convert timestamp in number
all_data.append([float(row[0]), row[1][1:]])
elif any('TRIALSTART' in item for item in row):
row = row[1].split()
event_data.append([float(row[0]), row[1]]) # convert timestamp in number
all_data.append([float(row[0]), row[1]])
elif any('TRIALEND' in item for item in row):
row = row[1].split()
event_data.append([float(row[0]), row[1]]) # convert timestamp in number
all_data.append([float(row[0]), row[1]])

# convert into pandas fix_data Frames for a better overview
eye_data = pd.DataFrame(eye_data)
event_data = pd.DataFrame(event_data)
all_data = pd.DataFrame(all_data)

# add headers
eye_data = eye_data.rename(columns=eye_header)
event_data = event_data.rename(columns=event_header)
all_data = all_data.rename(columns=all_header)

# substract the first timestamp of eye_data to set the start to 0ms
start_tijd = eye_data.tijd[0]
event_data.tijd -= start_tijd
eye_data.tijd -= start_tijd
all_data.tijd -= start_tijd

return eye_data, event_data, all_data

#%%
for i in range(1, 10):
file_name = 'ESS0'+ str(i) + 'Con'
eye_data, event_data, all_data = ASC2pandasframe(file_name + '.asc')
eye_data.to_csv('eye_data_' + file_name +'.csv', index=False)
event_data.to_csv('event_data' + file_name +'.csv', index=False)
all_data.to_csv('all_data' + file_name +'.csv', index=False)

