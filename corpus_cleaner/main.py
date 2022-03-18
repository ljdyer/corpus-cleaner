# img_viewer.py

import argparse
import re
from os.path import join

import PySimpleGUI as sg

from helper.helper import get_text_from_file
from helper.update_window import (update_files, update_before,
                                  update_subfolders)

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


# def log_instances(regex: str, subfolder_path: str) -> dict:
#     """Log frequencies of all instances of a regex in a list of files"""

#     files = [file for file in subfolder_path]
#     all_matches = flatten([re.findall(regex, get_text_from_file(fp))
#                            for fp in file_paths])
#     counts = Counter(all_matches)
#     counter_to_csv(counts, output_fp)


# === WINDOW LAYOUT ===

file_list_column = [
    [
        sg.Text("Corpus folder:"),
        sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
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
            size=(100, 100)),
        sg.Multiline(
            key="-AFTER-",
            size=(100, 100))
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
    update_subfolders(window, root_folder_path)

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
        update_subfolders(window, root_folder_path)

    # --- SUBFOLDER CHANGED ---
    elif event == "-SUBFOLDER-":
        subfolder_name = values["-SUBFOLDER-"][0]
        subfolder_path = join(root_folder_path, subfolder_name)
        update_files(window, subfolder_path)

    # --- FILE CHANGED ---
    elif event == "-FILE-":
        file_name = values["-FILE-"][0]
        file_path = join(subfolder_path, file_name)
        text = get_text_from_file(file_path)
        update_before(window, text, find_re, replace_re)

    # --- 'FIND' REGEX CHANGED ---
    elif event == "-FIND-":
        find_re = values["-FIND-"]
        update_before(window, text, find_re, replace_re)

    # --- 'REPLACE' REGEX CHANGED ---
    elif event == "-REPLACE-":
        replace_re = values["-REPLACE-"]
        update_before(window, text, find_re, replace_re)


window.close()
