# handlers.py

import re
from collections import Counter
from datetime import datetime
from os import mkdir
from os.path import isdir, join

import PySimpleGUI as sg

from helper.helper import (append_text_to_file, flatten, get_listbox_index,
                           get_subfolder_names, get_text_from_file,
                           get_txt_file_names, get_txt_file_names_and_paths,
                           get_txt_file_paths,
                           multiline_print_with_regex_highlight,
                           save_text_to_file)


# === EVENT HANDLERS ===

# ====================
def handle_folder_change(window, values):
    """Handle change to folder selection"""

    root_folder_path = values["-FOLDER-"]
    sf_list = get_subfolder_names(root_folder_path)
    window["-SUBFOLDER-"].update(sf_list)
    window["-FILE-"].update([])
    clear_before_after(window)
    clear_find_replace(window)


# ====================
def handle_subfolder_change(window, values):
    """Handle change to subfolder selection"""

    if not values["-SUBFOLDER-"]:
        return
    subfolder_path = get_subfolder_path(values)
    f_list = get_txt_file_names(subfolder_path)
    window["-FILE-"].update(f_list)
    clear_before_after(window)
    clear_find_replace(window)


# ====================
def handle_file_change(window, values):
    """Handle change to file selection"""

    if not values["-FILE-"]:
        return
    file_path = get_file_path(window)
    text = get_text_from_file(file_path).strip()
    window["-BEFORE-"].update(text)
    update_before_after(window, values)


# ====================
def handle_find_re_change(window, values):

    clear_occurrence(window)
    update_before_after(window, values)


# ====================
def handle_replace_re_change(window, values):

    update_before_after(window, values)


# ====================
def update_before_after(window, values):

    find_re = values["-FIND-"]
    replace_re = values["-REPLACE-"]
    text = window["-BEFORE-"].get()

    if not find_re:
        window["-BEFORE-"].update(text)
        window["-AFTER-"].update(text)
        return

    multiline_print_with_regex_highlight(window["-BEFORE-"], text,
                                         "red", find_re)
    multiline_print_with_regex_highlight(window["-AFTER-"], text, "green",
                                         find_re, replace_re)


# ====================
def handle_update_click(window, values):

    find_re = values["-FIND-"]
    subfolder_path = get_subfolder_path(values)

    if not find_re:
        window["-INSTANCES-"].update("")
        window["-FILES_IN-"].update("")
        return

    file_paths = get_txt_file_paths(subfolder_path)
    try:
        all_matches = flatten([re.findall(find_re, get_text_from_file(fp))
                               for fp in file_paths])
    except re.error:
        sg.PopupOK("'Find' regex is invalid.")
        return

    all_matches = [match[0] if isinstance(match, tuple) else match
                   for match in all_matches]
    counts = Counter(all_matches)
    count_list = [f'{instance}: {count}'
                  for instance, count in counts.most_common()]
    window["-INSTANCES-"].update(count_list, disabled=False)
    window["-FILES_IN-"].update("")


# ====================
def handle_substr_change(window, values):

    if not values["-INSTANCES-"]:
        return

    substr = values["-INSTANCES-"][0].rpartition(':')[0]
    subfolder_path = get_subfolder_path(values)

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
def handle_files_in_click(window, values):

    if not values["-FILES_IN-"]:
        return

    file_name = values["-FILES_IN-"][0].rpartition(':')[0]
    index = get_listbox_index(window["-FILE-"], file_name)
    window["-FILE-"].update(set_to_index=index, scroll_to_index=index-5)
    handle_file_change(window, values)


# ====================
def handle_save_click(window, values):

    new_subfolder_name = values["-SAVE_FOLDER-"]
    find_re = values["-FIND-"]
    replace_re = values["-REPLACE-"]
    old_subfolder_path = get_subfolder_path(values)
    new_subfolder_path = join(values["-FOLDER-"], new_subfolder_name)

    if isdir(new_subfolder_path):
        proceed = sg.PopupYesNo('A subfolder with this name already exists.',
                                'Overwrite?')
        if proceed != 'Yes':
            return
    else:
        mkdir(new_subfolder_path)

    if not find_re:
        sg.PopupOK("'Find' regex is not defined.")
        return
    if not replace_re:
        sg.PopupOK("'Replace' regex is not defined.")
        return

    # Generate new files
    old_files = get_txt_file_names_and_paths(old_subfolder_path)
    for fn, fp in old_files:
        old_text = get_text_from_file(fp).strip()
        new_text = re.sub(find_re, replace_re, old_text)
        new_fp = join(new_subfolder_path, fn)
        save_text_to_file(new_text, new_fp)

    # Update log file
    log_lines = [
        f'Time: {str(datetime.now())}',
        f'Previous subfolder: {values["-SUBFOLDER-"]}',
        f'New subfolder: {new_subfolder_name}',
        f"'Find' regex: /{find_re}/",
        f"'Replace' regex: /{replace_re}/",
        f'Note: {values["-NOTE-"]}',
        '===================='
    ]
    log_text = '\n'.join(log_lines) + "\n\n"
    log_file_path = get_log_file_path(values)
    append_text_to_file(log_text, log_file_path)

    handle_folder_change(window, values)
    # TODO: Select newly-created subfolder


# ====================
def handle_save_changes_click(window, values):

    text = values["-BEFORE-"]
    file_path = get_file_path(values)
    save_text_to_file(text, file_path)

    log_lines = [
        f'Time: {str(datetime.now())}',
        f'Spot change to file: {values["-FILE-"]}',
        '===================='
    ]
    log_text = '\n'.join(log_lines) + "\n\n"
    log_file_path = get_log_file_path(values)
    append_text_to_file(log_text, log_file_path)


# === GET VALUES ===

# ====================
def get_subfolder_path(values):

    return join(values["-FOLDER-"],
                values["-SUBFOLDER-"][0])


# ====================
def get_file_path(window):

    return join(window["-FOLDER-"].get(),
                window["-SUBFOLDER-"].get()[0],
                window["-FILE-"].get()[0])


# ====================
def get_log_file_path(values):

    return join(values["-FOLDER-"], "log.txt")


# === CLEAR VALUES ===

# ====================
def clear_before_after(window):

    window["-BEFORE-"].update("")
    window["-AFTER-"].update("")


# ====================
def clear_find_replace(window):

    window["-FIND-"].update("")
    window["-REPLACE-"].update("")
    clear_occurrence(window)


# ====================
def clear_occurrence(window):

    window["-INSTANCES-"].update([])
    window["-FILES_IN-"].update([])
