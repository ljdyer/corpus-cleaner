from os import listdir
from os.path import join, isdir, isfile
import re


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
def update_subfolders(window, root_folder_path: str):

    sf_list = get_subfolder_names(root_folder_path)
    window["-SUBFOLDER-"].update(sf_list)


# ====================
def update_files(window, subfolder_path: str):

    f_list = get_txt_file_names(subfolder_path)
    window["-FILE-"].update(f_list)


# ====================
def update_before(window, text: str, find_re: str, replace_re: str):

    if not find_re:
        window["-BEFORE-"].update(text)

    else:
        try:
            text_tagged = re.sub(rf'({find_re})', r'***\1***', text)
        except re.error:
            print("Not a valid regex!")
            return

        text_parts = text_tagged.split('***')
        window["-BEFORE-"].update("")
        for index, part in enumerate(text_parts):
            if index % 2 == 0:
                window["-BEFORE-"].update(part, append=True)
            else:
                window["-BEFORE-"].update(
                    part, background_color_for_value="red", append=True
                )

        if replace_re:
            try:
                text_tagged = re.sub(
                    rf'{find_re}', rf'***{replace_re}***', text
                )
            except re.error:
                print("Not a valid regex!")
                return

            text_parts = text_tagged.split('***')
            window["-AFTER-"].update("")
            for index, part in enumerate(text_parts):
                if index % 2 == 0:
                    window["-AFTER-"].update(part, append=True)
                else:
                    window["-AFTER-"].update(
                        part, background_color_for_value="green", append=True
                    )


