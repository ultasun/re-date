#!/usr/bin/env python3
# Copyright 2022 ultasun, All Rights Reserved.  See the LICENSE file.
#
# This is a very basic utility to convert a .CSV log file generated by the
# Android application `Torque Pro` into a file which may be used by a particular
# analytics visualization tool.
#
# See the TODO tracker at github.com/ultasun/re-date/issues

import csv
import sys
from datetime import datetime

def is_substring_ignore_case(substring, string):
    """
    Check if the substring is a substring of string, ignoring case.
    
    Returns a boolean.
    """
    assert(isinstance(substring, str))
    assert(isinstance(string, str))
    return substring.lower() in string.lower()

def find_index_of_datetime_column(column_list):
    """
    Find the index of the provided list containing the word 'time'.
    Ignores character case.
    
    Returns None if no column with the name 'time' is found.
    """
    assert(isinstance(column_list, list))
    index = 0
    for column in column_list:
        if is_substring_ignore_case('time', column):
            return index
        else:
            index += 1
    return None

def build_new_date_format1(old_date):
    """
    Take a string like
    22-Feb-2021
    and convert it to
    2021-02-22

    Returns a string.
    """
    assert(isinstance(old_date, str))
    old_datetime = datetime.strptime(old_date, '%d-%b-%Y')
    return old_datetime.strftime('%Y-%m-%d')

def build_new_time_format1(old_time):
    """
    Chop the sub-seconds from a string.
    
    Take a string like
    18:15:47.926
    and convert it to
    18:15:47

    Returns a string.
    """
    assert(isinstance(old_time, str))
    return old_time.split('.')[0]

def build_new_datetime_format1(old_datetime, discard_date=True):
    """
    Take a string like
    22-Feb-2021 18:15:47.926
    and convert it to
    2021-02-22 18:15:47

    Returns a string.
    """
    assert(isinstance(old_datetime, str))
    date, time = old_datetime.split(' ')
    
    if not discard_date:
        new_date = build_new_date_format1(date)
        
    new_time = build_new_time_format1(time)

    if not discard_date:
        return new_date + ' ' + new_time
    else:
        return new_time

def build_new_row(row, datetime_column_index=0, discard_date=True):
    """
    Returns a tuple containing the row with the desired transformation.

    The second argument is the index containing the datetime column, as
    detected by find_index_of_datetime_column.

    The third argument specifies to discard the date from the datetime column
    by default, pass 'False' to disable this behavior.
    """
    assert(isinstance(row, list))
    assert(isinstance(datetime_column_index, int))
    result_row = ()
    index = 0
    for column in row:
        if index == datetime_column_index:
            result_row += (build_new_datetime_format1(column, discard_date),)
        else:
            result_row += (column,)
        index += 1

    return result_row

def process_torque_csv_log(input_filename,
                           output_filename,
                           skip_every_nth_row=0, discard_date=True):
    """
    Process a Torque Pro CSV log in such a way that a particular popular
    analytics visualizer is able to draw meaningful visualizations from it.

    Skip every nth row if the third function argument is greater than 1.
    """
    try:
        csv_input_file = open(input_filename, mode='r', newline='')
        csv_output_file = open(output_filename, mode='w', newline='')
        csv_reader = csv.reader(csv_input_file)
        csv_writer = csv.writer(csv_output_file)
        
        column_headers = csv_reader.__next__()
        csv_writer.writerow(column_headers)
        
        datetime_column_index = find_index_of_datetime_column(column_headers)

        index = 0
        for row in csv_reader:
            if skip_every_nth_row > 1 and index % skip_every_nth_row != 0:
                csv_writer.writerow(
                    build_new_row(row,
                                  datetime_column_index, discard_date))
            index += 1

        csv_input_file.close()
        csv_output_file.close()
    except BaseException as e:
        print("Error: ", end='')
        print(e)
        return False

    return True

# Begin program execution if invoked from the command line
if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Provide an input file name to parse as the first argument,\n"
              + "an output file name as the second argument,\n"
              + "optionally an integer 'to skip every nth' as a third,\n"
              + "and optionally the word False, to retain dates in the output.")
        print("")
        print("For example as a bare minimum, input.csv must exist already:")
        print("./python3 ./re-date.py ./input.csv ./output.csv")
        print(" - or -")
        print("./python3 ./re-date.py ./input.csv ./output.csv 3 False")
        print(" - the above example will remove about 33% of the data, "
              + "meanwhile retaining the date and time in the datetime column.")
        print("./python3 ./re-date.py ./input.csv ./output.csv 2")
        print(" - the above example will remove about 50% of the data, "
              + "meanwhile retaining only the time in the datetime column.")
        print("")
        print("The integer provided must be greater than 1.")
        exit()
    elif len(sys.argv) == 3:
        # User provides only input file and output file
        process_torque_csv_log(sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 4:
        # User provides input file, output file, and skip every nth
        process_torque_csv_log(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    elif len(sys.argv) == 5:
        # User provides input file, output file, skip every nth, and False
        # Providing False will cause the tool to retain the date
        process_torque_csv_log(sys.argv[1],
                               sys.argv[2], int(sys.argv[3]), bool(sys.argv[4]))
        
