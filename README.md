# names-dataprep.py
Preps Excel data for use in Names Registry project.
Takes names project excel files, performs data prep operations
(removes extraneous cols/rows, normalizes col names, etc.), then saves data 
in CSV format and schema info about the input files as a text file. 

If `--consolidate` mode is selected, the script will iterate through all input 
excels and attempt to save all data into a single csv file with a simplified 
format.

## Requirements

Compatible with Python 3 only. Requires `pandas`.

## Usage

`names-dataprep.py [-h] [-A] [-C] inpath [outpath]`

**Positional Arguments:**
```
  inpath              Path to directory containing excel files for conversion.
  outpath             Path to write filtered files.
```

**Optional Arguments:**
```
  -h, --help          show this help message and exit
  -A, --analyze-only  Do not convert files, just output stats file.
  -C, --consolidate   Consolidate filtered CSVs into single file in simple
                      form (name, family id, birthdate only).
```

**Examples**:
```
     $ python names-dataprep.py ./data ./output
     $ python names-dataprep.py --analyze-only ./data
     $ python names-dataprep.py --consolidate ./data_in ./data_out
```

### Notes and Tips

1. The filtering operations will attempt to trim leading and trailing space, lower-case, 
remove ')' and '(' chars, and replace spaces with '_' from columns. It also drops rows 
that do not contain any data. 

2. Use the `--analyze-only` mode to produce a text file with stats; 
but skip the more time-consuming filtering operations if you do not 
need the data converted.

3. In `--consolidate` mode, if the excel does not contain the 
required columns (or their labels are malformed) the script will 
emit an error in stdout and will skip the file when consolidating. 
However, all of the other excel data will continue to be processed 
for the consolidated file.

The required columns for consolidated file are: 

```
    'original_order',
    'far_line_id',
    'last_name_corrected',
    'first_name_corrected', 
    'other_names',
    'date_of_birth',
    'family_number'

```
