import gw_helper

''' usage: python update_json.py '''

''' modify these variables to customise your update_json run: ''' 

# list of json files to update
jsons='input_json_files.txt'

# output details
dir_out='out'
dir_log='log'
prefix=None
overwrite=False
verbose=False

# global params to update
propid='2020A-0402'
tilings=2

# tiling-specific params to update
# all lists must have same length as the tilings variable above
# use None if you want to keep original input values
band=[None,'r']
exptime=[None,90.0] # seconds
ra_shift=[0.0,0.5] # deg
dec_shift=None # equiv to [0.0,0.0] or [None,None]

''' end of settings '''





# read list of jsons
json_files=list(open(jsons).read().splitlines()) 

# apply changes
gw_helper.setup_tilings(
    json_files,
    tilings,
    ra_shift,
    dec_shift,
    exptime,
    band,
    propid,
    dir_out,
    dir_log,
    prefix,
    overwrite,
    verbose)



#exit
