#!/usr/bin/env python3

from json import dumps, load, dump
from os import makedirs
from os.path import exists, join
from subprocess import check_output
from urllib.request import urlretrieve
from re import sub

currentDir = '/home/sph/Dev/dunspotify'
# cacheDir = "/home/sph/.local/cache/dunspotify"
cacheDir = '/home/sph/Dev/dunspotify'
lastSavedSongFile = join(cacheDir, 'lastSavedSong.json')
currentSongFile = join(cacheDir, 'currentSong.json')

# empty json structure to populate files
songStructure = {
    'coverUrl': '',
    'songTitle': '',
    'artist': '',
    'albumTitle': ''
}

jsonStructure = dumps(songStructure)


# create files if they don't exist
def create_files_dirs():
    if not exists(cacheDir):
        print('Creating dirs')
        makedirs(cacheDir)

    files = [lastSavedSongFile, currentSongFile]

    for file in files:
        if not exists(file):
            with open(file, 'w') as file:
                file.write(jsonStructure)


def get_metadata():
    metadata = check_output(
        ['./spot_metadata'], universal_newlines=True)
    return convert_metadata_json(metadata)


def convert_metadata_json(metadata):
    coverUrl = ''
    songTitle = ''
    album = ''
    artist = ''

    for line in metadata.split('\n'):
        if 'artUrl' in line:
            coverUrl = line.split('|')[1]
        if 'title' in line:
            songTitle = line.split('|')[1]
        if 'album' in line:
            album = line.split('|')[1]
        if 'artist' in line:
            artist = line.split('|')[1]

    readyData = {
        'coverUrl': coverUrl,
        'songTitle': songTitle,
        'album': album,
        'artist': artist
    }

    return dumps(readyData)


# format the album title to give it as a name to the downloaded album cover
def format_album_title():
    albumTitleFormatted = ''
    with open(currentSongFile, 'r') as current:
        # get album title from current song file and make it lowercase
        albumTitleFormatted = load(current)['album'].lower()

    # remove all characters that ARE NOT letters and numbers
    albumTitleFormatted = sub('[^ a-zA-Z0-9]', '', albumTitleFormatted)
    # replace spaces for underscores
    albumTitleFormatted = albumTitleFormatted.replace(' ', '_')

    return albumTitleFormatted


def download_album_cover():
    albumTitleFormatted = format_album_title()
    coverUrl = ''

    with open(currentSongFile, 'r') as current:
        coverUrl = load(current)['coverUrl'].lower()

    # check if the album cover was previously downloaded
    if exists(join(cacheDir, albumTitleFormatted + '.png')):
        print('Album cover already saved, no need to download it again.')
        return

    # download the album cover and name it to the formatted album title
    urlretrieve(coverUrl, albumTitleFormatted + '.png')
    print(f'Downloaded {albumTitleFormatted}.png')


# get currently playing song's metadata and save it to the file
def write_song_to_file():
    # retrieve currently playing song's metadata
    newSong = get_metadata()
    # read last saved and current song files
    with open(lastSavedSongFile, 'w') as last, open(currentSongFile, 'r+') as current:

        # copy current file contents to last saved
        currentData = load(current)
        dump(currentData, last)

        # write real current song to current file
        current.seek(0)
        current.write(newSong)
        current.truncate()


# check if current song is in the same album as last saved song
def compare_songs():
    print('Comparing last saved song with current')
    with open(lastSavedSongFile, 'r') as last, open(currentSongFile, 'r') as current:

        # read both files
        coverUrlLast = load(last)['coverUrl']
        coverUrlCurrent = load(current)['coverUrl']
        if coverUrlLast == coverUrlCurrent:
            # if album cover url matches, assume it's in the same album
            print('Still in the same album as last song')
            return
        else:
            # if not, download the album cover
            print('Downloading album cover...')
            download_album_cover()
            pass


def main():
    # create_files_dirs()
    # convert_metadata_json()
    # download_album_cover()
    # get_metadata()
    compare_songs()
    # write_song_to_file()


if __name__ == '__main__':
    main()
