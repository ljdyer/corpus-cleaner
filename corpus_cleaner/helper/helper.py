from os import listdir
from os.path import join
from os import getcwd


# ====================
def save_text_to_file(text: str, file_path: str):

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)


# ====================
def get_text_from_file(file_path: str):

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read().strip()


# ====================
def get_all_file_names(folder_path: str):

    folder_path = join(getcwd(), folder_path)
    return listdir(folder_path)


# ====================
def get_all_file_paths(folder_path: str):

    folder_path = join(getcwd(), folder_path)
    return ([join(folder_path, fn) for fn in listdir(folder_path)])
