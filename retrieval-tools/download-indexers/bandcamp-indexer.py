""" Bandcamp indexer: Takes a downloaded bandcamp file or zip-file, inspects it, building up
    a list of the artists and songs per artist. Then it creates folders per artist if none exist
    at C:/${Current_User}/Music/Artists if not specified,
    and inserts the music files from each artist into the created or existing folders. 
"""

import argparse

from os import mkdir
from pathlib import Path
from shutil import move
from tqdm import tqdm
from zipfile import ZipFile

""" This function reads the arguments passed to it on the command line. At present this 
    indexer only takes one positional argument, the name of either a music or a zip-file.
    It takes one keyword argument, the destination folder to place the indexed files and their
    created folders into.
    
    If a music file, the file must have a recognized music file extension.

    If a zip file which contains multiple music files, it will shorten the filenames of each of
    the constituent music files in the following pattern:
    Given a file with a pattern ${ARTIST_NAME} - ${ALBUM_NAME} - ${SONG_NAME}, it will remove the
    ${ALBUM_NAME} substring. For example given the pattern 'Four Tet - There is Love in You - Circles'
    would result in the pattern 'Four Tet - Circles', keeping the extension as is.
"""

""" Globals """
valid_extensions = {'aiff', 'mp3', 'wav', 'aac', 'flac', 'alac'}
zipfile_extensions = {'zip'}

def parse_arguments():
    parser = argparse.ArgumentParser(
        prog='Bandcamp File Indexer',
        description='''Takes a downloaded bandcamp file or zip-file, inspects it, building up
    a list of the artists and songs per artist. Then it creates folders per artist if none exist
    at the destination directory specified, or C:/$\\{Current_User\\}/Music/Artists if not specified,
    and inserts the music files from each artist into the created or existing folders.''')
    
    parser.add_argument('filename')
    args = parser.parse_args()
    return args.filename


def get_extension(filepath):
    suffix = filepath.suffix
    return suffix[min(len(suffix), 1):]

def is_zipfile(filepath):
    extension = get_extension(filepath)
    return extension in zipfile_extensions

def is_dir(filepath):
    return Path(filepath).is_dir()

def validate_extension(filepath):
    extension = get_extension(filepath)
    return extension in valid_extensions

def get_artist(filename):
    artist_album_sep = ' - '
    sep_index = filename.find(artist_album_sep)
    if sep_index == -1:
        return None
    return filename[:sep_index].strip()

def unzip_file_to_folder_of_same_name(filepath):
    with ZipFile(filepath.absolute(), 'r') as myzip:
        new_folder_path = filepath.parent.joinpath(filepath.stem)
        myzip.extractall(new_folder_path)
        return new_folder_path
    return None

    
def index_file(filepath):
    filename = filepath.name
    if not validate_extension(filepath):
        print(f'The file type "{get_extension(filepath)}" was not valid. Please enter a file with a type of the supported formats: {", ".join(valid_extensions)}')
        return
    destination_path = Path.home().joinpath('Music', 'Artists')
    artist_name = get_artist(filename)
    if artist_name is None:
        print(f'Could not find Artist name in filename {filename}. Aborting...')
        return
    else:
        destination_path = destination_path.joinpath(artist_name)
        print(f'Destination path is: {destination_path.absolute()}')
        if not destination_path.exists() or not destination_path.is_dir():
            print(f'\nMaking directory at {destination_path} because it does not already exist.')
            mkdir(destination_path)
    move(filepath.absolute(),  destination_path.absolute())
    print('File successfully moved to ' + str(destination_path.joinpath(filename).absolute()))

def main():
    filepath = Path(parse_arguments())
    if is_zipfile(filepath):
        filepath = unzip_file_to_folder_of_same_name(filepath)
        if filepath is None:
            print("Oops...Something went wrong in decompression. Aborting")
            return
    files_to_index = []
    if is_dir(filepath):
        files_to_index = [child for child in filepath.iterdir() if child.is_file()]
    else:
        files_to_index = [filepath]

    for file_to_index in tqdm(files_to_index):
        index_file(file_to_index)

if __name__ == "__main__":
    main()