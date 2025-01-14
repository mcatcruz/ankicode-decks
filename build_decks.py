# Copyright: Daveight and contributors
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
import argparse
import errno
import os
from argparse import ArgumentParser


def encode_csv(text: str):
    """
    Encodes text for CSV format
    :param text: target text
    :return: encoded text
    """
    text = text.replace('"', '""')
    return text


def get_file_content(path: str):
    """
    Reads file content by path
    :param path: file location path
    :return: file text content
    """
    f = None
    try:
        with open(path, "r") as f:
            return f.read()
    except OSError:
        return None
    finally:
        if f is not None:
            f.close()


SOLUTION_SECTIONS = [['header', ''], ['java', 'Java'], ['cpp', 'C++'], ['js', 'JavaScript'], ['python', 'Python']]
parser = ArgumentParser()
parser.add_argument('--debug', dest='debug', action='store_true')
args = parser.parse_args()

for deck_category in os.listdir('src'):
    for deck_subcategory in os.listdir('src/' + deck_category):
        out = ''
        deck_name = deck_category + '/' + deck_subcategory
        if deck_name.startswith('.') or deck_name in ['template']:
            continue
        for name in sorted(os.listdir(f'src/{deck_name}/test_cases')):
            try:
                if not name.endswith('.tsv'):
                    continue
                file = open(f'src/{deck_name}/test_cases/' + name, 'r')
                lines = file.readlines()

                name = name.replace('.tsv', '')
                description = get_file_content(f'src/{deck_name}/descriptions/' + name)
                if description is None:
                    print('can\'t find description for ' + name)
                    continue

                title = get_file_content(f'src/{deck_name}/titles/' + name)
                if title is None:
                    print('can\'t find title for ' + name)
                    continue

                func_name = get_file_content(f'src/{deck_name}/fn_names/' + name)
                if not func_name:
                    print('can\'t find func name for ' + name)
                    continue

                solution = ''
                for section in SOLUTION_SECTIONS:
                    txt = get_file_content(f'src/{deck_name}/solutions/{section[0]}/{name}')
                    if txt is None:
                        print(f'can\'t find {section[0]} solution for {name}')
                        continue
                    if section[1]:
                        solution += '### ' + section[1] + '\n'
                    solution += txt + '\n'

                out += '"' + encode_csv(title.strip()) + '"' + '\t'
                out += '"' + encode_csv(description.strip()) + '"' + '\t'
                out += '"' + func_name.strip() + '"' + '\t'
                out += '"' + encode_csv(solution.strip()) + '"' + '\t'
                out += '"'

                for i, line in enumerate(lines):
                    items = line.strip().split('\t')
                    out += encode_csv(';'.join(items))
                    out += '\n'
                out += '"'
                out += '\n'
                if args.debug:
                    debug_csv_name = f'debug/{deck_category}-{deck_subcategory}/{name}.csv'
                    if not os.path.exists(os.path.dirname(debug_csv_name)):
                        try:
                            os.makedirs(os.path.dirname(debug_csv_name))
                        except OSError as exc:  # Guard against race condition
                            if exc.errno != errno.EEXIST:
                                raise
                    result = open(debug_csv_name, "w+")
                    result.write(out)
                    result.close()
                    out = ''

                if not args.debug:
                    result = open(f'dist/{deck_category}-{deck_subcategory}.csv', 'w+')
                    result.write(out)
                    result.close()
            except FileNotFoundError:
                pass
