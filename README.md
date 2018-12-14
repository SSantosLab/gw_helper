# Repo: gw_helper
## Some auxiliary codes for DES-GW

### 1) `json_modify.py`
Typical call for a single file modification is:

`python json_modify.py --file some.json --change g r --drop z VR N964 --exp 120 --shift 0.02 0.02 --pre myPrefix`

For a set of files is:

`python json_modify.py --tab list_json.txt --change g r --drop z VR N964 --exp 120 --shift 0.02 0.02 --pre myPrefix`

Or simply using the default values:

`python json_modify.py --file some.json --exp 120`
`python json_modify.py --tab list_json.txt --exp 120`

About the parameters (this information is also available typing `python json_modify.py --help`):
  * `--file` or `--tab`: to input either a single filename or a file containing the paths to all the JSON files
  * `--change`: to input 2 variables, the first is the band to be replaced, the second is the band used as replacement. Example: if we use `--change u Y` then the code will locate all u-band and replace them by Y-band. *Default is to change from g-band to r-band*
  * `--drop`: single variable or list of variables. Each of these will be used to drop the entries in the JSON file. Example: using `--drop H J K` will cause the code to remove all entries having either H-band, J-band, or K-band. *Default is to drop only z-band*
  * `--exp`: single value to be used to replace the exposure time for **all** the entries. If this argument is not used, then the exposure time will be not modified. Example: `--exp 15` will set 15 as the exposure time for **all** the entries. *Default is to not change the exposure time*
  * `--shift`: two values to be used as the shift in RA and DEC for the dithering. These values will be added to the RA and DEC values for each entry, resulting in 3 entries: (1) original entry, (2) entry shifted in RA only, (3) entry shifted in DEC only. Example: if we set `--shift 0.015 0.03` the code will create a shifted entry for `RA + 0.015` and other entry shifted in `DEC + 0.03`. *Default is to use 0.02 deg for RA and for DEC*
  * `--pre`: variable to be prepend to the resulting filename(s). Example: if `--pre neutr` then the output file for `obs01.json` will be `neutr_obs01.json`

--------------------------------------------------------------------
