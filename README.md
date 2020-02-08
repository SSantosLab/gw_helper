# Repo: gw_helper
## Some auxiliary codes for DES-GW

### 1) `json_modify.py`: code to modify JSON files and apply dithering

#### What the code does?
1) The code runs well in Python2.7 (works in Python 3 too), and doesn’t need any additional library, just numpy. So, if you put in on a directory, it works without needing additional files.
1) The code will set the Proposal ID from "--pid" or "--pname" to all JSON files.
1) The code will only drop entries with bands listed in the “--drop” argument.
1) The code will only change the bands matching the criteria in “--change” argument.
1) The code will generate 2 additional entries for each RA-DEC position, one shifted only in RA, the other only in DEC (dithering).
1) The code changes g-band to r-band by default, drops z-band, and set a dithering of **0.02 deg** to cover the CCD gaps. All these values can be changed when calling the script.
1) To change the exposure time (one value for all the entries) use the calling argument.
1) The code works either on a single file or in a list of files.
1) The code writes out “RA” in lowercase. Let me know if you want it uppercase.

------------------------------------------------
#### How to call the code?
*Note: You will need to provide the Proposal ID (or proposal entry) always.*

Typical call for a single file modification is:

`python json_modify.py --file some.json --pname BNS --change g r --drop z VR N964 --exp 120 --shift 0.02 0.02 --pre myPrefix`

For a set of files is:

`python json_modify.py --tab list_json.txt --pname BBH --change g r --drop z VR N964 --exp 120 --shift 0.02 0.02 --pre myPrefix`

Or simply using the default values:

`python json_modify.py --file some.json --pid 2017A-0069 --exp 120`

`python json_modify.py --tab list_json.txt --pid 2017A-0069 --exp 120`

------------------------------------------------
#### Arguments for calling the code
(this information is also available typing `python json_modify.py --help`):
  * `--file` or `--tab`: to input either a single filename or a file containing the paths to all the JSON files. Remember you can create a list of files simply doing `ls *json > my_list.txt` on the commad line.
  * `--pname` or `--pid`: to input the Proposal ID to be used in all JSON files. There are 2 coded in the script, via a Python dictionary, via the `--pname` option: 2019A-0205 (accessed using **pname** BNS) and 2019A-0235 (accessed using **pname** BBH). If you want to use another Proposal ID, then use the option `--pid` followed by the code. Example: `--pid 2017A-0069`
  * `--change`: to input 2 variables, the first is the band to be replaced, the second is the band used as replacement. Example: if we use `--change u Y` then the code will locate all u-band and replace them by Y-band. *Default is to change from g-band to r-band*
  * `--drop`: single variable or list of variables. Each of these will be used to drop the entries in the JSON file. Example: using `--drop H J K` will cause the code to remove all entries having either H-band, J-band, or K-band. *Default is to drop only z-band*
  * `--exp`: single value to be used to replace the exposure time for **all** the entries. If this argument is not used, then the exposure time will be not modified. Example: `--exp 15` will set 15 as the exposure time for **all** the entries. *Default is to not change the exposure time*
  * `--shift`: two values to be used as the shift in RA and DEC for the dithering. These values will be added to the RA and DEC values for each entry, resulting in 3 entries: (1) original entry, (2) entry shifted in RA only, (3) entry shifted in DEC only. Example: if we set `--shift 0.015 0.03` the code will create a shifted entry for `RA + 0.015` and other entry shifted in `DEC + 0.03`. *Default is to use 0.02 deg for RA and for DEC*
  * `--pre`: variable to be prepend to the resulting filename(s). Example: if `--pre neutr` then the output file for `obs01.json` will be `neutr_obs01.json`

------------------------------------------------
#### Note about format
Note the Python-JSON standard fails (the core library) when the float numbers has only the “dot” but not “decimals”.
Example:
* “RA”: 32.    Will make Python-json fail
* “RA”: 32.0    Will work perfect!
------------------------------------------------


#### Alex D-W wget command to get images
```bash
STARTDATE=`date --date="12 hours ago"  +%Y%m%d`
URL=http://decade.ncsa.illinois.edu/deca_archive/RAW
wget -X . -r -A DECam_\*fits.fz  -np --level=2 --no-check-certificate -N -nH --cut-dirs=2 --progress=dot -e dotbytes=4M $URL/${STARTDATE}/
```

### 2) `setup_tilings()`: a useful helper function 

Use setup_tilings() to modify a json file for observing with DECam. The entire list of exposures is considered as one "tiling". Multiple tilings (copies of the entire list) can be created by setting the number of tilings to > 1. Exposure details (band, exposure time, and ra/dec offsets) must be specified for each tiling via parameter lists. If a parameter is set to None for a given tiling, the original tiling value will be copied over. The propid can also be specified; it will be applied to all tilings.


Example usage:
```
import gw_helper

gw_helper.setup_tilings(
    json_files=['json/sample.json'],
    tilings=2,
    ra_shift=[0.0,0.5],
    dec_shift=[0.0,0.0],
    etime=[None,200],
    band=[None,'z'],
    propid='2020A-0402',
    dir_out=None,
    dir_log=None, 
    prefix='out2',
    overwrite=True,
    debug=True)
```
