""" Script to modify the JSON file performing following steps:
1) change g-band to r-band
2) drop z-band entirely
3) change exposures times
4) add series of dither to cover CCD gaps
5) check the new generated JSON passes the checking of Eric Neilsen scripts
/data/des60.b/data/neilsen/gwwide
"""

import os
import socket
import logging
import datetime
import argparse
import numpy as np
import json

#
# Start the logs
#
dir_log = None
# Check/assign LOG directory
if (dir_log is None):
    dir_log = os.path.join(os.getcwd(), "log/")
# Check if the path exists. If doesn't, create it
if (not os.path.isdir(dir_log)):
    try:
        os.makedirs(dir_log)
    except:
        print('Error creating directory: {0}'.format(dir_log))
# Setup write out
hhmmss = datetime.datetime.today().strftime("%Hh%Mm%Ss")
lognm = "json_mod_{0}.log".format(hhmmss)
logpath = os.path.join(dir_log, lognm)
# Setup logger to file and stdout
logger = logging.getLogger('json_for_gw')
logger.setLevel(logging.DEBUG)
# File recording from DEBUG and uppper levels
fh = logging.FileHandler(logpath)
fh.setLevel(logging.DEBUG)
# STDOUT handler recording INFO and upper levels
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)
# logging.basicConfig(filename=logpath, 
#                     level=logging.DEBUG,
#                     format="%(asctime)s - %(levelname)s - %(message)s")
logger.info('LOG: {0}'.format(logpath))

def open_json(fnm):
    """Open JSON file. If file cannot be accessed the returned value is None
    and should be checked by the code using this function
    Parameters 
    ----------
    fnm : str
        Filename or full path 
    Returns
    -------
    data : list of dict | None
        Returned list contains one entry for each observation recorded in the
        JSON. Returns None if file doesn't exists or cannot be accessed
    """
    # Check if file exists
    if (not os.path.exists(fnm)):
        logger.error('File {0} not exists or cannot be access'.format(fnm))
        logger.info('Skipping {0}'.format(fnm))
        data = None
    else:
        try:
            with open(fnm) as f:
                data = json.load(f)
        except:
            logger.error('Something wrong in the JSON format, even a comma')
            logger.info('Skipping {0}'.format(fnm))
            data = None
    return data


def modify_json(j_in, 
                etime=None, 
                ra_shift=0.02, dec_shift=0.02,
                b_ini='g', b_end='r', b_drop=['z'], 
                equiv={'band': 'filter', 'exposureTime': 'exptime', 
                       'RA': 'ra', 'DEC': 'dec',},):
    """
    Note all comparison are made as lowercase, to avoid errors due to a capital
    letter being in the string
    Parameters
    ----------
    j_in : list of dict
        List of dictionaries containig the entries from a JSON file 
    etime : float
        Exposure time to replace all the exposure times in the different 
        entries. If None, then the exposure time will not be changed
    ra_shift : float
        Shift in degress for RA, to cover the gaps in a dithering. This value
        is capable to cover up to a misalignement of 48 deg between DECam and
        the RA-DEC grid
    dec_shift : float
        Shift in degress for DEC, to cover the gaps in a dithering. This value
        is capable to cover up to a misalignement of 48 deg between DECam and
        the RA-DEC grid
    b_ini : str
        Initial band to be replaced by the value in b_end 
    b_end : str
        Band to replace the initial band defined in b_ini
    b_drop : list
        The entries having these bands will be removed
    equiv : dict
        Dictionary to relate names we use for some keywords, against the
        values present in the JSON files. Example: we will call 'band' what
        the JSON file calls 'filter'
    Returns
    -------
    j_out : list of dict
        List of dictionaries containing the modified dictionary, and the 2
        dithered obtained translating it in RA and DEC
    """
    # Making sure all values of the equiv dictionary are lowercase
    equiv = dict((k, v.lower()) for k, v in equiv.iteritems())
    logger.info('Dictionary of name-keyword equivalences: {0}'.format(equiv))
    # Each element of the JSON object is a dictionary 
    j_out = []
    for entry_n in j_in:
        # Create a copy of the n-th dictionary to work on it
        tmp_d = entry_n.copy()
        # First of all is to change to lowercase the keywords of interest. 
        # This will avoid us simple errors. We create a second copy to avoid
        # erros when modifyng the dictionary on the iteration
        aux_dict = entry_n.copy()
        for k, v in tmp_d.iteritems():
            if k.lower() in map(str.lower, equiv.values()):
                aux_dict[k.lower()] = aux_dict.pop(k)
                # tmp_d[k.lower()] = tmp_d.pop(k)
        del tmp_d
        tmp_d = aux_dict
        # 1) Change g-band to r-band
        # If later we want to change this, something more elegant need to 
        # be put in place
        band = tmp_d[equiv['band']].strip().lower()
        if (band == b_ini.lower()):
            tmp_d[equiv['band']] = b_end
        # 2) Drop z-band
        if (band in b_drop):
            # skip the rest and go to the next, not saving this entry
            continue
        # 3) Change exptime to a new value
        if (etime is not None):
            tmp_d[equiv['exposureTime']] = etime
        # 4) Dithering, in deg units
        # A dithering of 0.02 deg in each direction is small enough to just 
        # cover the CCD gaps and also to take into account the non-perfect 
        # alignment between DECam and the RA-DEC grid
        ra0 = tmp_d[equiv['RA']]
        dec0 = tmp_d[equiv['DEC']]
        # Translation in RA only
        dict_dRA = tmp_d.copy()
        dict_dRA[equiv['RA']] = ra0 + ra_shift
        # Translation in DEC only
        dict_dDEC = tmp_d.copy()
        dict_dDEC[equiv['DEC']] = dec0 + dec_shift
        # Add the modified dictionary and the 2 dithered to the output list
        j_out.append(tmp_d)
        j_out.append(dict_dRA)
        j_out.append(dict_dDEC)
    return j_out
    

def aux_main():
    """Auxiliary main function 
    """
    # Setup argparse for user input
    h0 = "Script to modify JSON files by: (1) changing g to r-band,"
    h0 += " (2) drop z-band entirely, (3) change exptime, (4) add dithering"
    h0 += " to cover CCD gaps. After this you should check it passes quality"
    h0 += " checks for your telescope control system. \nNOTE: the keywords to"
    h0 += " be modified/searched will be converted to lowercase."
    epi = "Remember to use E. Neilsen's code to check JSON files compatibility"
    arg = argparse.ArgumentParser(description=h0, epilog=epi)
    #
    arg_file = arg.add_mutually_exclusive_group(required=True)
    h1 = 'Filename (or full path) of the JSON file to be modified'
    arg_file.add_argument('--file', help=h1)
    h2 = 'Filename (or full path) of a 1-column text file containing the'
    h2 += ' list of filenames of the JSON files to be modified'
    arg_file.add_argument('--tab', help=h2)
    #
    band_change = ['g', 'r']
    h3 = 'Pair of bands from which change the entries. Input the 2 separated'
    h3 += ' by a space. Format: band-in band-out. Default:'
    h3 += ' {0}'.format(' '.join(band_change))
    arg.add_argument('--change', help=h3, nargs=2, default=band_change)
    #
    band_drop = ['z']
    h4 = 'Band to be dropped from the JSON. If more than one is given,'
    h4 += ' input separated by a space.'
    h4 += ' Default: {0}'.format(' '.join(band_drop))
    arg.add_argument('--drop', help=h4, nargs='+', default=band_drop)
    #
    h5 = 'New exposure time to be set to all entries in the JSON.'
    h5 += ' If no value is input, exposure time will not be changed'
    arg.add_argument('--exp', help=h5, type=float)
    #
    dither = [0.02, 0.02]
    h6 = 'Shift in degrees, for RA and DEC, to be applied to the selected'
    h6 += ' JSON entries. Space-separated. Format: shift-RA shift-DEC.'
    h6 += ' Default: {0}'.format(' '.join(map(str, dither)))
    arg.add_argument('--shift', help=h6, nargs=2, type=float, default=dither)
    #
    pref = 'mod'
    h7 = 'Prefix to be prepend to the original JSON filename, to generate the'
    h7 += ' output filenames. Output directory is the same as the input file.'
    h7 += ' Default: {0}'.format(pref)
    arg.add_argument('--pre', help=h7, default=pref)
    #
    arg = arg.parse_args()
    #
    # First information
    logger.info("Running on: {0}".format(socket.gethostname()))
    logger.info("Script: {0}".format(os.path.basename(__file__)))
    #
    # Even if there is only one file, treat as a list
    if (arg.tab is None):
        path_list = [arg.file]
    else:
        # Read list
        arr = np.loadtxt(arg.tab, dtype=str)
        path_list = list(arr)
    # If exptime is None then it will not be changed
    if (arg.exp is None):
        logger.warning('EXPTIME will not be changed as no value was input')
    exptime = arg.exp
    # One JSON at a time
    for p in path_list:
        # Open JSON
        tmp_in = open_json(p)
        if (tmp_in is None):
            continue
        logger.info('Working on {0}'.format(p))
        # Modify the JSON
        tmp_out = modify_json(
            tmp_in, 
            etime=arg.exp, 
            ra_shift=arg.shift[0], 
            dec_shift=arg.shift[1], 
            b_ini=arg.change[0], 
            b_end=arg.change[1], 
            b_drop=arg.drop, 
        )
        if (len(tmp_out) == 0):
            logger.warning('No entries were selected from {0}'.format(p))
            continue
        # Writting out the modified JSON
        head, tail = os.path.split(p)
        tail = '{0}_{1}'.format(arg.pre, tail) 
        fname = os.path.join(head, tail)
        json.dump(tmp_out, open(fname, 'w+'), indent=4)
        #
        logger.info('File {0} was written'.format(fname))
        logger.info('{0} entries were selected'.format(len(tmp_out) / 3))
    return True


if __name__ == '__main__':
    aux_main()
