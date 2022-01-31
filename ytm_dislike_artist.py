#!/usr/bin/env python3

# This requires ytmusicapi.  See https://ytmusicapi.readthedocs.io/en/latest/setup.html for setup instructions

import argparse
import os
from time import sleep

from ytmusicapi import YTMusic


def get_artist(client, artist_name):
    """Get the artist object for the supplied artist's name."""
    return client.get_artist(
        client.search(query=artist_name, filter="artists", ignore_spelling=True)[0][
            "browseId"
        ]
    )


def dislike_tracks(client, tracks, dry_run):
    """Dislike each of these tracks/songs"""
    for t in tracks:
        print(t["title"])
        client.rate_song(
            videoId=t["videoId"], rating="DISLIKE"
        ) if not dry_run else None
        sleep(1)


def dislike_album_songs(client, albums, dry_run):
    """Dislike all tracks from all albums in this list"""
    for a in albums:
        album = client.get_album(a["browseId"])
        print("\nAlbum Title: ", album["title"])
        dislike_tracks(client, album["tracks"], dry_run)


def dislike_all_songs(client, artist, dry_run=False):
    """Lookup all albums and singles by this artist and dislike them"""
    if "albums" in artist:
        if artist["albums"]["browseId"] is None:
            print("Returned %d albums." % len(artist["albums"]["results"]))
            albums = artist["albums"]["results"]
        else:
            albums = client.get_artist_albums(
                channelId=artist["channelId"], params=artist["albums"]["params"]
            )
            print("Returned %d albums." % len(albums))
        dislike_album_songs(client, albums, dry_run)
    if "singles" in artist:
        if artist["singles"]["browseId"] is None:
            print("Returned %d singles." % len(artist["singles"]["results"]))
            singles = artist["singles"]["results"]
        else:
            singles = client.get_artist_albums(
                channelId=artist["channelId"], params=artist["singles"]["params"]
            )
            print("Returned %d singles." % len(singles))
        dislike_album_songs(client, singles, dry_run)


def main():
    my_parser = argparse.ArgumentParser(
        description="Dislike all songs from an Artist on YouTube Music"
    )
    my_parser.add_argument("--dry-run", action="store_true")
    my_parser.add_argument(
        "--artist", action="store", type=str, required=True, help="name of the artist"
    )
    my_parser.add_argument(
        "--auth",
        action="store",
        type=str,
        default=os.path.expanduser("~/.config/ytm_headers_auth.json"),
        help="path to the headers_auth.json file.",
    )

    args = my_parser.parse_args()
    artist_name = args.artist

    try:
        ytmusic = YTMusic(args.auth)
    except:
        print(
            "You need to create a headers_auth.json, see  https://ytmusicapi.readthedocs.io/en/latest/setup.html"
        )
    else:
        artist = get_artist(ytmusic, artist_name)
        print("Artist Name: ", artist["name"])
        print("Artist Description: ", artist["description"])
        print("Top songs:")
        for song in artist["songs"]["results"]:
            print(song["title"])

        do_it = input("Do you want to dislike all songs by this artist? (y|n) ")
        if "y" in do_it.lower():
            print("About to dislike everything by %s ..." % artist["name"], end=" ")
            for i in reversed(range(4)):
                print(i, sep=".", end=" ", flush=True)
                sleep(1)
            print()
            dislike_all_songs(ytmusic, artist, args.dry_run)
        else:
            print("OK.  Exiting.")


if __name__ == "__main__":
    main()
