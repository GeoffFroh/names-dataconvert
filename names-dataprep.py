#! /usr/bin/env python3
#
# names-dataprep.py
# Tries to fix names project excel files
#

description = """Preps excel data for use in names project."""

epilog = """
This command takes names project excel files, performs data prep operations
(removes extraneous cols/rows, normalizes col names, etc.), then saves data 
in csv format and schema info about the input files as a text file. 

EXAMPLES
     $ python names-dataprep.py ./data ./output
     $ python names-dataprep.py --analyze-only ./data
     $ python names-dataprep.py --consolidate ./data_in ./data_out
"""


import argparse
import sys, shutil, os
import datetime
import csv
import pandas

def doAnalyze(df,filename):
    analyze_result = '--------------------------\n'
    analyze_result += 'Filename: {}\n'.format(filename)
    analyze_result += '{} rows. {} columns.\n'.format(df.shape[0],df.shape[1])
    analyze_result += '{}\n'.format(df.columns)
    analyze_result += '--------------------------\n'
    return(analyze_result,df.shape[0])

def doFilters(namesdata):
    #remove empty rows
    namesdata.dropna(axis='index',how='all',inplace=True)

    #normalize column names
    namesdata.rename(columns=(lambda c:c.strip()),inplace=True)
    namesdata.rename(columns=(lambda c:c.replace(')','')),inplace=True)
    namesdata.rename(columns=(lambda c:c.replace('(','')),inplace=True)
    namesdata.rename(columns=(lambda c:c.replace(' ','_')),inplace=True)
    namesdata.rename(columns=(lambda c:c.lower()),inplace=True)

    return(namesdata)

def doSimplify(namesdata,filename):
    keepcols = ['original_order',
                'far_line_id',
                'family_number',
                'last_name_corrected',
                'first_name_corrected', 
                'other_names',
                'date_of_birth',
                'year_of_birth',
                'sex',
                'citizenship',
                'alien_registration_no.',
                'type_of_original_entry',
                'pre-evacuation_address',
                'pre-evacuation_state',
                'date_of_original_entry',
                'type_of_final_departure',
                'date_of_final_departure',
                'final_departure_state',
                'camp_address_original',
                'camp_address_block',
                'camp_address_barracks',
                'camp_address_room']
    missingcols = []
    #check if cols are missing, add an empty one, then warn
    for label in keepcols:
        if label not in namesdata.columns:
            namesdata[label] = ''
            print('WARNING: {} not found in {}. Adding to consolidated with empty values...'.format(label,os.path.abspath(filename)))
            missingcols.append(label)
    
    #drop extra cols; reorder
    namesdata = namesdata[keepcols]
    #add column for far file identifier
    namesdata.insert(0,'far', os.path.splitext(os.path.basename(filename))[0])

    return(namesdata,missingcols)

def doPrep(inpath,outpath,analyze_only,consolidate,keep_types):
    
    filesindir = 0
    processed = 0
    converted = 0
    totalrows = 0
    analyzefile = os.path.join(outpath, '{:%Y%m%d-%H%M%S}-namesanalyze.txt'.format(datetime.datetime.now()))
    consolidatedfile = os.path.join(outpath, '{:%Y%m%d-%H%M%S}-far_all.csv'.format(datetime.datetime.now()))

    # get all excels
    for root, dirs, files in os.walk(inpath):
        for file in files:
            filesindir +=1
            if file.endswith(".xlsx"):
                infile = os.path.join(root,file)
                print('File: {}'.format(infile))
                #first run write analyze file header
                if not os.path.isfile(analyzefile):
                    if not os.path.isdir(outpath):
                        os.mkdir(outpath)
                    report = open(analyzefile,'w')
                    report.write('names-dataprep.py analyze run at {:%c} on path: {}\n'.format(datetime.datetime.now(),inpath))
                    report.close()
                #import all vals as strings, unless --keep-types set
                if keep_types:
                    namesdata = pandas.read_excel(infile)
                else:
                    namesdata = pandas.read_excel(infile,dtype=str)
                    #replace nan vals with empty string
                    namesdata = namesdata.replace('nan','',regex=True)

                processed +=1
                currentrows = 0
                analysis, currentrows = doAnalyze(namesdata,infile)
                totalrows += currentrows
                report = open(analyzefile,'a')
                report.write(analysis)
                report.close()
                print(analysis)
                if not analyze_only:
                    namesdata = doFilters(namesdata)
                    if consolidate:
                        namesdata, missingcols = doSimplify(namesdata,infile)
                        if not missingcols:
                            #write namesdata to csv; print headers only if first pass
                            namesdata.to_csv(consolidatedfile,mode='a',header=(not os.path.exists(consolidatedfile)),index=False)
                            print('Added filtered csv to consolidated: {}\n'.format(os.path.abspath(file)))
                        else:
                            print('WARNING: Skipping {} for consolidation. Missing columns: {}'.format(os.path.abspath(file),missingcols))
                    else:
                        #save each file to csv
                        filteredfile = os.path.join(outpath, os.path.splitext(file)[0] + '.csv')
                        namesdata.to_csv(filteredfile)
                        print('Wrote filtered csv: {}'.format(filteredfile))

                    converted +=1
    return(filesindir,processed,converted,totalrows)

def main():

    parser = argparse.ArgumentParser(description=description, epilog=epilog,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('inpath', help='Path to directory containing excel files for conversion.')
    parser.add_argument('outpath', nargs='?', default=os.getcwd(), help='Path to write filtered files.')
    parser.add_argument('-A', '--analyze-only', required=False, action='store_true', dest='analyze_only', help='Do not convert files, just output stats file.')
    parser.add_argument('-C', '--consolidate', required=False, action='store_true', dest='consolidate', help='Consolidate filtered CSVs into single file in simple form (name, family id, birthdate only).')
    parser.add_argument('-K', '--keep-types', required=False, action='store_true', dest='keep_types', help='Keep datatypes from original Excel. Imports all data as strings, unless set.')

    args = parser.parse_args()

    started = datetime.datetime.now()
    inputerrs = ''
    filesindir = 0
    processed = 0
    converted = 0
    totalrows = 0

    if not os.path.exists(args.inpath):
        inputerrs + 'CSV directory path does not exist: {}\n'.format(args.inpath)
    if not os.path.exists(args.outpath):
        inputerrs + 'Output path does not exist: {}\n'.format(args.outpath)
    if inputerrs != '':
        print('Error -- script exiting...\n{}'.format(inputerrs))
    else:
        filesindir, processed, converted, totalrows = doPrep(args.inpath,
                                                             os.path.abspath(args.outpath),
                                                             args.analyze_only,
                                                             args.consolidate,
                                                             args.keep_types)

    finished = datetime.datetime.now()
    elapsed = finished - started

    print('Started: {}'.format(started))
    print('Finished: {}'.format(finished))
    print('Elapsed: {}'.format(elapsed))
    print('{} in {}. {} files processed. {} files converted. {} rows total.'.format(filesindir,
                                                                                    os.path.abspath(args.inpath),
                                                                                    processed,
                                                                                    converted,
                                                                                    totalrows))

    return

if __name__ == '__main__':
    main()

