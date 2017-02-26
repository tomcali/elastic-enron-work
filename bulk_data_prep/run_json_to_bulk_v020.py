# enron json-to-bulk conversion in batches 
# initial json to pre-bulk and pre-bulk to bulk (small batches)

# prepare for Python version 3x features and functions
# commented out for Python 3x users
# from __future__ import division, print_function, unicode_literals

# import packages for email archive work and json file preparation
import os  # operating system commands
import json  # work with JSON files
import codecs  # to handle unicode issues on reads

# function for walking enron email directory and creating json files
def list_all(current_directory):
    for root, dirs, files in os.walk(current_directory):
        level = root.replace(current_directory, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))
# examine the directory structure
# current_directory = os.getcwd()
# list_all(current_directory)

# list files in directory omitting hidden files
def listdir_no_hidden(path):
    start_list = os.listdir(path)
    end_list = []
    for file in start_list:
        if (not file.startswith('.')):
            end_list.append(file)
    return(end_list)

base_directory = '/Users/poweruser/Desktop/json_to_bulk'
input_directory_path = os.path.join(base_directory,'json_input_files')
input_file_names = listdir_no_hidden(path = input_directory_path)

# all mail message files in a file are parsed
# and reformatted json output for bulk input into elasticsearch

output_directory_path = os.path.join(base_directory,'pre_bulk_files')
os.mkdir(output_directory_path)  # directory for the resulting json data files

pre_bulk_file_count = []  # initialize list to maintain the count

for thisfile in input_file_names:
    with open(os.path.join(output_directory_path, thisfile), 'w') as outfile:
        total_file_count = 0  # initialize count of message files
        problem_file_count = 0  # initialize count of problem files    
        print('processing file = ', thisfile)
        
        problem_message_count = 0 # initialize count for this file
        # must process one line at a time due to codec problems
        infile = codecs.open(os.path.join(input_directory_path, thisfile),'r', encoding='utf8')
        for line in infile:
            try:         
                message = infile.readline()  # just one message actually
                # print('reading file ' + thisfile + ' with ' + str(len(messages)) + ' messages')   
                maildata = json.loads(message) # creates dictionary object
                maildata.pop('_id')  # removes unnecessary MongoDB id from dictionary object
                bulk_id = maildata['headers']['Message-ID']  # unique identifier for message
                bulk_metadata = '{"index":{"_index":"enron", "_type":"email", "_id":"' + bulk_id + '"}}'
                outfile.write(bulk_metadata)
                outfile.write('\n')
                json.dump(maildata, outfile)
                outfile.write('\n') 
            except Exception:
                problem_message_count = problem_message_count + 1
        print('number of problem messages: ' + str(problem_message_count))        
       
print('Completed processing of json to pre-bulk for ',\
    len(input_file_names), 'files')

# -----------------------------------------------
# go from pre-bulk to bulk

import math  # for trunc function

base_directory = '/Users/poweruser/Desktop/json_to_bulk'
input_directory_path = os.path.join(base_directory,'pre_bulk_files')
input_file_names = listdir_no_hidden(path = input_directory_path)

# all mail message files in a file are parsed
# and reformatted json output for bulk input into elasticsearch

BULK_FILE_LINE_MAX = 10000

output_directory_path = os.path.join(base_directory,'bulk_files')
os.mkdir(output_directory_path)  # directory for the resulting json data files

total_bulk_files = 0
total_message_count_in = 0
total_message_count_out = 0

for thisfile in input_file_names:
    bulk_file_count = 0  # initialize counter/identifier for bulk file
    jsonline_count = 0  # line count for controlling size of bulk file

    infile = codecs.open(os.path.join(input_directory_path, thisfile),'r', encoding='utf8')
    messages = infile.readlines()
    real_count = len(messages) / BULK_FILE_LINE_MAX
    total_message_count_in = total_message_count_in + len(messages)
    nbatches = math.trunc(real_count)
    if ((real_count - math.trunc(real_count)) != 0):
        nbatches = nbatches + 1
    batch_index = 0
    end_index = 0
    while batch_index < nbatches:
        thisoutfile = thisfile + '_' + str(batch_index)   
        with open(os.path.join(output_directory_path, thisoutfile), 'w') as outfile: 
            start_index = end_index
            end_index = min((end_index + BULK_FILE_LINE_MAX), len(messages))
            for imessage in range(start_index, end_index):
                outfile.writelines(messages[imessage])
                total_message_count_out = total_message_count_out + 1
        batch_index = batch_index +1
        total_bulk_files = total_bulk_files + 1
        
print('Completed processing of pre-bulk to bulk for ',\
    len(input_file_names), 'files')
print(str(total_message_count_in),\
    ' messages on input')
print('Created ',\
    str(total_bulk_files), ' bulk files')
print(str(total_message_count_out),\
    ' messages on output')  