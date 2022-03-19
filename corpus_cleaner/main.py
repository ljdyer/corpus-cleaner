# main.py

import argparse
import re
from collections import Counter
from os.path import join, isdir
from os import mkdir
from datetime import datetime

import PySimpleGUI as sg

from helper.helper import get_text_from_file, save_text_to_file
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
def handle_file_change(window, text: str, find_re: str, replace_re: str = ""):

    update_before_after(window, text, find_re, replace_re)


# ====================
def clear_text_displays(window):

    window["-BEFORE-"].update("")
    window["-AFTER-"].update("")


# ====================
def clear_find_replace_inputs(window):

    window["-FIND-"].update("")
    window["-REPLACE-"].update("")
    reset_occurrence_info(window)


# ====================
def update_before_after(window, text: str, find_re: str,
                        replace_re: str = None):

    if not find_re:
        window["-BEFORE-"].update(text)
        window["-AFTER-"].update("")
        return

    multiline_print_with_regex_highlight(window["-BEFORE-"], text,
                                         "red", find_re)
    multiline_print_with_regex_highlight(window["-AFTER-"], text, "green",
                                         find_re, replace_re)


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
    all_matches = [match[0] if isinstance(match, tuple) else match
                   for match in all_matches]
    counts = Counter(all_matches)
    count_list = [f'{instance}: {count}'
                  for instance, count in counts.most_common()]
    window["-INSTANCES-"].update(count_list, disabled=False)
    window["-FILES_IN-"].update("")


# ====================
def show_files_in(substr: str, subfolder_path: str):

    file_names_and_paths = get_txt_file_names_and_paths(subfolder_path)
    counts = [
        (fname, get_text_from_file(fpath).count(substr))
        for fname, fpath in file_names_and_paths
        if substr in get_text_from_file(fpath)
    ]
    count_list = [f'{fname}: {count}'
                  for fname, count in sorted(counts,
                                             key=lambda x: x[1], reverse=True)]
    window["-FILES_IN-"].update(count_list, disabled=False)


# ====================
def reset_occurrence_info(window):

    window["-INSTANCES-"].update([])
    window["-FILES_IN-"].update([])


# ====================
def get_listbox_index(listbox, value: str) -> int:

    values = listbox.get_list_values()
    return values.index(value)


# ====================
def save(window, root_folder_path: str, subfolder_name: str, find_re: str,
         replace_re: str, save_folder_name: str, note: str):

    subfolder_path = join(root_folder_path, subfolder_name)
    save_folder_path = join(root_folder_path, save_folder_name)
    if isdir(save_folder_path):
        proceed = sg.PopupYesNo('A subfolder with this name already exists.',
                                'Overwrite?')
        if proceed != 'Yes':
            return
    else:
        mkdir(save_folder_path)

    if not find_re:
        sg.PopupOK("'Find' regex is not defined.")
        return
    if not replace_re:
        sg.PopupOK("'Replace' regex is not defined.")
        return

    before_files = get_txt_file_names_and_paths(subfolder_path)
    for fn, fp in before_files:
        before_text = get_text_from_file(fp).strip()
        new_text = re.sub(find_re, replace_re, before_text)
        new_fp = join(save_folder_path, fn)
        save_text_to_file(new_text, new_fp)

    # Update log file
    update_save_log(root_folder_path, subfolder_name, save_folder_name,
                    find_re, replace_re, note)

    handle_folder_change(window, root_folder_path)


# ====================
def update_save_log(root_folder_path: str, subfolder_name: str, save_folder_name: str,
                    find_re: str, replace_re: str, note: str):

    with open(join(root_folder_path, 'log.txt'), 'a+', encoding='utf-8') as log_file:
        lines = [
            f'Time: {str(datetime.now())}',
            f'Previous subfolder: {subfolder_name}',
            f'New subfolder: {save_folder_name}',
            f"'Find' regex: /{find_re}/",
            f"'Replace' regex: /{replace_re}/",
            f'Note: {note}',
            '====================',
            ''
        ]
        log_file.write('\n'.join(lines))


def add_spot_change_to_log(file_name: str):
    with open(join(root_folder_path, 'log.txt'), 'a+', encoding='utf-8') as log_file:
        lines = [
            f'Time: {str(datetime.now())}',
            f'Spot change to file: {file_name}',
            '====================',
            ''
        ]
        log_file.write('\n'.join(lines))


# === WINDOW LAYOUT ===

FILE_SELECTION_COLUMN = [
    [
        sg.Text("Root folder:"),
        sg.In(size=(20, 1), enable_events=True, key="-FOLDER-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 20), key="-SUBFOLDER-"
        ),
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(40, 60), key="-FILE-"
        )
    ],
]

FIND_REPLACE_INPUT_ROW = [
    sg.Text("Find:"),
    sg.In(size=(25, 1), enable_events=True, key="-FIND-"),
    sg.Text("Replace:"),
    sg.In(size=(25, 1), enable_events=True, key="-REPLACE-"),
]

BEFORE_AFTER_PREVIEW_ROW = [
    sg.Multiline(
        key="-BEFORE-",
        size=(100, 40)),
    sg.Multiline(
        key="-AFTER-",
        size=(100, 40))
]

OCCURRENCE_INFO_COLUMN = [
    [
        sg.Button("Update", key="-UPDATE-")
    ],
    [
        sg.Listbox(values=[], enable_events=True, size=(60, 25), 
                   key="-INSTANCES-", disabled=True),
        sg.Listbox(values=[], enable_events=True, size=(60, 25),
                   key="-FILES_IN-", disabled=True)
    ]
]

SAVE_COLUMN = [
    [
        sg.Text("New folder name:"),
        sg.In(size=(40, 1), key="-SAVE_FOLDER-"),
    ],
    [
        sg.Text("Note (optional)"),
        sg.In(size=(40, 1), key="-NOTE-"),
    ],
    [
        sg.Button('Save', key="-SAVE-")
    ]
]

MAIN_COLUMN = [
    FIND_REPLACE_INPUT_ROW,
    BEFORE_AFTER_PREVIEW_ROW,
    [sg.Button('Save changes', key="-SAVE_CHANGES-")],
    [sg.HSeparator()],
    [
        sg.Column(OCCURRENCE_INFO_COLUMN),
        sg.VSeperator(),
        sg.Column(SAVE_COLUMN, vertical_alignment='t')
    ]
]

WINDOW_LAYOUT = [
    [
        sg.Column(FILE_SELECTION_COLUMN),
        sg.VSeperator(),
        sg.Column(MAIN_COLUMN),
    ]
]

# === INITIALIZE WINDOW ===

window = sg.Window("Corpus Cleaner", WINDOW_LAYOUT).Finalize()
window.Maximize()
find_re = ""
replace_re = ""
text = ""


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

    # --- EXIT PROGRAM ---
    if event == "Exit" or event == sg.WIN_CLOSED:
        break

    # --- ROOT FOLDER CHANGED ---
    if event == "-FOLDER-":
        root_folder_path = values["-FOLDER-"]
        handle_folder_change(window, root_folder_path)

    # --- SUBFOLDER CHANGED ---
    elif event == "-SUBFOLDER-" and values["-SUBFOLDER-"]:
        subfolder_name = values["-SUBFOLDER-"][0]
        subfolder_path = join(root_folder_path, subfolder_name)
        handle_subfolder_change(window, subfolder_path)

    # --- FILE CHANGED ---
    elif event == "-FILE-" and values['-FILE-']:
        file_name = values["-FILE-"][0]
        file_path = join(subfolder_path, file_name)
        text = get_text_from_file(file_path).strip()
        handle_file_change(window, text, find_re, replace_re)

    # --- 'FIND' REGEX CHANGED ---
    elif event == "-FIND-":
        find_re = values["-FIND-"]
        replace_re = values["-REPLACE-"]
        reset_occurrence_info(window)
        update_before_after(window, text, find_re, replace_re)

    # --- 'REPLACE' REGEX CHANGED ---
    elif event == "-REPLACE-":
        find_re = values["-FIND-"]
        replace_re = values["-REPLACE-"]
        update_before_after(window, text, find_re, replace_re)

    # --- 'UPDATE' BUTTON CLICKED ---
    elif event == "-UPDATE-":
        show_occurences(window, find_re, subfolder_path)

    elif event == "-INSTANCES-" and values["-INSTANCES-"]:
        substr = values["-INSTANCES-"][0].rpartition(':')[0]
        show_files_in(substr, subfolder_path)

    elif event == "-FILES_IN-" and values["-FILES_IN-"]:
        file_name = values["-FILES_IN-"][0].rpartition(':')[0]
        file_path = join(subfolder_path, file_name)
        index = get_listbox_index(window["-FILE-"], file_name)
        window["-FILE-"].update(set_to_index=index, scroll_to_index=index-5)
        text = get_text_from_file(file_path).strip()
        handle_file_change(window, text, find_re, replace_re)

    # --- 'SAVE' BUTTON CLICKED ---
    elif event == "-SAVE-":
        save_folder_name = values["-SAVE_FOLDER-"]
        note = values["-NOTE-"]
        save(window, root_folder_path, subfolder_name,
             find_re, replace_re, save_folder_name, note)
    
    # --- 'SAVE CHANGES' BUTTON CLICKED ---
    elif event == "-SAVE_CHANGES-":
        text = values["-BEFORE-"]
        save_path = file_path
        save_text_to_file(text, file_path)
        handle_folder_change(window, root_folder_path)
        add_spot_change_to_log(file_name)

window.close()
