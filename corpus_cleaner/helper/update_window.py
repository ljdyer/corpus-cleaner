from os import listdir
from os.path import join, isdir, isfile
from itertools import chain
import re


# ====================
def flatten(lis_: list):
    """Flatten a list of lists into a flat list"""

    return list(chain(*lis_))


# ====================
def get_subfolder_names(root_folder_path: str) -> list:

    try:
        sf_list = [sf_name for sf_name in listdir(root_folder_path)
                   if isdir(join(root_folder_path, sf_name))]
    except Exception as e:
        print(e)
        sf_list = []
    return sf_list


# ====================
def get_txt_file_names(folder_path: str) -> list:

    try:
        f_list = [f_name for f_name in listdir(folder_path)
                  if isfile(join(folder_path, f_name))
                  and f_name.endswith('.txt')]
    except Exception as e:
        print(e)
        f_list = []
    return f_list


# ====================
def get_txt_file_paths(folder_path: str) -> list:

    txt_file_names = get_txt_file_names(folder_path)
    if txt_file_names:
        return [join(folder_path, fname) for fname in txt_file_names]
    else:
        return []


# ====================
def get_txt_file_names_and_paths(folder_path: str) -> list:

    txt_file_names = get_txt_file_names(folder_path)
    if txt_file_names:
        return [(fname, join(folder_path, fname)) for fname in txt_file_names]
    else:
        return []


# ====================
def multiline_print_with_regex_highlight(multiline,
                                         text: str,
                                         highlight_color: str,
                                         find_re: str,
                                         replace_re: str = None):

    if replace_re:
        replace_re = rf'***{replace_re}***'
        find_re = rf'{find_re}'
    else:
        replace_re = r'***\1***'
        find_re = rf'({find_re})'

    try:
        text_tagged = re.sub(find_re, replace_re, text)
    except re.error:
        print("Not a valid regex!")
        return

    text_parts = text_tagged.split('***')
    multiline.update("")

    for index, part in enumerate(text_parts):
        if index % 2 == 0:
            multiline.update(part, append=True)
        else:
            multiline.update(
                part,
                background_color_for_value=highlight_color,
                append=True
            )
