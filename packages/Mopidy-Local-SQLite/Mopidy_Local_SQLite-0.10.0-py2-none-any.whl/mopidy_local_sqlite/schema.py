from __future__ import unicode_literals

import itertools
import logging
import operator
import os
import sqlite3

from mopidy.models import Album, Artist, Ref, Track

_BROWSE_QUERIES = {
    None: """
    SELECT CASE WHEN album.uri IS NULL THEN '%s' ELSE '%s' END AS type,
           coalesce(album.uri, track.uri) AS uri,
           coalesce(album.name, track.name) AS name
      FROM track LEFT OUTER JOIN album ON track.album = album.uri
     WHERE %%s
     GROUP BY coalesce(album.uri, track.uri)
     ORDER BY %%s
    """ % (Ref.TRACK, Ref.ALBUM),
    Ref.ALBUM: """
    SELECT '%s' AS type, uri AS uri, name AS name
      FROM album
     WHERE %%s
     ORDER BY %%s
    """ % Ref.ALBUM,
    Ref.ARTIST: """
    SELECT '%s' AS type, uri AS uri, name AS name
      FROM artist
     WHERE %%s
     ORDER BY %%s
    """ % Ref.ARTIST,
    Ref.TRACK: """
    SELECT '%s' AS type, uri AS uri, name AS name
      FROM track
     WHERE %%s
     ORDER BY %%s
    """ % Ref.TRACK
}

_BROWSE_FILTERS = {
    None: {
        'album': 'track.album = ?',
        'albumartist': 'album.artists = ?',
        'artist': 'track.artists = ?',
        'composer': 'track.composers = ?',
        'date': "track.date LIKE ? || '%'",
        'genre': 'track.genre = ?',
        'performer': 'track.performers = ?',
        'max-age': "track.last_modified >= (strftime('%s', 'now') - ?) * 1000",
    },
    Ref.ARTIST: {
        'role': {
            'albumartist': """EXISTS (
                SELECT * FROM album WHERE album.artists = artist.uri
            )""",
            'artist': """EXISTS (
                SELECT * FROM track WHERE track.artists = artist.uri
            )""",
            'composer': """EXISTS (
                SELECT * FROM track WHERE track.composers = artist.uri
            )""",
            'performer': """EXISTS (
                SELECT * FROM track WHERE track.performers = artist.uri
            )"""
        },
    },
    Ref.ALBUM: {
        'albumartist': 'artists = ?',
        'artist': """? IN (
            SELECT artists FROM track WHERE album = album.uri
        )""",
        'composer': """? IN (
            SELECT composers FROM track WHERE album = album.uri
        )""",
        'date': """EXISTS (
            SELECT * FROM track WHERE album = album.uri AND date LIKE ? || '%'
        )""",
        'genre': """? IN (
            SELECT genre FROM track WHERE album = album.uri
        )""",
        'performer': """? IN (
            SELECT performers FROM track WHERE album = album.uri
        )""",
        'max-age': """EXISTS (
            SELECT *
              FROM track
             WHERE album = album.uri
               AND last_modified >= (strftime('%s', 'now') - ?) * 1000
        )""",
    },
    Ref.TRACK: {
        'album': 'album = ?',
        'albumartist': """? IN (
            SELECT artists FROM album WHERE uri = track.album
        )""",
        'artist': 'artists = ?',
        'composer': 'composers = ?',
        'date': "date LIKE ? || '%'",
        'genre': 'genre = ?',
        'performer': 'performers = ?',
        'max-age': "last_modified >= (strftime('%s', 'now') - ?) * 1000",
    }
}

_LOOKUP_QUERIES = {
    Ref.ALBUM: """
    SELECT * FROM tracks WHERE album_uri = ?
    """,
    Ref.ARTIST: """
    SELECT * FROM tracks WHERE ? IN (artist_uri, albumartist_uri)
    """,
    Ref.TRACK: """
    SELECT * FROM tracks WHERE uri = ?
    """
}

_SEARCH_SQL = """
SELECT *
  FROM tracks
 WHERE docid IN (SELECT docid FROM %s WHERE %s)
"""

_SEARCH_FILTERS = {
    'album': 'album_uri = ?',
    'albumartist': 'albumartist_uri = ?',
    'artist': 'artist_uri = ?',
    'composer': 'composer_uri = ?',
    'date': "date LIKE ? || '%'",
    'genre': 'genre = ?',
    'performer': 'performer_uri = ?',
    'uri': 'uri GLOB ?',
    'max-age': "last_modified >= (strftime('%s', 'now') - ?) * 1000",
}

_SEARCH_FIELDS = {
    'uri',
    'track_name',
    'album',
    'artist',
    'composer',
    'performer',
    'albumartist',
    'genre',
    'track_no',
    'date',
    'comment'
}

schema_version = 5

logger = logging.getLogger(__name__)


class Connection(sqlite3.Connection):

    class Row(sqlite3.Row):

        def __getattr__(self, name):
            return self[name]

    def __init__(self, *args, **kwargs):
        sqlite3.Connection.__init__(self, *args, **kwargs)
        self.execute('PRAGMA foreign_keys = ON')
        self.row_factory = self.Row


def load(c):
    sql_dir = os.path.join(os.path.dirname(__file__), b'sql')
    user_version = c.execute('PRAGMA user_version').fetchone()[0]
    if not user_version:
        logger.info('Creating SQLite database schema v%s', schema_version)
        script = os.path.join(sql_dir, 'create-v%s.sql' % schema_version)
        c.executescript(open(script).read())
        user_version = c.execute('PRAGMA user_version').fetchone()[0]
    while user_version != schema_version:
        logger.info('Upgrading SQLite database schema v%s', user_version)
        script = os.path.join(sql_dir, 'upgrade-v%s.sql' % user_version)
        c.executescript(open(script).read())
        user_version = c.execute('PRAGMA user_version').fetchone()[0]
    return user_version


def tracks(c):
    return itertools.imap(_track, c.execute('SELECT * FROM tracks'))


def list_distinct(c, field, query=[]):
    if field not in _SEARCH_FIELDS:
        raise LookupError('Invalid search field: %s' % field)
    sql = """
    SELECT DISTINCT %s AS field
      FROM search
     WHERE field IS NOT NULL
    """ % field
    terms = []
    params = []
    for key, value in query:
        if key == 'any':
            terms.append('? IN (%s)' % ','.join(_SEARCH_FIELDS))
        elif key in _SEARCH_FIELDS:
            terms.append('%s = ?' % key)
        else:
            raise LookupError('Invalid search field: %s' % key)
        params.append(value)
    if terms:
        sql += ' AND ' + ' AND '.join(terms)
    logger.debug('SQLite list query %r: %s', params, sql)
    return itertools.imap(operator.itemgetter(0), c.execute(sql, params))


def dates(c, format='%Y-%m-%d'):
    return itertools.imap(operator.itemgetter(0), c.execute("""
    SELECT DISTINCT strftime(?, date) AS date
      FROM track
     WHERE date IS NOT NULL
     ORDER BY date
    """, [format]))


def lookup(c, type, uri):
    return itertools.imap(_track, c.execute(_LOOKUP_QUERIES[type], [uri]))


def exists(c, uri):
    rows = c.execute('SELECT EXISTS(SELECT * FROM track WHERE uri = ?)', [uri])
    return rows.fetchone()[0]


def browse(c, type=None, order=('type', 'name'), **kwargs):
    filters, params = _filters(_BROWSE_FILTERS[type], **kwargs)
    sql = _BROWSE_QUERIES[type] % (
        ' AND '.join(filters) or '1',
        ', '.join(order)
    )
    logger.debug('SQLite browse query %r: %s', params, sql)
    return [Ref(**row) for row in c.execute(sql, params)]


def search_tracks(c, query, limit, offset, exact, filters=[]):
    if not query:
        sql, params = ('SELECT * FROM tracks WHERE 1', [])
    elif exact:
        sql, params = _indexed_query(query)
    else:
        sql, params = _fulltext_query(query)
    clauses = []
    for kwargs in filters:
        f, p = _filters(_SEARCH_FILTERS, **kwargs)
        if f:
            clauses.append('(%s)' % ' AND '.join(f))
            params.extend(p)
        else:
            logger.debug('Skipped SQLite search filter %r', kwargs)
    if clauses:
        sql += ' AND (%s)' % ' OR '.join(clauses)
    sql += ' LIMIT ? OFFSET ?'
    params += [limit, offset]
    logger.debug('SQLite search query %r: %s', params, sql)
    rows = c.execute(sql, params)
    return map(_track, rows)


def insert_artists(c, artists):
    if not artists:
        return None
    if len(artists) != 1:
        logger.warn('Ignoring multiple artists: %r', artists)
    artist = next(iter(artists))
    _insert(c, 'artist', {
        'uri': artist.uri,
        'name': artist.name,
        'musicbrainz_id': artist.musicbrainz_id
    })
    return artist.uri


def insert_album(c, album):
    if not album or not album.name:
        return None
    _insert(c, 'album', {
        'uri': album.uri,
        'name': album.name,
        'artists': insert_artists(c, album.artists),
        'num_tracks': album.num_tracks,
        'num_discs': album.num_discs,
        'date': album.date,
        'musicbrainz_id': album.musicbrainz_id,
        'images': ' '.join(album.images) if album.images else None
    })
    return album.uri


def insert_track(c, track):
    _insert(c, 'track', {
        'uri': track.uri,
        'name': track.name,
        'album': insert_album(c, track.album),
        'artists': insert_artists(c, track.artists),
        'composers': insert_artists(c, track.composers),
        'performers': insert_artists(c, track.performers),
        'genre': track.genre,
        'track_no': track.track_no,
        'disc_no': track.disc_no,
        'date': track.date,
        'length': track.length,
        'bitrate': track.bitrate,
        'comment': track.comment,
        'musicbrainz_id': track.musicbrainz_id,
        'last_modified': track.last_modified
    })
    return track.uri


def delete_track(c, uri):
    c.execute('DELETE FROM track WHERE uri = ?', (uri,))


def count_tracks(c):
    return c.execute('SELECT count(*) FROM track').fetchone()[0]


def cleanup(c):
    c.execute("""
    DELETE FROM album WHERE NOT EXISTS (
        SELECT uri FROM track WHERE track.album = album.uri
    )
    """)
    c.execute("""
    DELETE FROM artist WHERE NOT EXISTS (
        SELECT uri FROM track WHERE track.artists = artist.uri
         UNION
        SELECT uri FROM track WHERE track.composers = artist.uri
         UNION
        SELECT uri FROM track WHERE track.performers = artist.uri
         UNION
        SELECT uri FROM album WHERE album.artists = artist.uri
    )
    """)
    c.execute('ANALYZE')


def clear(c):
    c.executescript("""
    DELETE FROM track;
    DELETE FROM album;
    DELETE FROM artist;
    VACUUM;
    """)


def _insert(c, table, params):
    sql = 'INSERT OR REPLACE INTO %s (%s) VALUES (%s)' % (
        table,
        ', '.join(params.keys()),
        ', '.join(['?'] * len(params))
    )
    logger.debug('SQLite insert statement: %s %r', sql, params.values())
    return c.execute(sql, params.values())


def _filters(mapping, role=None, **kwargs):
    filters, params = [], []
    if role and 'role' in mapping:
        rolemap = mapping['role']
        if isinstance(role, basestring):
            filters.append(rolemap[role])
        else:
            filters.append(' OR '.join(rolemap[r] for r in role))
    for key, value in kwargs.items():
        if key in mapping:
            filters.append(mapping[key])
            params.append(value)
        else:
            logger.debug('Skipped SQLite filter expression: %s=%r', key, value)
    return (filters, params)


def _indexed_query(query):
    terms = []
    params = []
    for field, value in query:
        if field == 'any':
            terms.append('? IN (%s)' % ','.join(_SEARCH_FIELDS))
        elif field in _SEARCH_FIELDS:
            terms.append('%s = ?' % field)
        else:
            raise LookupError('Invalid search field: %s' % field)
        params.append(value)
    return (_SEARCH_SQL % ('search', ' AND '.join(terms)), params)


def _fulltext_query(query):
    terms = []
    params = []
    for field, value in query:
        if field == 'any':
            terms.append(_SEARCH_SQL % ('fts', 'fts MATCH ?'))
        elif field in _SEARCH_FIELDS:
            terms.append(_SEARCH_SQL % ('fts', '%s MATCH ?' % field))
        else:
            raise LookupError('Invalid search field: %s' % field)
        params.append(value)
    return (' INTERSECT '.join(terms), params)


def _track(row):
    kwargs = {
        'uri': row.uri,
        'name': row.name,
        'genre': row.genre,
        'track_no': row.track_no,
        'disc_no': row.disc_no,
        'date': row.date,
        'length': row.length,
        'bitrate': row.bitrate,
        'comment': row.comment,
        'musicbrainz_id': row.musicbrainz_id,
        'last_modified': row.last_modified
    }
    if row.album_uri is not None:
        if row.albumartist_uri is not None:
            albumartists = [Artist(
                uri=row.albumartist_uri,
                name=row.albumartist_name,
                musicbrainz_id=row.albumartist_musicbrainz_id
            )]
        else:
            albumartists = None
        kwargs['album'] = Album(
            uri=row.album_uri,
            name=row.album_name,
            artists=albumartists,
            num_tracks=row.album_num_tracks,
            num_discs=row.album_num_discs,
            date=row.album_date,
            musicbrainz_id=row.album_musicbrainz_id,
            images=row.album_images.split() if row.album_images else None
        )
    if row.artist_uri is not None:
        kwargs['artists'] = [Artist(
            uri=row.artist_uri,
            name=row.artist_name,
            musicbrainz_id=row.artist_musicbrainz_id
        )]
    if row.composer_uri is not None:
        kwargs['composers'] = [Artist(
            uri=row.composer_uri,
            name=row.composer_name,
            musicbrainz_id=row.composer_musicbrainz_id
        )]
    if row.performer_uri is not None:
        kwargs['performers'] = [Artist(
            uri=row.performer_uri,
            name=row.performer_name,
            musicbrainz_id=row.performer_musicbrainz_id
        )]
    return Track(**kwargs)
