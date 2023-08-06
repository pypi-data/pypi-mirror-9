import cgi
import json
import requests
import re
from datetime import datetime

class HaloReachAPI():
    def __init__(self, token, api_url='http://www.bungie.net/api/reach/reachapijson.svc/'):
        self.token = token
        self.api_url = api_url

        self.HEADERS = { 'User-Agent': 'Halo:Reach API Python' }

    def set_http_headers(self, http_headers={}):
        self.HEADERS.update(http_headers)

    def fetch(self, uri):
        return requests.get(self.api_url + uri, headers=self.HEADERS)

    '''
    The "GetGameMetadata" method returns several dictionaries so that resource ids can be translated into their more detailed versions.
    For example, this method can be used to associate a medal resource id with its representative medal (say, a killing spree).

    http://www.haloreachapi.net/wiki/GetGameMetadata
    '''
    def get_game_metadata(self):
        game_metadata_uri = "game/metadata/%s" % self.token
        return self.fetch(game_metadata_uri)

    '''The "GetCurrentChallenges" method returns the currently active weekly and daily challenges.

    http://www.haloreachapi.net/wiki/GetCurrentChallenges
    '''
    def get_current_challenges(self):
        current_challenges_uri = "game/challenges/%s" % self.token
        return self.fetch(current_challenges_uri)

    '''
    The "GetGameDetails" method returns detailed information for a given game ID.

    http://www.haloreachapi.net/wiki/GetGameDetails
    '''
    def get_game_details(self, game_id):
        get_game_details_uri = "game/details/%s/%s" % (self.token, game_id)
        return self.fetch(get_game_details_uri)

    '''
    The "GetGameHistory" method returns a players list of games, in chronological reverse over. Returned games is paginated,
    and you can specific which game variant, (Invasion, Campaign, for example), or Unknown for all games.

    http://www.haloreachapi.net/wiki/GetGameHistory
    '''
    def get_game_history(self, gamertag, variant_class='Unknown', page=0):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_game_history_uri = "player/gamehistory/%s/%s/%s/%s" % (self.token, gamertag, variant_class, page)
        return self.fetch(get_game_history_uri)

    '''
    Undocumented

    http://www.haloreachapi.net/wiki/GetPlayerDetailsWithStatsByMap
    '''
    def get_player_details_with_stats_by_map(self, gamertag):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_player_details_with_stats_by_map_uri = "player/details/bymap/%s/%s" % (self.token, gamertag)
        return self.fetch(get_player_details_with_stats_by_map_uri)

    '''
    The "GetPlayerDetailsWithStatsByPlaylist" method Returns detailed aggregate information on a player, including arena information.

    http://www.haloreachapi.net/wiki/GetPlayerDetailsWithStatsByPlaylist
    '''
    def get_player_details_with_stats_by_playlist(self, gamertag):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_player_details_with_stats_by_playlist_uri = "player/details/byplaylist/%s/%s" % (self.token, gamertag)
        return self.fetch(get_player_details_with_stats_by_playlist_uri)

    '''
    The "GetPlayerDetailsWithNoStats" method returns basic information about a player.

    http://www.haloreachapi.net/wiki/GetPlayerDetailsWithNoStats
    '''
    def get_player_details_with_no_stats(self, gamertag):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_player_details_with_no_stats_uri = "player/details/nostats/%s/%s" % (self.token, gamertag)
        return self.fetch(get_player_details_with_no_stats_uri)

    '''
    The "GetPlayerFileShare" method returns a listing of files in a player's file share.

    http://www.haloreachapi.net/wiki/GetPlayerFileShare
    '''
    def get_player_file_share(self, gamertag):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_player_file_share_uri = "file/share/%s/%s" % (self.token, gamertag)
        return self.fetch(get_player_file_share_uri)

    '''
    The "GetFileDetails" method returns the file details for a single file.

    http://www.haloreachapi.net/wiki/GetFileDetails
    '''
    def get_file_details(self, file_id):
        get_file_details_uri = "file/details/%s/%s" % (self.token, file_id)
        return self.fetch(get_file_details_uri)

    '''
    The "GetPlayerRecentScreenshots" method returns a list of the player's recent screenshots.

    http://www.haloreachapi.net/wiki/GetPlayerRecentScreenshots
    '''
    def get_player_recent_screenshots(self, gamertag):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_player_recent_screenshots_uri = "file/screenshots/%s/%s" % (self.token, gamertag)
        return self.fetch(get_player_recent_screenshots_uri)

    '''
    The "GetPlayerFileSets" method returns a listing of file sets created by the player.

    http://www.haloreachapi.net/wiki/GetPlayerFileSets
    '''
    def get_player_file_sets(self, gamertag):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_player_file_sets_uri = "file/sets/%s/%s" % (self.token, gamertag)
        return self.fetch(get_player_file_sets_uri)

    '''
    The "GetPlayerFileSetFiles" method returns a listing of files in the specified file set.

    http://www.haloreachapi.net/wiki/GetPlayerFileSetFiles
    '''
    def get_player_file_set_files(self, gamertag, file_set_id):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_player_file_set_files_uri = "file/sets/files/%s/%s/%s" % (self.token, gamertag, file_set_id)
        return self.fetch(get_player_file_set_files_uri)

    '''
    The "GetPlayerRenderedVideos" method returns a listing of rendered videos created by a player.

    http://www.haloreachapi.net/wiki/GetPlayerRenderedVideos
    '''
    def get_player_rendered_videos(self, gamertag, page=0):
        gamertag = HaloReachAPI.msftize(gamertag)
        get_player_rendered_videos_uri = "file/videos/%s/%s/%s" % (self.token, gamertag, page)
        return self.fetch(get_player_rendered_videos_uri)

    '''
    The "ReachFileSearch" method returns a listing of files matching the specified criteria.

    http://www.haloreachapi.net/wiki/ReachFileSearch
    '''
    def reach_file_search(self, file_category, map_filter, engine_filter, date_filter, sort_filter, tags=None, page=0):
        reach_file_search_uri = "file/search/%s/%s/%s/%s/%s/%s/%s" % ( self.token,
                                                                       file_category,
                                                                       map_filter,
                                                                       engine_filter,
                                                                       date_filter,
                                                                       sort_filter,
                                                                       page )

        if tags:
            reach_file_search_uri = '%s?tags=%s' % (reach_file_search_uri, cgi.escape(tags))

        return self.fetch(reach_file_search_uri)

    # MSFT servers are not able to parse the '+' if doing a straight CGI.escape
    @staticmethod
    def msftize(gamertag):
        return gamertag.replace(' ', '%20')

    @staticmethod
    def parse_timestamp(timestamp=None):
        try:
            match = re.match('^\/Date\((\d+)-(\d+)\)\/$', timestamp)
            utc_timestamp = float(match.group(1)) / 1000

            return datetime.utcfromtimestamp(utc_timestamp)
        except:
            raise Exception('Invalid Timestamp')
