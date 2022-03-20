# main.py

import argparse
from os.path import join

import PySimpleGUI as sg

from helper.helper import get_text_from_file
from handlers import (handle_file_change, handle_files_in_click,
                      handle_find_re_change, handle_folder_change,
                      handle_replace_re_change, handle_save_changes_click,
                      handle_save_click, handle_subfolder_change,
                      handle_substr_change, handle_update_click, handle_lower_click, handle_normalize_click)
from layout import WINDOW_LAYOUT

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


# === INITIALIZE WINDOW ===

window = sg.Window("Corpus Cleaner", WINDOW_LAYOUT).Finalize()
window.Maximize()


# === CHECK FOR DEBUG MODE ===

args = get_args()
debug = int(args.debug)
if debug:
    print('Debug mode.')
    root_folder_path = DEBUG_FOLDER
    window["-FOLDER-"].update(root_folder_path)
    handle_folder_change(window, root_folder_path)
    subfolder_path = join(root_folder_path, 'original')
    handle_subfolder_change(window, subfolder_path)
    file_path = join(subfolder_path, '1.txt')
    text = get_text_from_file(file_path).strip()
    find_re = 'm+'
    handle_file_change(window, text, find_re)


# === EVENT LOOP ===

while True:

    event, values = window.read()

    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    if event == "-FOLDER-":
        handle_folder_change(window, values)
    elif event == "-SUBFOLDER-":
        handle_subfolder_change(window, values)
    elif event == "-FILE-":
        handle_file_change(window, values)
    elif event == "-FIND-":
        handle_find_re_change(window, values)
    elif event == "-REPLACE-":
        handle_replace_re_change(window, values)
    elif event == "-UPDATE-":
        handle_update_click(window, values)
    elif event == "-INSTANCES-":
        handle_substr_change(window, values)
    elif event == "-FILES_IN-":
        handle_files_in_click(window, values)
    elif event == "-SAVE_CHANGES-":
        handle_save_changes_click(window, values)
    elif event == "-SAVE-":
        handle_save_click(window, values)
    elif event == "-NORMALIZE-":
        handle_normalize_click(window, values)
    elif event == "-LOWERCASE-":
        handle_lower_click(window, values)
    else:
        print(f'Event not handled: {event}')

window.close()
