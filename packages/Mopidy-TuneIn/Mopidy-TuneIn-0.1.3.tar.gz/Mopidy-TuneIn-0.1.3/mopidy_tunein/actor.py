from __future__ import unicode_literals

import logging

from collections import deque

from mopidy import backend, exceptions
from mopidy.audio import scan
from mopidy.models import Ref, SearchResult

import pykka

from mopidy_tunein import translator, tunein

logger = logging.getLogger(__name__)


class TuneInBackend(pykka.ThreadingActor, backend.Backend):
    uri_schemes = ['tunein']

    def __init__(self, config, audio):
        super(TuneInBackend, self).__init__()
        self.tunein = tunein.TuneIn(config['tunein']['timeout'])
        self.library = TuneInLibrary(backend=self,
                                     timeout=config['tunein']['timeout'])
        self.playback = TuneInPlayback(audio=audio,
                                       backend=self,
                                       timeout=config['tunein']['timeout'])


class TuneInLibrary(backend.LibraryProvider):
    root_directory = Ref.directory(uri='tunein:root', name='TuneIn')

    def __init__(self, backend, timeout):
        super(TuneInLibrary, self).__init__(backend)
        self._scanner = scan.Scanner(min_duration=None, timeout=timeout)

    def browse(self, uri):
        result = []
        variant, identifier = translator.parse_uri(uri)
        logger.debug('Browsing %s' % uri)
        if variant == 'root':
            for category in self.backend.tunein.categories():
                result.append(translator.category_to_ref(category))
        elif variant == "category" and identifier:
            for section in self.backend.tunein.categories(identifier):
                result.append(translator.section_to_ref(section, identifier))
        elif variant == "location" and identifier:
            for location in self.backend.tunein.locations(identifier):
                result.append(translator.section_to_ref(location, 'local'))
            for station in self.backend.tunein.stations(identifier):
                result.append(translator.station_to_ref(station))
        elif variant == "section" and identifier:
            if (self.backend.tunein.related(identifier)):
                result.append(Ref.directory(
                    uri='tunein:related:%s' % identifier, name='Related'))
            if (self.backend.tunein.shows(identifier)):
                result.append(Ref.directory(
                    uri='tunein:shows:%s' % identifier, name='Shows'))
            for station in self.backend.tunein.featured(identifier):
                result.append(translator.section_to_ref(station))
            for station in self.backend.tunein.local(identifier):
                result.append(translator.station_to_ref(station))
            for station in self.backend.tunein.stations(identifier):
                result.append(translator.station_to_ref(station))
        elif variant == "related" and identifier:
            for section in self.backend.tunein.related(identifier):
                result.append(translator.section_to_ref(section))
        elif variant == "shows" and identifier:
            for show in self.backend.tunein.shows(identifier):
                result.append(translator.show_to_ref(show))
        elif variant == "episodes" and identifier:
            for episode in self.backend.tunein.episodes(identifier):
                result.append(translator.station_to_ref(episode))
        else:
            logger.debug('Unknown URI: %s', uri)

        return result

    def refresh(self, uri=None):
        self.backend.tunein.reload()

    def lookup(self, uri):
        variant, identifier = translator.parse_uri(uri)
        if variant != 'station':
            return []
        station = self.backend.tunein.station(identifier)
        if not station:
            return []

        track = translator.station_to_track(station)
        return [track]

    def find_exact(self, query=None, uris=None):
        return self.search(query=query, uris=uris)

    def search(self, query=None, uris=None):
        if query is None or not query:
            return
        tunein_query = translator.mopidy_to_tunein_query(query)
        tracks = []
        for station in self.backend.tunein.search(tunein_query):
            track = translator.station_to_track(station)
            tracks.append(track)
        return SearchResult(uri='tunein:search', tracks=tracks)


class TuneInPlayback(backend.PlaybackProvider):
    def __init__(self, audio, backend, timeout):
        super(TuneInPlayback, self).__init__(audio, backend)
        self._scanner = scan.Scanner(min_duration=None, timeout=timeout)

    def play(self, track):
        self.audio.prepare_change()
        return self.change_track(track) and self.audio.start_playback().get()

    def change_track(self, track):
        variant, identifier = translator.parse_uri(track.uri)
        station = self.backend.tunein.station(identifier)
        if not station:
            return False
        uris = deque(self.backend.tunein.tune(station, parse_url=False))
        while uris:
            uri = uris.popleft()
            logger.debug('Looking up URI: %s.' % uri)
            try:
                track = scan.audio_data_to_track(self._scanner.scan(uri))
                # TODO: Somehow update metadata using station.
                return super(TuneInPlayback, self).change_track(track)
            except exceptions.ScannerError as se:
                try:
                    logger.debug('Mopidy scan failed: %s.' % se)
                    next_uris = self.backend.tunein.parse_stream_url(uri)
                    if uri in next_uris:
                        raise tunein.PlaylistError('Recursive playlist')
                    next_uris.reverse()  # extendleft will reverse order.
                    uris.extendleft(next_uris)
                except tunein.PlaylistError as pe:
                    logger.debug('Tunein lookup failed: %s.' % pe)
                    break
        return False
