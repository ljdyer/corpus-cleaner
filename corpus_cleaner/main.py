# main.py

import argparse
import re
from collections import Counter
from os.path import join

import PySimpleGUI as sg

from helper.helper import get_text_from_file
from helper.update_window import (flatten, get_subfolder_names,
                                  get_txt_file_names,
                                  get_txt_file_names_and_paths,
                                  get_txt_file_paths,
                                  multiline_print_with_regex_highlight)

DEBUG_FOLDER = "E:\\TED_Talks"


# ====================
def get_args():
    """Get command-line arguments"""

    parser = argparse.ArgumentParser(
        description='Corpus Cleaner',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--debug',
                        action=argparse.BooleanOptionalAction,
                        type=bool,
                        help='launch in debug mode')
    parser.set_defaults(debug=False)
    return parser.parse_args()


# ====================
def handle_folder_change(window, root_folder_path: str):
    """Handle change to folder selection

    1. Update list of subfolders.
    2. Clear list of files
    3. Clear all text displays"""

    sf_list = get_subfolder_names(root_folder_path)
    window["-SUBFOLDER-"].update(sf_list)
    window["-FILE-"].update([])
    clear_text_displays(window)
    clear_find_replace_inputs(window)


# ====================
def handle_subfolder_change(window, subfolder_path: str):
    """Handle change to subfolder selection

    1. Update list of files
    2. Clear all text displays"""

    f_list = get_txt_file_names(subfolder_path)
    window["-FILE-"].update(f_list)
    clear_text_displays(window)
    clear_find_replace_inputs(window)


# ====================
def handle_file_change(window, text: str, find_re: str, replace_re: str):

    update_before_after(window, text, find_re, replace_re)


# ====================
def clear_text_displays(window):

    window["-BEFORE-"].update("")
    window["-AFTER-"].update("")


# ====================
def clear_find_replace_inputs(window):

    window["-FIND-"].update("")
    window["-REPLACE-"].update("")


# ====================
def update_before_after(window, text: str, find_re: str,
                        replace_re: str = None):

    if not find_re:
        window["-BEFORE-"].update(text)
        window["-AFTER-"].update("")
        return

    multiline_print_with_regex_highlight(window["-BEFORE-"], text,
                                         "red", find_re)

    if replace_re:
        multiline_print_with_regex_highlight(window["-AFTER-"], text, "green",
                                             find_re, replace_re)
    else:
        window["-AFTER-"].update("")


# ====================
def show_occurences(window, find_re: str, subfolder_path: str):

    if not find_re:
        window["-INSTANCES-"].update("")
        window["-FILES_IN-"].update("")
        return

    file_paths = get_txt_file_paths(subfolder_path)
    try:
        all_matches = flatten([re.findall(find_re, get_text_from_file(fp))
                               for fp in file_paths])
    except re.error:
        print('Invalid regex.')
        return
    counts = Counter(all_matches)
    count_list = [f'{instance}: {count}'
                  for instance, count in counts.most_common()]
    window["-INSTANCES-"].update(count_list)
    window["-FILES_IN-"].update("")


def show_files_in(substr: str, subfolder_path: str):

    file_names_and_paths = get_txt_file_names_and_paths(subfolder_path)
    counts = [
        (fname, get_text_from_file(fpath).count(substr))
        for fname, fpath in file_names_and_paths
        if substr in get_text_from_file(fpath)
    ]
    count_list = [f'{fname}: {count}'
                  for fname, count in sorted(counts, key=lambda x: x[1])]
    window["-FILES_IN-"].update(count_list)


# === WINDOW LAYOUT ===

file_list_column = [
    [
        sg.Text("Corpus folder:"),
        sg.In(size=(20, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-SUBFOLDER-"
        )
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 60), key="-FILE-"
        )
    ],
]

text_display_column = [
    [
        sg.Text("Find:"),
        sg.In(size=(25, 1), enable_events=True, key="-FIND-"),
        sg.Text("Replace:"),
        sg.In(size=(25, 1), enable_events=True, key="-REPLACE-"),
    ],
    [
        sg.Multiline(
            key="-BEFORE-",
            size=(100, 40)),
        sg.Multiline(
            key="-AFTER-",
            size=(100, 40))
    ],
    [
        sg.HSeparator()
    ],
    [
        sg.Button("Update", key="-UPDATE-")
    ],
    [
        sg.Listbox(
            values=[],
            enable_events=True,
            size=(60, 25),
            key="-INSTANCES-"
        ),
        sg.Listbox(
            values=[],
            enable_events=True,
            size=(60, 25),
            key="-FILES_IN-"
        ),
    ]

]

layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(text_display_column),
    ]
]

# === INITIALIZE WINDOW ===

window = sg.Window("Corpus Cleaner", layout).Finalize()
window.Maximize()


# === CHECK FOR DEBUG MODE ===

args = get_args()
debug = int(args.debug)
if debug:
    print('Debug mode.')
    root_folder_path = DEBUG_FOLDER
    handle_folder_change(window, root_folder_path)

# === EVENT LOOP ===

find_re = ""
replace_re = ""

while True:

    event, values = window.read()

    # --- EXIT PROGRAM ---
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # --- ROOT FOLDER CHANGED ---
    if event == "-FOLDER-":
        root_folder_path = values["-FOLDER-"]
        handle_folder_change(window, root_folder_path)

    # --- SUBFOLDER CHANGED ---
    elif event == "-SUBFOLDER-":
        subfolder_name = values["-SUBFOLDER-"][0]
        subfolder_path = join(root_folder_path, subfolder_name)
        handle_subfolder_change(window, subfolder_path)

    # --- FILE CHANGED ---
    elif event == "-FILE-" and values['-FILE-']:
        file_name = values["-FILE-"][0]
        file_path = join(subfolder_path, file_name)
        text = get_text_from_file(file_path)
        handle_file_change(window, text, find_re, replace_re)

    # --- 'FIND' REGEX CHANGED ---
    elif event == "-FIND-":
        find_re = values["-FIND-"]
        update_before_after(window, text, find_re, replace_re)

    # --- 'REPLACE' REGEX CHANGED ---
    elif event == "-REPLACE-":
        replace_re = values["-REPLACE-"]
        update_before_after(window, text, find_re, replace_re)

    # --- 'UPDATE' BUTTON CLICKED ---
    elif event == "-UPDATE-":
        show_occurences(window, find_re, subfolder_path)

    elif event == "-INSTANCES-":
        substr = values["-INSTANCES-"][0].rpartition(':')[0]

        show_files_in(substr, subfolder_path)



window.close()
