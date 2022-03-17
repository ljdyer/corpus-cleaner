# img_viewer.py

import PySimpleGUI as sg
import os.path
import re
from helper.helper import get_text_from_file

root_folder = ""
SUBFOLDER = ""
FILE = ""

# First the window layout in 2 columns

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

# For now will only show the name of the file that was chosen
text_display_column = [
    [
        sg.Text("Find:"),
        sg.In(size=(25, 1), enable_events=True, key="-FIND-"),
        sg.Text("Replace:"),
        sg.In(size=(25, 1), enable_events=True, key="-REPLACE-"),
    ],
    [
        sg.Multiline(
            key="-PREVIEW-",
            size=(200, 100))
    ]
]

# ----- Full layout -----
layout = [
    [
        sg.Column(file_list_column),
        sg.VSeperator(),
        sg.Column(text_display_column),
    ]
]

window = sg.Window("Corpus Cleaner", layout).Finalize()
window.Maximize()

# Run the Event Loop
while True:
    event, values = window.read()
    if event == "Exit" or event == sg.WIN_CLOSED:
        break
    # Folder name was filled in, make a list of files in the folder
    if event == "-FOLDER-":
        root_folder = values["-FOLDER-"]
        try:
            # Get list of files in folder
            file_list = os.listdir(root_folder)
        except Exception as e:
            print(e)
            file_list = []

        fnames = [
            sf for sf in file_list
            if os.path.isdir(os.path.join(root_folder, sf))
        ]
        window["-SUBFOLDER-"].update(fnames)

    elif event == "-SUBFOLDER-":
        subfolder = values["-SUBFOLDER-"][0]
        try:
            # Get list of files in folder
            file_list = os.listdir(os.path.join(root_folder, subfolder))
        except Exception as e:
            print(e)
            file_list = []

        fnames = [
            sf for sf in file_list
            if os.path.isfile(os.path.join(root_folder, subfolder, sf))
        ]
        window["-FILE-"].update(fnames)

    elif event == "-FILE-":
        FILE = values["-FILE-"][0]
        text = get_text_from_file(os.path.join(root_folder, subfolder, FILE))
        window["-PREVIEW-"].update(text)

    elif event == "-FIND-":
        find_re = values["-FIND-"]
        for match in re.finditer(find_re, text):
            print(match.span())


    # elif event == "-FILE LIST-":  # A file was chosen from the listbox
        # try:
        #     filename = os.path.join(
        #         values["-FOLDER-"], values["-FILE LIST-"][0]
        #     )
        #     window["-TOUT-"].update(filename)
        #     window["-IMAGE-"].update(filename=filename)

        # except:
        #     pass

window.close()
