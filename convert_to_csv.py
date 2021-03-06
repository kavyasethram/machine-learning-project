import argparse as optparse
import collections
import csv
import simplejson as json

def read_file(file_path):
    #Read in the json dataset file and return a list of python dicts
    file_contents = []
    column_names = set()
    with open(file_path) as fin:
        for line in fin:
            line_contents = json.loads(line)
            column_names.update(
                    set(get_column_names(line_contents).keys())
                    )
            file_contents.append(line_contents)
    return file_contents, column_names

def get_column_names(line_contents, parent_key=''):
    #Return a list of flattened key names given a dict.

    """
    Example:

        line_contents = {
            'a': {
                'b': 2,
                'c': 3,
                },
        }

        will return: ['a.b', 'a.c']

    These will be the column names for the eventual csv file.
    """
    column_names = []
    for k, v in line_contents.items():
        column_name = "{0}.{1}".format(parent_key, k) if parent_key else k
        if isinstance(v, collections.MutableMapping):
            column_names.extend(
                    get_column_names(v, column_name).items()
                    )
        else:
            column_names.append((column_name, v))
    return dict(column_names)

def get_nested_value(d, key):
    #Return a dictionary item given a dictionary `d` and a flattened key from `get_column_names`.
    """
    Example:

        d = {
            'a': {
                'b': 2,
                'c': 3,
                },
        }
        key = 'a.b'

        will return: 2
    
    """
    if '.' not in key:
        if key not in d:
            return None
        return d[key]
    base_key, sub_key = key.split('.', 1)
    if base_key not in d:
        return None
    sub_dict = d[base_key]
    return get_nested_value(sub_dict, sub_key)

def get_row(line_contents, column_names):
    #Return a csv compatible row given column names and a dict.
    row = []
    for column_name in column_names:
        line_value = get_nested_value(
                        line_contents,
                        column_name,
                        )
            # As review text can have multiple lines, make sure that new lines are deleted, and the entire text is just in one line.
            # Also, as we use [ as the csv column seperator for review text, make sure [ does not exist in the review text already.
        if line_value is not None:
            row.append('{0}'.format(line_value).replace(']',')').replace('[','(').replace('\n\n', ' ').replace('\n',' '))
        else:
            row.append('')
    return row

def write_file(file_path, file_contents, column_names):
    #Create and write a csv file given file_contents of our json dataset file and column names.
    delimiter = ';'
    if "review" in file_path:
        # for reviews, use [ as delimiter, as review text usually contains all other characters, and using any other character would yield incorrect columns.
        delimiter='['

    print("Using {} as the delimiter for the csv file.".format(delimiter))    
    with open(file_path, 'w+') as fin:
        csv_file = csv.writer(fin, delimiter=delimiter)
        csv_file.writerow([item for item in column_names])
        for line_contents in file_contents:
            csv_file.writerow(get_row(line_contents, column_names))

if __name__ == '__main__':
    #Convert a yelp dataset file from json to csv	
    parser = optparse.ArgumentParser(
            description='Convert Yelp Dataset Challenge data from JSON format to CSV.',
            )

    parser.add_argument(
            'json_file',
            type=str,
            help='The json file to convert.',
            )

    args = parser.parse_args()

    json_file = args.json_file
    csv_file = 'input_resources/{0}.csv'.format(json_file.split('.json')[0])

    file_contents, column_names = read_file(json_file)
    write_file(csv_file, file_contents, column_names)
    print("Created {} file".format(csv_file))
