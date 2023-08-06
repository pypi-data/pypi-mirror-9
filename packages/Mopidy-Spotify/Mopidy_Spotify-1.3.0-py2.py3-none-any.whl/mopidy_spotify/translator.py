from __future__ import unicode_literals

import logging
import re

from mopidy.models import Album, Artist, Playlist, Ref, Track

import spotify


logger = logging.getLogger(__name__)

artist_cache = {}
album_cache = {}
track_cache = {}

TRACK_AVAILABLE = 1


def parse_uri(uri):
    result = re.findall(r'^spotify:([a-z]+)(?::([\w:]+))?$', uri)
    if result:
        return result[0]
    return None, None


def to_mopidy_artist(spotify_artist):
    if spotify_artist is None:
        return
    uri = str(spotify.Link.from_artist(spotify_artist))
    if uri in artist_cache:
        return artist_cache[uri]
    if not spotify_artist.is_loaded():
        return Artist(uri=uri, name='[loading] %s' % uri)
    artist_cache[uri] = Artist(uri=uri, name=spotify_artist.name())
    return artist_cache[uri]


def to_mopidy_album(spotify_album):
    if spotify_album is None:
        return
    uri = str(spotify.Link.from_album(spotify_album))
    if uri in album_cache:
        return album_cache[uri]
    if not spotify_album.is_loaded():
        return Album(uri=uri, name='[loading] %s' % uri)
    album_cache[uri] = Album(
        uri=uri,
        name=spotify_album.name(),
        artists=[to_mopidy_artist(spotify_album.artist())],
        date=spotify_album.year())
    return album_cache[uri]


def to_mopidy_track_ref(spotify_track):
    uri = str(spotify.Link.from_track(spotify_track, 0))
    if not spotify_track.is_loaded():
        return Ref.track(uri=uri, name='[loading] %s' % uri)

    name = spotify_track.name()
    if spotify_track.availability() != TRACK_AVAILABLE:
        name = '[unplayable] %s' % name
    return Ref.track(uri=uri, name=name)


def to_mopidy_track(spotify_track, bitrate=None):
    if spotify_track is None:
        return
    uri = str(spotify.Link.from_track(spotify_track, 0))
    if uri in track_cache:
        return track_cache[uri]
    if not spotify_track.is_loaded():
        return Track(uri=uri, name='[loading] %s' % uri)
    name = spotify_track.name()
    if spotify_track.availability() != TRACK_AVAILABLE:
        name = '[unplayable] %s' % name
    spotify_album = spotify_track.album()
    if spotify_album is not None and spotify_album.is_loaded():
        date = spotify_album.year()
    else:
        date = None
    track_cache[uri] = Track(
        uri=uri,
        name=name,
        artists=[to_mopidy_artist(a) for a in spotify_track.artists()],
        album=to_mopidy_album(spotify_track.album()),
        track_no=spotify_track.index(),
        date=date,
        length=spotify_track.duration(),
        bitrate=bitrate)
    return track_cache[uri]


def to_mopidy_playlist(
        spotify_playlist, folders=None, bitrate=None, username=None):
    if spotify_playlist is None or spotify_playlist.type() != 'playlist':
        return
    try:
        uri = str(spotify.Link.from_playlist(spotify_playlist))
    except spotify.SpotifyError as e:
        logger.debug('Spotify playlist translation error: %s', e)
        return
    if not spotify_playlist.is_loaded():
        return Playlist(uri=uri, name='[loading] %s' % uri)
    name = spotify_playlist.name()
    if folders:
        folder_names = '/'.join(folder.name() for folder in folders)
        name = folder_names + '/' + name
    tracks = [
        to_mopidy_track(spotify_track, bitrate=bitrate)
        for spotify_track in spotify_playlist
        if not spotify_track.is_local()
    ]
    if not name:
        name = 'Starred'
        # Tracks in the Starred playlist are in reverse order from the official
        # client.
        tracks.reverse()
    if spotify_playlist.owner().canonical_name() != username:
        name += ' by ' + spotify_playlist.owner().canonical_name()
    return Playlist(uri=uri, name=name, tracks=tracks)
