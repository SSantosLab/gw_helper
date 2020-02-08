import os
import socket
import logging
import datetime
import argparse
import numpy as np
import json

def start_logger(dir_log=None,debug=True):
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
    if debug: logger.setLevel(logging.DEBUG)
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
    return logger

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
    if 'json_for_gw' in logging.Logger.manager.loggerDict:
        logger = logging.getLogger('json_for_gw')
    else:
        logger = start_logger()
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

def write_json(j_out,j_file=None,dir_out=None,prefix=None,overwrite=True):
    if 'json_for_gw' in logging.Logger.manager.loggerDict:
        logger = logging.getLogger('json_for_gw')
    else:
        logger = start_logger()
    if dir_out is None: dir_out = os.path.join(os.getcwd(),'json/')
    if not os.path.isdir(dir_out):
        try:
            os.makedirs(dir_out)
        except:
            print('Error creating directory: {0}'.format(dir_out))
            return
    if j_file is None: j_file = os.path.join(dir_out,'out.json')
    head, tail = os.path.split(j_file)
    if prefix is not None: tail = '{0}_{1}'.format(prefix, tail)
    fname = os.path.join(dir_out,tail)
    if os.path.exists(fname):
        logger.warning('File {0} already exists'.format(fname)) 
        if overwrite: 
            logger.warning('Overwriting file')
        else:
            logger.error('Return w/o writing to file')
            return 
    json.dump(j_out, open(fname, 'w+'), indent=4,sort_keys=True)
    logger.info('File {0} was (over)written'.format(fname))
    return

def modify_exp(j_in,key=None,value=None,shift=None):
    if key is None: return j_in
    j_out = []
    for exp in j_in:
        e = exp.copy()
        if value is not None: e[key] = value
        if shift is not None: e[key] += shift
        j_out.append(e)
    return j_out

def setup_tilings(json_files,
                  tilings=1,
                  ra_shift=[0.0],
                  dec_shift=[0.0],
                  etime=[None],
                  band=[None],
                  propid=None, 
                  dir_out=None,
                  dir_log=None,
                  prefix='out',
                  overwrite=False,
                  debug=False):

    if 'json_for_gw' in logging.Logger.manager.loggerDict:
        logger = logging.getLogger('json_for_gw')
        if debug: 
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.NOTSET)
    else:
        logger = start_logger(dir_log,debug)

    logger = logging.getLogger('json_for_gw')

    for f in json_files:
        logger.info('Working on file {0}'.format(f))
        data_in=open_json(f)
        if data_in is None: continue
        if propid is not None:
            data_in=modify_exp(data_in,key='propid',value=propid)
        data_out=[]
        for t in range(tilings):
            data_t=list(data_in)
            data_t=modify_exp(data_t,key='RA',shift=ra_shift[t])
            data_t=modify_exp(data_t,key='dec',shift=dec_shift[t])
            if etime[t] is not None:
                data_t=modify_exp(data_t,key='exptime',value=etime[t])
            if band[t] is not None:
                data_t=modify_exp(data_t,key='filter',value=band[t])
            data_out+=data_t
            logger.info('Completed tiling {0} of {1}'.format(t,tilings))
        write_json(data_out,f,dir_out,prefix,overwrite)
    return 

