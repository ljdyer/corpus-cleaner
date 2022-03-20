import re
from itertools import chain
from os import listdir
from os.path import isdir, isfile, join


# === FILES AND FOLDERS ===

# ====================
def get_text_from_file(file_path: str):
    """Get the text from a .txt file"""

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


# ====================
def save_text_to_file(text: str, file_path: str):
    """Save text to a .txt file"""

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


# ====================
def append_text_to_file(text: str, file_path: str):

    with open(file_path, 'a+', encoding='utf-8') as f:
        f.write(text)


# ====================
def get_subfolder_names(root_folder_path: str) -> list:
    """Get names of all subfolders in a folder"""

    try:
        sf_list = [sf_name for sf_name in listdir(root_folder_path)
                   if isdir(join(root_folder_path, sf_name))]
    except Exception as e:
        print(e)
        return []
    return sf_list


# ====================
def get_txt_file_names_and_paths(folder_path: str) -> list:
    """Get names and paths of all .txt files in a folder"""

    try:
        txt_file_names = [fn for fn in listdir(folder_path)
                          if fn.endswith('.txt')]
    except Exception as e:
        print(e)
        return []
    txt_file_names = natural_sort(txt_file_names)
    return [(fname, join(folder_path, fname)) for fname in txt_file_names]


# ====================
def get_txt_file_names(folder_path: str) -> list:
    """Get names of all .txt files in a folder"""

    names_and_paths = get_txt_file_names_and_paths(folder_path)
    return [n for n, _ in names_and_paths]


# ====================
def get_txt_file_paths(folder_path: str) -> list:
    """Get full paths of all .txt files in a folder"""

    names_and_paths = get_txt_file_names_and_paths(folder_path)
    return [p for _, p in names_and_paths]


# ====================
def natural_sort(fnames: list) -> list:
    """Return natural sort of a list of filenames"""

    fnames = list(sorted(
        fnames,
        key=lambda fn: (
            ''.join([c for c in fn.partition('.') if c.isalpha()]),
            get_num_part_or_zero(fn)
        )
    ))
    return fnames


# ====================
def get_num_part_or_zero(string: str):

    num_part = ''.join([c for c in string if c.isnumeric()])
    try:
        return int(num_part)
    except ValueError:
        return 0


# === LISTS ===

# ====================
def flatten(lis_: list):
    """Flatten a list of lists into a flat list"""

    return list(chain(*lis_))


# === PYSIMPLEGUI ELEMENTS ===

# ====================
def multiline_print_with_regex_highlight(multiline,
                                         text: str,
                                         highlight_color: str,
                                         find_re: str,
                                         replace_re: str = None):

    if replace_re is not None:
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


# ====================
def get_listbox_index(listbox, value: str) -> int:

    values = listbox.get_list_values()
    return values.index(value)
