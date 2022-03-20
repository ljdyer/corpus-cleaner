import PySimpleGUI as sg

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
        sg.Button('Replace in all files', key="-SAVE-"),
        sg.Button('Normalize unicode (remove diacritics)', key="-NORMALIZE-", button_color="red"),
        sg.Button('Convert all to lowercase', key="-LOWERCASE-", button_color="red")
    ]
]

MAIN_COLUMN = [
    FIND_REPLACE_INPUT_ROW,
    BEFORE_AFTER_PREVIEW_ROW,
    [sg.Button('Save changes to this file', key="-SAVE_CHANGES-")],
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
