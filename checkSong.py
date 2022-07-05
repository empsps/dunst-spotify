#!/usr/bin/env python3

from re import sub
from os import makedirs
from time import sleep, time
from os.path import exists, join
from subprocess import check_output
from urllib.request import urlretrieve
from json import dumps, load, dump, loads
from cv2 import INTER_AREA, resize, imread, imwrite

current_dir = '/home/sph/Dev/dunspotify'
cache_dir = '/home/sph/.local/share/dunspotify'
covers_dir = join(cache_dir, 'covers')
last_saved_song_file = join(cache_dir, 'lastSavedSong.json')
current_song_file = join(cache_dir, 'currentSong.json')
current_song_txt = join(cache_dir, 'currentSong')

# empty json structure to populate files
song_structure = {
    'coverUrl': '',
    'songTitle': '',
    'artist': '',
    'albumTitle': ''
}

json_song_structure = dumps(song_structure)


# create files if they don't exist
def create_files_dirs():
    dirs = [cache_dir, covers_dir]

    for dir in dirs:
        if not exists(dir):
            print('Creating dirs')
            makedirs(dir)

    files = [last_saved_song_file, current_song_file, current_song_txt]

    for file in files:
        if not exists(file):
            with open(file, 'w') as file:
                file.write(json_song_structure)


def get_metadata():
    metadata = check_output(
        ['./spot_metadata'], universal_newlines=True)
    return convert_metadata_json(metadata)


def convert_metadata_json(metadata):
    cover_url = ''
    song_title = ''
    album = ''
    artist = ''

    for line in metadata.split('\n'):
        if 'artUrl' in line:
            cover_url = line.split('|')[1]
        if 'title' in line:
            song_title = line.split('|')[1]
        if 'album' in line:
            album = line.split('|')[1]
        if 'artist' in line:
            artist = line.split('|')[1]

    album_title_formatted = format_album_title(album)

    readyData = {
        'coverUrl': cover_url,
        'songTitle': song_title,
        'album': album,
        'albumFormatted': album_title_formatted,
        'artist': artist
    }

    return dumps(readyData)


# format the album title to give it as a name to the downloaded album cover
def format_album_title(album=None):
    album_title_formatted = ''

    if album is None:
        with open(current_song_file, 'r') as current:
            # get album title from current song file
            album_title_formatted = load(current)['album']
    else:
        album_title_formatted = album

    # make it lowercase
    album_title_formatted = album_title_formatted.lower()
    # remove all characters that ARE NOT letters and numbers
    album_title_formatted = sub('[^ a-zA-Z0-9]', '', album_title_formatted)
    # replace spaces for underscores
    album_title_formatted = album_title_formatted.replace(' ', '_')

    return album_title_formatted


def download_album_cover():
    album_title_formatted = format_album_title()
    cover_url = ''

    with open(current_song_file, 'r') as current:
        cover_url = load(current)['coverUrl'].lower()

    # check if the album cover was previously downloaded
    if exists(join(covers_dir, album_title_formatted + '.png')):
        print('Album cover already saved, no need to download it again.')
        return

    # download the album cover and name it to the formatted album title
    cover_img = join(covers_dir, album_title_formatted) + '.png'
    urlretrieve(cover_url, cover_img)
    resized_image = resize(imread(cover_img), dsize=(
        50, 50), interpolation=INTER_AREA)
    imwrite(cover_img, resized_image)
    print(f'Downloaded {album_title_formatted}.png')


# get currently playing song's metadata and save it to the file
def write_song_to_file():
    # retrieve currently playing song's metadata
    new_song = get_metadata()
    # read last saved and current song files
    with open(last_saved_song_file, 'w') as last, open(current_song_file, 'r+') as current:

        # copy current file contents to last saved
        current_data = load(current)
        dump(current_data, last)

        # write real current song to current file
        current.seek(0)
        current.write(new_song)
        current.truncate()

    with open(current_song_txt, 'w') as txt:
        json_song = loads(new_song)
        for entry in json_song:
            txt.write(f'{entry}|{json_song[entry]}\n')

    compare_songs()


# check if current song is in the same album as last saved song
def compare_songs():
    print('Comparing last saved song with current')
    with open(last_saved_song_file, 'r') as last, open(current_song_file, 'r') as current:

        # read both files
        cover_url_last = load(last)['coverUrl']
        cover_url_current = load(current)['coverUrl']
        if cover_url_last == cover_url_current:
            # if album cover url matches, assume it's in the same album
            print('Still in the same album as last song')
            return
        else:
            # if not, download the album cover
            print('Downloading album cover...')
            download_album_cover()


def song_check_loop():
    start_time = time()
    while True:
        write_song_to_file()
        sleep(2.5 - ((time() - start_time) % 2.5))


def main():
    create_files_dirs()
    song_check_loop()


if __name__ == '__main__':
    main()
