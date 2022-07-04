#!/usr/bin/env python3

from json import dumps, load, dump
from os import makedirs
from os.path import exists, join
from subprocess import check_output
from urllib.request import urlretrieve
from re import sub

currentDir = "/home/sph/Dev/dunspotify"
# cacheDir = "/home/sph/.local/cache/dunspotify"
cacheDir = "/home/sph/Dev/dunspotify"
lastSavedSongFile = join(cacheDir, "lastSavedSong.json")
currentSongFile = join(cacheDir, "currentSong.json")

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
        print("Creating dirs")
        makedirs(cacheDir)

    if not exists(lastSavedSongFile):
        with open(lastSavedSongFile, 'w') as last:
            last.write(jsonStructure)

    if not exists(currentSongFile):
        with open(currentSongFile, 'w') as current:
            current.write(jsonStructure)


def get_metadata():
    metadata = check_output(
        ["./spot_metadata"], universal_newlines=True)
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


def prepare_album_and_url():
    metadata = get_metadata()

    albumTitle = ''
    for line in metadata.split('\n'):
        if 'album' in line:
            albumTitle = line.split('|')[1].lower()
    removeChars = '[^ a-zA-Z0-9]'
    albumTitle = sub(removeChars, '', albumTitle)
    albumTitle = albumTitle.replace(' ', '_')


def download_album_cover():
    data = prepare_album_and_url()
    albumTitle = data.albumTitle
    coverUrl = data.coverUrl

    print(coverUrl, albumTitle)
    # urlretrieve(coverUrl, '')


def write_song_to_file():
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
    print("Comparing last saved song with current")
    with open(lastSavedSongFile, 'r') as last, open(currentSongFile, 'r') as current:

        # read both files
        dataLast = load(last)
        dataCurrent = load(current)
        if dataLast['coverUrl'] == dataCurrent['coverUrl']:
            # if album cover url matches, assume it's in the same album
            print("Still in the same album as last song")
            pass
        else:
            # if not, download the album cover
            print("Downloading album cover...")
            # TODO: download album cover
            pass


def main():
    # convert_metadata_json()
    # download_album_cover()
    # get_metadata()
    # compare_songs()
    write_song_to_file()


if __name__ == '__main__':
    main()
