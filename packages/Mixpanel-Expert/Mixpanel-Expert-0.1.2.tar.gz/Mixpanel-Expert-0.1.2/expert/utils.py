from bisect import bisect_left
import codecs
import simplejson as json
import os
import time
import sys

def binary_search(sorted_list, value, lo=0, hi=None):
    hi = hi if hi is not None else len(sorted_list)
    pos = bisect_left(sorted_list, value, lo, hi)
    return (pos if pos != hi and sorted_list[pos] == value else -1) != -1
'''
def binary_search(value, sorted_list):
    """
    useful to find values in large lists
    cuts down on the time it would take using 'if value in sorted_list' repeatedly
    """
    first = 0
    last = len(sorted_list) - 1
    found = False

    while first <= last and not found:
        midpoint = (first + last)//2
        if sorted_list[midpoint] == value:
            found = True
        else:
            if value < sorted_list[midpoint]:
                last = midpoint - 1
            else:
                first = midpoint - 1

    return found
'''
def file_path(project, filename):
    """
    Keep work area tidy and enable safe_zip to work easily
    """
    folder_path = '/'.join([os.getcwd(), project])
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path + '/' + filename

def export_parse(filename):
    """
    Parse a file of json.dumps back into a list of dictionaries
    """
    with codecs.open(filename, 'r', encoding='utf-8') as users:
        objects_list = [json.loads(user) for user in users.readlines()]

    print 'done parsing from file'
    return objects_list

def export_parse_pager(filename):
    """
    Parse a file of json.dumps back into a list of dictionaries
    """
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            yield obj
    return

def csv_read(filename):
    """
    parse and return a csv file with a header row
    """
    with codecs.open(filename, 'r', encoding='utf-8') as f:
        data = f.read().split('\n')

    header = data[0].split(',')
    data = data[1:]

    """
    catch the situation where there's a trailing newline character
    """
    if not data[-1]:
        data = data[:-1]

    parsed = []
    for line in data:
        temp = {}
        line = line.split(',')
        for i, item in enumerate(header):
            temp[item] = line[i]
        parsed.append(temp)

    return parsed

def csv_write(object_list, export_file):
    """
    export to CSV
    """
    header = set()
    object_list = [flatten(obj) for obj in object_list]
    for obj in object_list:
        header.update(obj.keys())

    with codecs.open(export_file, 'w', encoding='utf-8') as csvfile:
        header = list(header)
        csvfile.write(','.join(header)+'\n')
        for obj in object_list:
            csvfile.write(','.join([unicode(obj.get(item, '')).replace(',', ';') for item in header])+'\n')

    return export_file

def flatten(d, parent_key=None, sep='.'):
    """
    Flattens CSV using dot notation for nested objects
    """
    items = []
    for k,v in d.items():
        new_key = (parent_key + sep if parent_key and parent_key not in [ 'properties', '$properties'] else "") + k
        if isinstance(v, dict):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def safe_zip(folder, secret):
    """
    Whenever we create a file(s) for delivery to a customer it should be zipped and password protected
    """
    if folder == "/":
        return

    zip_command = "zip -P %s -r %s.zip %s" % (secret, folder, folder)
    os.system(zip_command)
    rm_command = "rm -rf %s" % folder
    os.system(rm_command)
    return

def progress(percent, bar_length=50):
    hashes = '=' * int(round(percent * bar_length))
    spaces = '-' * (bar_length - len(hashes))
    sys.stdout.write("\rPercent: [{0}] {1}%".format(hashes + spaces, int(round( percent * 100 ))))
    sys.stdout.flush()


def raw_parse(raw_export):
    pass

def epoch_to_iso(timestamp):
    pass

def iso_to_epoch(iso_time):
    pass
