#!/usr/bin/env python

"""seedme.py: Uploads, downloads and queries content at SeedMe.org.
This module provides command line interface as well as methods and api
for programmatic usage. It performs extensive sanity checks input data
and is kept upto date with REST api at SeedMe.org.

Visit https://bitbucket.org/seedme/seedme-python-client/overview
or see README.md file for usage information
"""
__author__ = "Amit Chourasia"
__status__ = "Production"
__version__ = "0.9.8"
#__credits__ = [] # bug reporters, suggestion makers

from datetime import datetime
from fnmatch import fnmatch
import glob
#from glob import glob
import logging
import os
#from os import access, environ, path
import subprocess
#from subprocess import PIPE, Popen
import sys
from time import sleep


try:
    from collections import OrderedDict
except ImportError: # use backport for python 2.6
    try: # look for installed version
        from ordereddict import OrderedDict
    except ImportError:
        try: # use the one shipped with simplejson
            from thirdparty.simplejson.ordered_dict import OrderedDict
        except ImportError:
            print('No module named ordered_dict, one of these will work')
            print('1: Install simplejson module')
            print('2: Use Python 2.7.x +')
            print('3: Use self contained SeedMe module from here ' +\
            'https://bitbucket.org/seedme/seedme-python-client/get/master.zip')
            sys.exit(1) #bail


try:
    import json
except ImportError: # use backport for python 2.6
    try: # look for installed version
        import simplejson as json
    except ImportError:
        try: # use our shipped version
            import thirdparty.simplejson as json
        except ImportError:
            print('No module named simplejson, one of the following will work')
            print('1: Install simplejson module')
            print('2: Use Python 2.7.x +')
            print('3: Use self contained SeedMe module from here ' +\
            'https://bitbucket.org/seedme/seedme-python-client/get/master.zip')
            sys.exit(1) #bail


try:
    import requests
except ImportError:
    try: # use our shipped version
        import thirdparty.requests as requests
    except ImportError:
        print('No module named requests, one of the following will work')
        print('1: Install requests as instructed here ' +\
              'http://docs.python-requests.org/en/latest/user/install')
        print('2: Use self contained SeedMe module from here ' +\
            'https://bitbucket.org/seedme/seedme-python-client/get/master.zip')
        sys.exit(1) #bail


# Following setting is needed for pyinstaller exe to work
# https://github.com/kennethreitz/requests/issues/557
if getattr(sys, '_MEIPASS', '.') != '.':
    def _resource_path(relative):
        """returns path for the exe dir"""
        return os.path.join(getattr(sys, '_MEIPASS', os.path.abspath(".")),
                            relative)
    cert_path = _resource_path('cacert.pem') #cacert.pem is copied to lib/
    os.environ['REQUESTS_CA_BUNDLE'] = os.path.join(os.getcwd(), cert_path)

###############################################################################
# Set up logging
###############################################################################
# Adds null handler to support python 2.6
class _NullHandler(logging.Handler):
    """Adds null handler to support python 2.6"""
    def emit(self, record):
        pass

# Add private class to restrict info logs to stdout
class _InfoFilter(logging.Filter):
    """Sets up filtering for stdout log handler"""
    def filter(self, rec):
        return rec.levelno in (logging.DEBUG, logging.INFO)

# Create a top-level logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
# add null handler as a back up when no handlers are set
#null_handler = logging.NullHandler() python 2.7 onwards
null_handler = _NullHandler() # python 2.6 compatibility
log.addHandler(null_handler)


###############################################################################
# SeedMe class implements methods for using webservices
###############################################################################
class SeedMe(object):
    """SeedMe class implements methods for using webservices"""
    def __init__(self):
        """Initializes state for SeedMe object"""
        self.base_url = 'https://www.seedme.org/services/1.0/collection'
        self.service_version = '1.0'
        self.url = ''
        self.username = ''
        self.apikey = ''
        self.session = None

        self.curl_commands = False
        self.curl_commands_auth = False
        self.curl_path = ''
        self.dry_run = False
        self.post_method = ''
        self.requests_loaded = True
        self.cacert_path = None
        self.ssl = True

        # overwrite existing files
        self.overwrite = {'all_types': False,
                          'files': False,
                          'plots': False,
                          'sequences': False,
                          'videos': False,
                         }

        self.f_log = False #file log
        self.f_hand = None #log file handler
        self.c_log = False #console log
        self.c_hand_err = None #console stderr handler
        self.c_hand_out = None #console stdout handler
        self.set_console_log(True) # turn on console log

        @property
        def curl_commands(self):
            """gets show curl commands mode"""
            return self._curl_commands

        @curl_commands.setter
        def curl_commands(self, value):
            """sets show curl commands mode"""
            if not isinstance(value, bool):
                raise TypeError('curl_commands must be True or False')
            else:
                self._curl_commands = value

        @property
        def dry_run(self):
            """gets dry run mode"""
            return self._dry_run

        @dry_run.setter
        def dry_run(self, value):
            """sets dry run mode"""
            if not isinstance(value, bool):
                raise TypeError('dry_run must be True or False')
            else:
                self._dry_run = value

        @property
        def post_method(self):
            """gets post method"""
            return self._post_method

        @post_method.setter
        def post_method(self, value):
            """sets post method"""
            if value != 'requests' or value != 'curl':
                raise TypeError('post_method must be "requests" or "curl"')
            else:
                self._post_method = value

    def __del__(self):
        """Delete SeedMe object"""
        log.debug("Deleting SeedMe Object")
        log.debug(self)
        log.handlers = [] #toss logging object





    ###########################################################################
    # Returns int for (success OR partial) or none
    # Wraps extract_cid global function
    # DEPRECATED use get_id(result) method
    ###########################################################################
    def extract_cid(self, result):
        """DEPRECATED use get_id(result) method
        Returns int for (success OR partial) or none
        Wraps extract_cid global function
        Parameters
        ----------
        result : string in JSON format
        """
        return extract_cid(result)


    ###########################################################################
    # Returns success, partial, failure or None
    # Wraps extract_status global function
    # DEPRECATED use get_status(result) method
    ###########################################################################
    def extract_status(self, result):
        """DEPRECATED use get_status(result) method
        Returns success, partial, failure or None
        Wraps extract_status global function
        Parameters
        ----------
        result : string in JSON format
        """
        return extract_status(result)


    ###########################################################################
    # Returns int for (success OR partial) or none
    # Wraps get_id global function
    ###########################################################################
    def get_id(self, result):
        """Returns int for (success OR partial) or none
        Wraps get_id global function
        Parameters
        ----------
        result : string in JSON format
        """
        return get_id(result)


    ###########################################################################
    # Returns message found in result
    # Wraps get_message global function
    ###########################################################################
    def get_message(self, result):
        """Returns string message or None
        Wraps get_message global function
        Parameters
        ----------
        result : string in JSON format
        """
        return get_message(result)


    ###########################################################################
    # Returns success, partial, failure or None
    # Wraps get_status global function
    ###########################################################################
    def get_status(self, result):
        """Returns success, partial, failure or None
        Wraps get_status global function
        Parameters
        ----------
        result : string in JSON format
        """
        return get_status(result)


    ###########################################################################
    # Returns string (url to the collection)
    # Wraps get_url global function
    ###########################################################################
    def get_url(self, result):
        """Returns string (url to the collection)
        Wraps get_url global function
        Parameters
        ----------
        result : string in JSON format
        """
        return get_url(result)

    ###########################################################################
    # Sets authorization with a file containing username:apikey
    # Use this method when using this module via script
    ###########################################################################
    def set_auth_via_file(self, my_auth_file_path):
        """Sets authorization with a file containing username:apikey
        Use this method when using this module via script
        Parameters
        ----------
        my_auth_file_path : JSON file
                            Absolute path to file containing the following
                            {"username":"YourUserName", "apikey":"YourApiKey"}
        """
        abs_path = os.path.normpath(os.path.expanduser(my_auth_file_path))
        try:
            with open(abs_path) as auth_file:
                auth = json.loads(auth_file.read())
                if 'username' in auth and 'apikey' in auth:
                    self.username = auth['username']
                    self.apikey = auth['apikey']
                else:
                    message = 'Invalid authorization file at ' +\
                              str(abs_path) +\
                              "\nThis file must contain the following" +\
                              '\n{"username" : "YourUserName", ' +\
                              '"apikey" : "YourApiKey"}' +\
                        "\nDownload this file from https://www.seedme.org/user"
                    log.error(message)
                    if not self.dry_run:
                        sys.exit(1) #bail

        except IOError:
            if abs_path != '.':
                message = 'Authorization file not found or could not' +\
                          ' be read at ' + str(abs_path)
            else:
                auth1 = os.path.normpath(os.path.expanduser('~/.seedme'))
                auth2 = os.path.normpath(os.path.expanduser('~/seedme.txt'))
                message = 'Authorization file not found at ' +\
                           auth1 + ' or ' + auth2

            message += "\nThis file should contain the following" +\
                       '\n{"username" : "YourUserName", ' +\
                       '"apikey" : "YourApiKey"}'
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail


    ###########################################################################
    # Sets authorization with username and apikey
    ###########################################################################
    def set_auth_via_string(self, my_username, my_apikey):
        """Sets authorization with username and apikey
        Parameters
        ----------
        my_username : str
                      Your username for SeedMe.org

        my_apikey   : str
                     Your apikey for SeedMe.org
        """
        if not my_username:
            message = ''
            if __name__ == '__main__':
                message = "Authorization username not set, include " +\
                          "following option." +\
                          "\n\t-u YourUserName"
            else:
                message = "Authorization username not set in following " +\
                          "method call." +\
                          "\n\tset_auth_via_string(username, apikey)"

            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        elif not my_apikey:
            if __name__ == '__main__':
                message = "Authorization apikey not set, include " +\
                          "following option." +\
                          "\n\t-a YourApiKey"
            else:
                message = "Authorization apikey not set in following " +\
                          "method call." +\
                          "\n\tset_auth_via_string(username, apikey)"

            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail

        else:
            self.username = my_username
            self.apikey = my_apikey


    ###########################################################################
    # Sets logging level
    ###########################################################################
    def set_log_level(self, level):
        """Sets logging level
        Parameters
        ----------
        level : DEBUG, INFO, WARNING, ERROR, CRITICAL
        """
        if level == 'DEBUG':
            log.setLevel(logging.DEBUG)
        elif level == 'INFO':
            log.setLevel(logging.INFO)
        elif level == 'WARNING':
            log.setLevel(logging.WARNING)
        elif level == 'ERROR':
            log.setLevel(logging.ERROR)
        elif level == 'CRITICAL':
            log.setLevel(logging.CRITICAL)


    ###########################################################################
    # Sets console log
    ###########################################################################
    def set_console_log(self, state):
        """Sets console log state.
        Note: console output is ON by default
        Parameters
        ----------
        state : bool
                True or False
        """
        if not isinstance(state, bool):
            raise TypeError('set_console_log(state): ' +\
                            '"state" argument must be True or False')
        # console log is ON by default, turn it OFF when requested
        if state == True:
            # Set log message format
            err_format = logging.Formatter("%(levelname)s : " +\
                                           "%(message)s %(asctime)s ")
            out_format = logging.Formatter("%(message)s")
            if not self.c_hand_err: # add stderr if not present
                self.c_hand_err = logging.StreamHandler(sys.stderr)
                self.c_hand_err.setLevel(logging.WARNING)
                self.c_hand_err.setFormatter(err_format)
                log.addHandler(self.c_hand_err)
            if not self.c_hand_out: # add stdout if not present
                self.c_hand_out = logging.StreamHandler(sys.stdout)
                self.c_hand_out.setLevel(logging.DEBUG)
                self.c_hand_out.addFilter(_InfoFilter())
                self.c_hand_out.setFormatter(out_format)
                log.addHandler(self.c_hand_out)
            self.c_log = True
        else:
            if self.c_hand_err: # toss handler if it exists
                log.removeHandler(self.c_hand_err)
            if self.c_hand_out: # toss handler if it exists
                log.removeHandler(self.c_hand_out)
            self.c_hand_err = None
            self.c_hand_out = None
            self.c_log = False


    ###########################################################################
    # Sets file log state and filepath
    ###########################################################################
    def set_file_log(self, state, filepath=None):
        """Sets file log state and filepath
        Parameters
        ----------
        state    : bool
                   True or False
        filepath : str
                   filepath to log file
        """
        if not isinstance(state, bool):
            raise TypeError('set_file_log(state, filepath="/tmp/xyz.log"):' +\
                            '"state" argument must be True or False')

        if state == True:
            if filepath:
                # Set log message format
                err_format = logging.Formatter("%(levelname)s : " +\
                                               "%(asctime)s %(message)s ")
                if self.f_hand: # toss existing handler
                    log.removeHandler(self.f_hand)
                    log.removeHandler(self.f_hand)
                self.f_hand = logging.FileHandler(filepath)
                self.f_hand.setFormatter(err_format)
                log.addHandler(self.f_hand)
                self.f_log = True
            else:
                log.error('Log file not set')
                sys.exit(1) #bail
        else:
            if self.f_hand: # toss handler if it exists
                log.removeHandler(self.f_hand)
                log.removeHandler(self.f_hand)
            self.f_hand = None
            self.f_log = False


    ###########################################################################
    # Sets base URL for web services
    # DO NOT use this method unless you know the internals
    ###########################################################################
    def set_base_url(self, custom_url):
        """Overide and set base URL for web services
        Useful only for interacting with older versions of webservices API
        Parameters
        ----------
        custom_url : str
                     Web Services URL for SeedMe.org
        """
        if self._url_sanity_(my_url=custom_url):
            self.base_url = custom_url


    ###########################################################################
    # Set curl path
    ###########################################################################
    def set_curl_path(self, my_path):
        """Sets curl path
        Parameters
        ----------
        my_path : str
                  Absolute path to curl executible
        """
        if _which_(my_path):
            self.curl_path = str(my_path)
            log.info('curl path is set to: ' + str(my_path))
        else:
            log.error("curl not found at path: " + str(my_path))


    ###########################################################################
    # Sets Dry Run
    ###########################################################################
    def set_dry_run(self):
        """Performs sanity checks on all inputs locally,
        except authorization which requires server side communication
        """
        self.dry_run = True
        log.info("Dry Run: All input validated" +\
                " without communication with server")

    ###########################################################################
    # Sets Overwrite Mode
    ###########################################################################
    def set_overwrite(self, all_types=False, files=False, plots=False,
                      sequences=False, videos=False):
        """Sets overwrite mode for all, file, plot, sequence, video
        Parameters
        ----------
        all_types : bool
                   Global overwrite for all content types
        files     : bool
                   Overwrite file if it exist
        plots     : bool
                   Overwrite plot if it exist
        seqeunces : bool
                   Overwrite sequence file if it exist
        videos    : bool
                   Overwrite video file if it exist
        """
        if all_types:
            if isinstance(all_types, bool):
                self.overwrite['all_types'] = True
                log.info("Overwrite set for all content types")
            else:
                log.warning('Invalid parameter in set_overwrite method:' +
                            '\'all_types\' parameter must be bool')

        if files and not self.overwrite['all_types']:
            if isinstance(files, bool):
                self.overwrite['files'] = True
                log.info("Overwrite set for all : files")
            else:
                log.warning('Invalid parameter in set_overwrite method:' +
                            '\'files\' parameter must be bool')

        if plots and not self.overwrite['all_types']:
            if isinstance(plots, bool):
                self.overwrite['plots'] = True
                log.info("Overwrite set for all : plots")
            else:
                log.warning('Invalid parameter in set_overwrite method:' +
                            '\'plots\' parameter must be bool')

        if sequences and not self.overwrite['all_types']:
            if isinstance(sequences, bool):
                self.overwrite['sequences'] = True
                log.info("Overwrite set for all : sequences")
            else:
                log.warning('Invalid parameter in set_overwrite method:' +
                            '\'sequences\' parameter must be bool')

        if videos and not self.overwrite['all_types']:
            if isinstance(videos, bool):
                self.overwrite['videos'] = True
                log.info("Overwrite set for all : videos")
            else:
                log.warning('Invalid parameter in set_overwrite method:' +
                            '\'videos\' parameter must be bool')

    ###########################################################################
    # Sets POST method
    ###########################################################################
    def set_post_method(self, my_post_method):
        """Sets POST method
        Parameters
        ----------
        my_post_method : str
                         Valid options 'requests' or 'curl'
        """
        if my_post_method == 'requests' and (not self.requests_loaded):
            message = 'requests module not found, try using curl'
            log.error(message)
            sys.exit(1) #bail

        self.post_method = my_post_method
        log.info('POST method is set to: ' + str(my_post_method))


    ###########################################################################
    # Sets path to SSL certificate file to be used for secure communication.
    # This is only needed in special cases when
    #    * default certifcate cacert.pem is not found in default system path
    #    * default cacert.pem certifacate does not work in firewalled zones
    #    * REQUESTS_CA_BUNDLE environment variable to cert path is not set
    ###########################################################################
    def set_ssl_cert(self, path):
        """Sets path to SSL certificate file to be used for secure communication
           This is only needed in special cases when
           * default certifcate cacert.pem is not found in default system path
           * default cacert.pem certifacate does not work in firewalled zones
           * REQUESTS_CA_BUNDLE environment variable to cert path is not set
        Parameters
        ----------
        path : string (path to file)
        """
        if (not path) or (not os.path.isfile(path)):
            message = "Invalid certifcate path or file could not be read. '" +\
                      path + "'"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        else:
            self.cacert_path = path


    ###########################################################################
    # Sets SSL on or off
    ###########################################################################
    def set_ssl(self, state=True):
        """Sets SSL on of off
        This must be never turned off. If done please reset your APIKEY ASAP
        Parameters
        ----------
        state : boolean
        """
        if state: # SSL is on by default
            pass
        else:
            message = "Security Hazard: SSL has been turned off.\n" +\
                      "Please reset your APIKEY ASAP to mitigate potential " +\
                      "compromise of your account."
            log.warning(message)
            self.ssl = state


    ###########################################################################
    # Sets POST method to curl and shows curl command line options
    ###########################################################################
    def show_curl_commands(self):
        """Sets POST method to curl and shows curl command line options"""
        self.curl_commands = True
        self.set_post_method('curl') # set post method to curl


    ###########################################################################
    # Sets POST method to curl and shows curl command line options with Auth
    ###########################################################################
    def show_auth_in_curl_commands(self):
        """Sets POST method to curl and shows curl command line options"""
        self.curl_commands_auth = True
        self.set_post_method('curl') # set post method to curl


    ###########################################################################
    # Shows web api version and web service url
    ###########################################################################
    def version(self):
        """Shows web api version and web service url"""
        log.info('Module Version: ' + __version__)
        log.info('Web API Version: ' + self.service_version)
        log.info('Web Service URL: ' + self.base_url)
        sys.exit(1) #bail


    ##########################################################################
    # Download items
    ##########################################################################
    def download(self,
                 cid=None, #int
                 content=None, #str: one of 'all' or 'video' or wildcard
                 path=None, #path to save the files, (default: ~/Downloads)
                 retry=3, #int, number of retry < 10
                 interval=60, #int, number of seconds between retry > 30 sec
                 overwrite=False, #boolean, overwrite existing local file
                ):
        """Download items

        Parameters
        ----------
        cid             : int, required
                          Collection ID for download

        content         : Which content to download
                          Choice of one of the following, required
                          'all'or 'video' or string with or without wildcard
                          'all' : download all files in collection
                          'video': download only videos in collection
                          wildcard: download any files that match given string

        path            : str, optional
                          Path for downloading content
                          Default: ~/Downloads or HOME/Downloads

        retry           : int, optional
                          number of times to retry attempts for downloading

        interval        : int, optional
                          number of seconds between retry > 30
                          Default: 60

        overwrite       : bool, optional
                          Overwrite local existing files
        """
        retry = int(retry)
        interval = int(interval)

        if not path: # set default download path
            path = os.path.normpath(os.path.expanduser('~/Downloads'))
            if not os.path.isdir(path):
                message = 'Could not find download path at :  ' + path
                message += '\nPlease set a valid path for downloads'
                log.error(message)
                if not self.dry_run:
                    sys.exit(1) #bail
        else: # normalize path
            path = os.path.normpath(os.path.expanduser(path))
            if not os.path.isdir(path):
                message = 'Invalid download path provided :  ' + path
                message += '\nPlease set a valid path for downloads'
                log.error(message)
                if not self.dry_run:
                    sys.exit(1) #bail

        if retry > 10: # clamp max retires to 10
            log.warning('Retry maximum must be <= 10. Defaulting to 10')
            retry = 10
        elif retry < 1:
            log.warning('Retry minimum must be >= 1. Clamping to 1')
            retry = 1

        if interval < 30: # clamp interval minimum to 30 sec
            log.warning('Interval must be > 30. Defaulting to 30 seconds')
            interval = 30

        for i in range(retry):
            # Wait and retry second time onwards
            if i > 0:
                log.info('Note: Video encoding from sequence ' +\
                         'could take several minutes to complete.')
                log.info('Retry ' + str(i+1)  + ' of ' + str(retry))
                # Wait for some interval seconds before retry
                for remaining in range(interval, 0, -1):
                    sys.stdout.write("\r")
                    sys.stdout.write("{0:2d} seconds remaining".format(remaining))
                    sys.stdout.flush()
                    sleep(1)

                sys.stdout.write("\r\n")

            # Trim log level for querying purpose
            user_level = log.getEffectiveLevel()
            if user_level < 30: # If more verbose than WARNING level
                log.setLevel('WARNING')

            # Query to get list of urls in collection
            result = self.query(cid, content='url')

            try:
                json_object = json.loads(result)
            except ValueError:
                log.error('JSON decode failed for result:' + str(result))
                sys.exit(1) #bail

            # Set log level back to what they were
            log.setLevel(user_level)

            # Check error and bail for non public collection
            if 'error' in json_object:
                message = json_object['error']
                log.error(message)
                if not self.dry_run:
                    sys.exit(1) #bail

            # Create list of files to be downloaded
            download_items = dict()
            for k, v in list(json_object.items()):

                if content == 'all' and 'http' in v and not 'collection_url' in k:
                    download_items[k] = v
                elif content == 'video':
                    video_ext = ['m4v', 'mpg', 'mpeg', 'mp4', 'mov', 'webm']
                    for suffix in video_ext:
                        if k.endswith(suffix): # add to download list
                            download_items[k] = v
                else: # wildcard
                    if fnmatch(k, content):
                        download_items[k] = v

            # set dummay names for dryrun
            if self.dry_run:
                download_items['dummy.txt'] = 'http://www.seedme.org/junk.txt'

            if download_items:
                i = 1
                l = len(download_items)
                for filename, url in list(download_items.items()):

                    # rename output filename if it exists
                    name, ext = os.path.splitext(filename)
                    j = 0
                    while os.path.isfile(path + '/' + filename) and not overwrite:
                        j += 1
                        filename = name + '_' + str(j) + ext

                    if j > 0: # file has been renamed
                        log.info('File exists: ' + name + ext)
                        log.info('Renaming output: ' + filename)

                    # file will be overwritten
                    if overwrite and os.path.isfile(path + '/' + filename):
                        log.info('Overwriting existing file')

                    n = str(i) + ' of ' + str(l) + ' : '
                    log.info('Downloading ' + n + filename + ' to ' + path)
                    self._do_download_(url, filename, path)
                    i += 1

                log.info('NOTICE: Download of sequence files is not ' +
                         'supported at present (Under development).')
                break # done with download

            if content == 'all':
                log.info('Could not find any files at ID ' +
                         str(cid) + ' to download')
            elif content == 'video':
                log.info('Could not find any video files at ID ' +
                         str(cid) + ' to download')
            else:
                log.info('Could not find any files matching "' + content +
                         '" pattern at ID ' + str(cid) + ' to download')
            log.info('NOTICE: Download of sequence files is not ' +
                     'supported at present (Under development).')




    ##########################################################################
    # Queries and retrieves content from user's collections
    ##########################################################################
    def query(self,
              qid=None, #int
              keyvalues=None, #string or dict
              content=None, #str: one of 'all'|'keyvalue'|'ticker'|'url'
              tail=None, #int, requires content
             ):
        """Queries and retrieves content from user's collections
        Returns JSON array

        *********************
        Query All Collections
        *********************
        query(): Returns list of users collection
        query(keyvalues="ssid:1234"): Returns list of all collection that match
                                      all specified key values
        ************************
        Query Single Collections
        ************************
        query(qid=666, list='all'): Returns all content for collection ID 666
        query(qid=666, list='tic'): Returns all tickers for collection ID 666
        query(qid=666, list='tic', tail=5): Returns last 5 tickers for ID 555


        Parameters
        ----------
        qid             : bool OR int, required
                          Collection ID to query

        keyvalues       : colon delimited string or dict, optional
                          Key Value pairs to search in all user's collection
                          when multiple key values are specified they are used
                          with AND condition. The function returns a list of
                          collections that match all specified key values.
                          Note: This option must be used without other arguments

        content    : str, optional (Requires qid set as colleciton ID)
                          Choice of one of the following
                          ['all', 'keyvalue', 'kv', 'tic', 'ticker', 'url']
                          Default: all
                          Note: this option can only be used with qid

        tail            : int, optional (Requires content option)
                          Last n items to list.
                          Note: this option can only be used in conjunction with
                          content as kv OR tic OR url
        """

        # ordered dictionary to collect query info
        q_data = OrderedDict()

        # check default path if authorization was not set
        if not self.username or not self.apikey:
            self._auth_default_check_()

        q_data['username'] = self.username
        q_data['apikey'] = self.apikey

        # attempt to convert specified qid to int
        if qid:
            try:
                qid = int(qid)
            except ValueError:
                log.error('Error: ID must be an integer.' +\
                          'You specified:' + str(qid))
                sys.exit(1) #bail


        # Change url when querying a specified collection
        if isinstance(qid, int) and not isinstance(qid, bool):
            self.url = self.base_url + '/' + str(qid)

            # content requested for listing
            if content:
                # expand short cuts
                if content == 'kv':
                    content = 'keyvalue'

                if content == 'tic':
                    content = 'ticker'

                if content in ['all', 'keyvalue', 'ticker', 'url']:
                    q_data['list'] = content
                else:
                    log.error("content must be one of " +\
                              "'all', 'keyvalue', 'ticker', 'url'")
                    sys.exit(1) #bail
            else: # add list all as default
                q_data['list'] = 'all'



        else: # query all collections
            #set url for querying
            self.url = self.base_url

            # bail if content set
            if content:
                log.error('Error: list "' + content +\
                          '" requires collection ID to be set.')
                sys.exit(1) #bail

            if keyvalues:
                #for k, v in list(keyvalues.items()):
                #    q_data['keyvalue'] = str(k) + ":" + str(v)
                if isinstance(keyvalues, str):
                    if len(keyvalues.split(':')) >= 2:
                        q_data['keyvalue'] = keyvalues
                    else:
                        log.warning('Skipping keyvalue: string should be colon' +\
                               'delimited as key:value, you specified' + keyvalues)
                else:
                    # query does not use array syntax and requires repeated use
                    # of same keyword as key for multiple items
                    # this is not possible with dict as it requires uniques
                    # keys for all items
                    # We can accomplish this via a string buffer as follows

                    kv_buffer = ''
                    i = 1
                    for key, value in list(keyvalues.items()): #py3 comp
                        # For first item do not add 'keyvalue' as it needs
                        # to be added when we insert kv_buffer to q_data
                        if i == 1:
                            kv_buffer += str(key) + ":" + str(value)
                        else: # prefix all items with '&keyvalue='
                            kv_buffer += '&keyvalue=' + str(key) + ":" + str(value)
                        i += 1

                    #now add all our key value pairs to query dict as one item
                    q_data['keyvalue'] = kv_buffer


        # tail items
        if tail:
            q_data['tail'] = tail

        return self._do_query_(q_data)

    ##########################################################################
    # Create a new collection
    ##########################################################################
    def create_collection(self,
                          privacy='',
                          sharing='',
                          notify='',
                          title='',
                          description='',
                          credits='',
                          license='',
                          overwrite=None, # bool or dict
                          keyvalues=None, # dict
                          tags=None,      # list
                          tickers=None,   # list
                          files=None,     # dict
                          sequences=None, # dict
                          plots=None,     # dict, DEPRECATED use files instead
                          videos=None,    # dict, DEPRECATED use files instead
                         ):
        """Creates a new collection at SeedMe.org
        Returns a string which is a JSON array
        Parameters
        ----------
        privacy         : str, optional
                          Permissions to access collection
                          'private' (default) or 'group' or 'public'

        sharing         : str or list of string, optional
                          space or comma delimimted string
                          or list of emails for sharing and notification

        notify          : bool, optional (default: False)
                          send email to shared users about shared collection

        title           : str, optional
                          Title for the collection

        description     : str, optional
                          Description for the collection

        credits         : str, optional
                          Credits for the collection

        license         : str, optional
                          License for the collection

        overwrite       : bool OR dict, optional
                          Dictionary consisting of following key value pairs
                          'all_types' : bool, optional (default: False)
                          'files' : bool, optional (default: False)
                          'plots' : bool, optional (default: False)
                          'sequences' : bool, optional (default: False)
                          'videos' : bool, optional (default: False)

        keyvalues       : dict, optional
                          Key Value pairs for the collection

        tags            : str OR list of str, optional
                         tags for the collection

        tickers         : str OR list of str, optional
                          Text tickers for the collection

        files           : dict OR list of dict, optional
                          Dictionary consisting of following key value pairs
                          'filepath'    : str, required
                          'title'       : str, optional
                          'description' : str, optional
                          *'poster'     : str, optional, *videos only
                          *'fps'        : float (default 30), *videos only
                          *'encode'     : bool, optional, *videos only

        sequences       : dict OR list of dict, optional
                          Dictionary consisting of following key value pairs
                          'filepath'    : str, required
                          'title'       : str, optional
                          'description' : str, optional
                          'fps'         : float (default 30)
                          'encode'      : bool, optional

        plots           : DEPRECATED use files instead
                          dict OR list of dict, optional
                          Dictionary consisting of following key value pairs
                          'filepath'    : str, required
                          'title'       : str, optional
                          'description' : str, optional

        videos          : DEPRECATED use files instead
                          dict OR list of dict, optional
                          Dictionary consisting of following key value pairs
                          'filepath'    : str, required
                          'poster'      : str, optional
                          'title'       : str, optional
                          'description' : str, optional
                          'fps'         : float (default 30)
                          'encode'      : bool, optional
        """

        # list of ordered dictionaries to collect text and file info
        # file dictionary contains the max file uploads per post
        # max file size per post permitted by the server
        #c_text_data = [collections.OrderedDict()]
        #c_file_data = [collections.OrderedDict()]
        c_text_data = [OrderedDict()]
        c_file_data = [OrderedDict()]

        c_file_data[0]['chunk_filesize'] = 0
        c_file_data[0]['file_count'] = 0
        c_file_data[0]['global_count'] = 0
        c_file_data[0]['index'] = 0
        c_file_data[0]['last_title_key'] = ''
        c_file_data[0]['last_title_value'] = ''

        #server settings constraints
        c_file_data[0]['max'] = 20 # max files per post
        # Subtract 1.0 MB for text content
        c_file_data[0]['post_max_size'] = 100.0*1024*1024
        #c_file_data[0]['post_max_size'] = 1024*500

        # check default path if authorization was not set
        if not self.username or not self.apikey:
            self._auth_default_check_()

        c_text_data[0]['username'] = self.username
        c_text_data[0]['apikey'] = self.apikey

        if not self.url:
            self.url = self.base_url #initialize

        if not self._url_sanity_(self.url):
            if not self.dry_run:
                sys.exit(1) #bail

        if privacy:
            self._privacy_sanity_(privacy)
            c_text_data[0]['privacy'] = privacy

        if sharing:
            #convert list to space delimited string
            if isinstance(sharing, list):
                temp = ''
                for item in sharing:
                    temp += ' ' + item
                c_text_data[0]['sharing'] = temp
            else:
                c_text_data[0]['sharing'] = sharing.replace(',', " ")

        if notify:
            if isinstance(notify, bool):
                c_text_data[0]['notify'] = notify
            else:
                log.warning('notify option must be True or False')

        if title:
            # title = self._sanitize_text_(title)
            c_text_data[0]['title'] = title

        if description:
            # description = self._sanitize_text_(description)
            c_text_data[0]['description'] = description

        if credits:
            # credits = self._sanitize_text_(credits)
            c_text_data[0]['credits'] = credits

        if license:
            # license = self._sanitize_text_(license)
            c_text_data[0]['license'] = license

        if overwrite or any(v for v in list(self.overwrite.values())):
            if isinstance(overwrite, bool):
                if overwrite: # global overwrite
                    self.overwrite['all_types'] = True
                    c_text_data[0]['overwrite'] = True
            elif isinstance(overwrite, dict): # many items in a dict
                for key, value in list(overwrite.items()): #py3 comp
                    if key in self.overwrite and value:
                        if key in 'all_types':
                            self.overwrite['all_types'] = True
                            c_text_data[0]['overwrite'] = True
                        if key in 'files':
                            self.overwrite['files'] = True
                            c_text_data[0]['file[overwrite]'] = True
                        if key in 'plots':
                            self.overwrite['plots'] = True
                            c_text_data[0]['plot[overwrite]'] = True
                        if key in 'sequences':
                            self.overwrite['sequences'] = True
                            c_text_data[0]['sequence[overwrite]'] = True
                        if key in 'videos':
                            self.overwrite['videos'] = True
                            c_text_data[0]['video[overwrite]'] = True
                    else:
                        log.warning('overwrite option must be a dictionary' +
                                    ' of the form \n' + str(self.overwrite))

            #Handle case if overwrite set by set_overwrite method
            if self.overwrite['all_types']:
                c_text_data[0]['overwrite'] = True
            else:
                if self.overwrite['files']:
                    c_text_data[0]['file[overwrite]'] = True
                if self.overwrite['plots']:
                    c_text_data[0]['plot[overwrite]'] = True
                if self.overwrite['sequences']:
                    c_text_data[0]['sequence[overwrite]'] = True
                if self.overwrite['videos']:
                    c_text_data[0]['video[overwrite]'] = True


        if tags:
            if isinstance(tags, list): # many tags in a list
                for i, tag in enumerate(tags, 1):
                    # tag = self._sanitize_text_(tag)
                    c_text_data[0]['tag[' + str(i) + ']'] = tag

            else: # single tag as a string
                # tag = self._sanitize_text_(tag)
                c_text_data[0]['tag'] = tags

        if tickers:
            if isinstance(tickers, list): # many tickers in a list
                for i, tickers in enumerate(tickers, 1):
                    # tickers = self._sanitize_text_(tickers)
                    c_text_data[0]['ticker[' + str(i) + ']'] = tickers

            else: # single key value pair as a string
                # tickers = self._sanitize_text_(tickers)
                c_text_data[0]['ticker'] = tickers

        if keyvalues:
            if isinstance(keyvalues, str):
                if len(keyvalues.split(':')) >= 2:
                    prefix = 'keyvalue[1]'
                    c_text_data[0][prefix] = keyvalues
                else:
                    log.warning('Skipping keyvalue: string should be colon' +\
                           'delimited as key:value, you specified' + keyvalues)
            else:
                i = len(keyvalues) #items are returned back to front
                for key, value in list(keyvalues.items()): #py3 comp
                    prefix = 'keyvalue[' + str(i) + ']'
                    c_text_data[0][prefix] = str(key) + ':' + str(value)
                    i -= 1
        """
        if files:
            self._append_content_(files, 'file', c_text_data, c_file_data)
        """
        if files:
            # add dict into at a list so it can be handled easily
            if isinstance(files, dict):
                data = [files]
            else:
                data = files

            flist = []
            plist = []
            vlist = []
            for mydict in data:
                # check whether wild card or dir path used
                if 'filepath' in mydict and ('*' in mydict['filepath'] or \
                      os.path.isdir(os.path.abspath(mydict['filepath']))):

                    v = os.path.abspath(mydict['filepath'])
                    filename = os.path.basename(v)
                    filelist = None
                    if os.path.isdir(v):
                        # todo can this be done more efficiently?
                        # glob files only above skip dirs
                        filelist = [os.path.join(v, f) for f in os.listdir(v) \
                                    if os.path.isfile(os.path.join(v, f))]

                    else:
                        filelist = glob.glob(v) # fetch files with wild card

                    if not filelist: # bail if empty dir
                        message = "No files found at '" + v + "'"
                        log.error(message)
                        if not self.dry_run:
                            sys.exit(1) #bail

                    for fpath in filelist:
                        #find content type of this file
                        content_type = self._find_content_type_(fpath)
                        self._file_sanity_(fpath, content_type)

                        temp = dict()

                        # add file path
                        temp['filepath'] = fpath

                        if len(filelist) == 1 and 'title' in mydict:
                            temp['title'] = mydict['title']
                        else:
                            #overwrite any specified file title
                            #temp['title'] = os.path.basename(fpath)
                            pass

                        # add description if any
                        if 'description' in mydict:
                            temp['description'] = mydict['description']

                        if content_type == 'plot':
                            if temp:
                                plist.append(temp.copy()) #deep copy
                        elif content_type == 'video':
                            # add encode option for video
                            if not 'encode' in mydict:
                                temp['encode'] = True
                            else:
                                temp['encode'] = mydict['encode']

                            # add fps option if any
                            if 'fps' in mydict:
                                temp['fps'] = mydict['fps']
                            if temp:
                                vlist.append(temp.copy()) #deep copy
                        else:
                            if temp:
                                flist.append(temp.copy()) #deep copy
                        temp.clear() #purge dict

                else: #single file

                    if 'filepath' in mydict:
                        v = os.path.abspath(mydict['filepath'])
                        filename = os.path.basename(v)

                        if not 'title' in mydict:
                            mydict['title'] = filename

                        #find content type of this file
                        content_type = self._find_content_type_(v)
                        if content_type == 'plot':
                            plist.append(mydict.copy()) #deep copy
                        elif content_type == 'video':
                            # add encode option for video
                            if not 'encode' in mydict:
                                mydict['encode'] = True

                            vlist.append(mydict.copy()) #deep copy
                        else:
                            flist.append(mydict.copy()) #deep copy
                    else: # assume this is video because file and plot
                          # must have all things in one dict
                        vlist.append(mydict.copy()) #deep copy


            if flist:
                self._append_content_(flist, 'file', c_text_data, c_file_data)
            if plist:
                self._append_content_(plist, 'plot', c_text_data, c_file_data)
            if vlist:
                self._append_content_(vlist, 'video', c_text_data, c_file_data)

            del flist[:], plist[:], vlist[:] #purge lists

        if plots:
            self._append_content_(plots, 'plot', c_text_data, c_file_data)

        if sequences:
            self._seq_vid_sanity_(sequences, 'sequence')
            self._append_content_(sequences, 'sequence', c_text_data,
                                  c_file_data)

        if videos:
            self._seq_vid_sanity_(videos, 'video')
            self._append_content_(videos, 'video', c_text_data, c_file_data)

        # post the content by splitting them into chunks of max upload files
        return self._split_content_(c_text_data, c_file_data)


    ##########################################################################
    # Updates any content in an existing collection
    ##########################################################################
    def update_collection(self,
                          collection_id,#required
                          privacy='',
                          sharing='',
                          notify='',
                          title='',
                          description='',
                          credits='',
                          license='',
                          overwrite=None, # bool or dict
                          keyvalues=None, # dict
                          tags=None,      # list
                          tickers=None,   # list
                          files=None,     # dict
                          sequences=None, # dict
                          plots=None,     # dict, DEPRECATED use files instead
                          videos=None,    # dict, DEPRECATED use files instead
                         ):
        """Updates any content for an existing collection at SeedMe.org
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id   : int, required
                          Collection ID to update

        privacy         : str, optional
                          Permissions to access collection
                          'private' (default) OR 'group' OR 'public'

        sharing         : str, optional
                          space OR comma delimimted string
                          or list of emails for sharing and notification

        notify          : bool, optional (default: False)
                          send email to shared users about shared collection

        title           : str, optional
                          Title for the collection

        description     : str, optional
                          Description for the collection

        credits         : str, optional
                          Credits for the collection

        license         : str, optional
                          License for the collection

        overwrite       : bool OR dict, optional
                          Dictionary consisting of following key value pairs
                          'all_types' : bool, optional (default: False)
                          'files' : bool, optional (default: False)
                          'plots' : bool, optional (default: False)
                          'sequences' : bool, optional (default: False)
                          'videos' : bool, optional (default: False)

        keyvalues       : dict, optional
                          Key Value pairs for the collection

        tags            : str OR list of str, optional
                         tags for the collection

        tickers         : str OR list of str, optional
                          Text tickers for the collection

        files           : dict OR list of dict, optional
                          Dictionary consisting of following key value pairs
                          'filepath'    : str, required
                          'title'       : str, optional
                          'description' : str, optional
                          *'poster'     : str, optional, *videos only
                          *'fps'        : float (default 30), *videos only
                          *'encode'     : bool, optional, *videos only

        sequences       : dict OR list of dict, optional
                          Dictionary consisting of following key value pairs
                          'filepath'    : str, required
                          'title'       : str, optional
                          'description' : str, optional
                          'fps'         : float (default 30)
                          'encode'      : bool, optional

        plots           : DEPRECATED use files instead
                          dict OR list of dict, optional
                          Dictionary consisting of following key value pairs
                          'filepath'    : str, required
                          'title'       : str, optional
                          'description' : str, optional

        videos          : DEPRECATED use files instead
                          dict OR list of dict, optional
                          Dictionary consisting of following key value pairs
                          'filepath'    : str, required
                          'poster'      : str, optional
                          'title'       : str, optional
                          'description' : str, optional
                          'fps'         : float (default 30)
                          'encode'      : bool, optional
        """

        self.url = self.base_url + '/' + str(collection_id) + '/update'

        if self._url_sanity_(self.url) and self._cid_sanity_(collection_id):
            return self.create_collection(privacy=privacy, sharing=sharing,
                                          notify=notify,
                                          title=title, description=description,
                                          credits=credits, license=license,
                                          overwrite=overwrite,
                                          keyvalues=keyvalues,
                                          tags=tags, tickers=tickers,
                                          files=files, plots=plots,
                                          sequences=sequences,
                                          videos=videos
                                         )


    ##########################################################################
    # Uploads a file to an existing collection
    ##########################################################################
    def add_file(self,
                 cid, #required
                 filepath, #required
                 title='',
                 description='',
                 overwrite=False, #Global setting to overwrite existing files
                 poster='', # for videos only, filepath for poster image
                 fps=30, # for videos only
                 encode=True, # for video only, pacebo same as transcode
                 transcode=True, # for video only, Note: default is true
                ):
        """Uploads a file to an existing collection.
        Returns a string which is a  JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update

        filepath      : str, required
                        Path for file to upload

        title         : str, optional
                        Title for the file

        description   : str, optional
                        Description for the file

        overwrite     : bool, optional (default: false)
                        Overwrite existing files in the collection
                        Global setting per execution for all files
                        (not per file)
        *'poster' : str, optional, *videos only
        *'fps'        : float (default 30), *videos only
        *'encode'     : bool, optional, *videos only
        *'transcode'  : bool, optional, same as encode, *videos only
        """
        # Create a new dictionary to hold file info
        up_file = dict()
        if filepath:
            up_file['filepath'] = filepath
        if title:
            up_file['title'] = title
        if description:
            up_file['description'] = description
        if poster:
            up_file['poster'] = poster
        if fps:
            up_file['fps'] = fps
        if encode and transcode:
            up_file['encode'] = True

        # set overwrite option
        if overwrite and not self.overwrite['all_types']:
            #self.overwrite['files'] = True
            self.set_overwrite(files=True)



        return self.update_collection(cid, files=up_file)


    ##########################################################################
    # Uploads a plot to an existing collection
    ##########################################################################
    def add_plot(self,
                 cid, #required
                 filepath, #required
                 title='',
                 description='',
                 overwrite=False, #Global setting to overwrite existing plots
                ):
        """DEPRECATED use add_file method
        Uploads a plot to an existing collection.
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update

        filepath      : str, required
                        Path for file to upload

        title         : str, optional
                        Title for the file

        description   : str, optional
                        Description for the file

        overwrite     : bool, optional (default: false)
                        Overwrite existing plots in the collection
                        Global setting per execution for all plots
                        (not per file)
        """
        # Create a new dictionary to hold plot info
        up_file = dict()
        if filepath:
            up_file['filepath'] = filepath
        if title:
            up_file['title'] = title
        if description:
            up_file['description'] = description

        # set overwrite option
        if overwrite and not self.overwrite['all_types']:
            #self.overwrite['plots'] = True
            self.set_overwrite(plots=True)

        log.critical("add_plot() method is deprecated.\n" +\
                     "Please use add_file() method")

        return self.update_collection(cid, plots=up_file)


    ##########################################################################
    # Uploads new or appends an image sequence to an existing collection
    ##########################################################################
    def add_sequence(self,
                     cid, #required
                     filepath='',
                     title='',
                     description='',
                     fps=30, #default is 30
                     encode=False,
                     overwrite=False, #Global setting to overwrite
                                      #existing files in a sequence
                    ):
        """Uploads new or appends an image sequence to an existing collection.
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update

        filepath      : str, optional
                        Path for file to upload

        title         : str, required
                        Title for the file

        description   : str, optional
                        Description for the file

        fps           : float, optional (default 30)
                        Frame rate for creating video

        encode        : bool, optional
                        Encode image sequence to video

        overwrite     : bool, optional (default: false)
                        Overwrite existing sequence files in the collection
                        Global setting per execution for all sequences
                        (not per file)
        """

        # Create a new dictionary to hold sequence info
        up_seq = dict()
        if filepath:
            up_seq['filepath'] = filepath
        if title:
            up_seq['title'] = title
        if description:
            up_seq['description'] = description
        if fps:
            up_seq['fps'] = fps
        if encode:
            up_seq['encode'] = encode

        # set overwrite option
        if overwrite and not self.overwrite['all_types']:
            #self.overwrite['sequences'] = True
            self.set_overwrite(sequences=True)

        return self.update_collection(cid, sequences=up_seq)


    ##########################################################################
    # Creates a video from an existing sequence
    ##########################################################################
    def encode_sequence(self,
                        cid, #required
                        title, #required
                        fps=30, #default is 30
                       ):
        """Creates a video from an existing sequence
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update

        title         : str, required
                        Title must be identical to an existing sequence title

        fps           : float, optional (default 30)
                        Frame rate for creating video
        """
        # Create a new dictionary to hold sequence info
        en_seq = dict()
        if title:
            en_seq['title'] = title
        else:
            message = 'Title is required to identify sequence for encoding'
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        if fps:
            en_seq['fps'] = fps
        en_seq['encode'] = True
        return self.update_collection(cid, sequences=en_seq)



    ##########################################################################
    # Notify users about shared collection via email
    ##########################################################################
    def notify(self,
               cid, #required
               email=None #str or list of str
              ):
        """Notify users about shared collection via email
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        email         : str, list or str
                        space or comma separated email str or list of emails
        """

        return self.update_collection(cid, sharing=email, notify=True)


    ##########################################################################
    # Uploads a video to an existing collection
    ##########################################################################
    def add_video(self,
                  cid, #required
                  filepath,  #required
                  poster='',
                  title='',
                  description='',
                  fps=30, #default same as video
                  encode=True, #pacebo same as transcode
                  transcode=True, #Note: default is true
                  overwrite=False, #Global setting to overwrite existing videos
                 ):
        """DEPRECATED use add_file method
        Uploads a video to an existing collection.
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        filepath      : str, required
                        Path for file to upload

        poster        : str, optional
                        Path for poster file to upload

        title         : str, optional
                        Title for the file

        description   : str, optional
                        Description for the file

        fps           : float (default is video's fps)
                        Frame rate for creating video

        encode        : bool, optional
                        Transcode video
                        (placebo same as encode)

        transcode     : bool, optional
                        Transcode video

        overwrite     : bool, optional (default: false)
                        Overwrite existing videos in the collection
                        Global setting per execution for all videos
                        (not per file)
        """
        # Create a new dictionary to hold video info
        up_vid = dict()
        if filepath:
            up_vid['filepath'] = filepath
        if poster:
            up_vid['poster'] = poster
        if title:
            up_vid['title'] = title
        if description:
            up_vid['description'] = description
        if fps:
            up_vid['fps'] = fps
        if encode and transcode:
            up_vid['encode'] = True

        # set overwrite option
        if overwrite and not self.overwrite['all_types']:
            #self.overwrite['videos'] = True
            self.set_overwrite(videos=True)

        log.critical("add_video() method is deprecated.\n" +\
                     "Please use add_file() method")
        return self.update_collection(cid, videos=up_vid)


    ##########################################################################
    # Transcodes an existing video
    ##########################################################################
    def encode_video(self,
                     cid, #required
                     title, #required
                     fps=30, #default same as video
                     #custom='' #future custom settings
                    ):
        """Alias function for transcode_video"""
        return self.transcode_video(cid, title, fps)

    def transcode_video(self,
                        cid, #required
                        title, #required
                        fps=30, #default same as video
                        #custom='' #future custom settings
                       ):
        """Transcodes an existing video
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update

        title         : str, required
                        Title must be identical to an existing video title

        fps           : float (default 30)
                        Frame rate for creating video
        """

        # Create a new dictionary to hold video info
        en_vid = dict()
        if title:
            en_vid['title'] = title
        else:
            message = 'Title is required to identify video for encoding'
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        if fps:
            en_vid['fps'] = fps
        en_vid['transcode'] = True

        #return self.update_collection(cid, videos=en_vid)
        return self.update_collection(cid, files=en_vid)


    ##########################################################################
    # Adds emails to an existing collection and notifies users
    ##########################################################################
    def add_email(self,
                  cid, #required
                  email, #required
                  notify=False,
                 ):
        """Adds emails to an existing collection and notifies users.
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        email         : str, list or str, required
                        space or comma separated email str or list of emails
        notify        : bool, optional (default: False)
                        send email notification to users about shared collection
        """
        return self.update_collection(cid, sharing=email, notify=notify)


    ##########################################################################
    # Adds emails to an existing collection and notifies users
    ##########################################################################
    def share(self,
              cid, #required
              email, #required
              notify=False,
             ):
        """Alias function for add_email"""
        return self.add_email(cid, email, notify)

    ##########################################################################
    # Adds a key-value pair to an existing collection
    ##########################################################################
    def add_keyvalue(self,
                     cid, #required
                     keyvalue, #required
                    ):
        """Adds a key-value pair to an existing collection.
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        keyvalue      : dict, required
                        Key Value pairs for the collection
        """
        if isinstance(keyvalue, str): # make a dict if keyvalue was a string
            temp = keyvalue.split(':')
            keyvalue = {temp[0]:temp[1]}
        return self.update_collection(cid, keyvalues=keyvalue)


    ##########################################################################
    # Adds a tag to an existing collection
    ##########################################################################
    def add_tag(self,
                cid, #required
                tag, #required
               ):
        """Adds a tag to an existing collection.
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        tag           : str or list of str, required
                        Tag for the collection
        """
        if isinstance(tag, str): # make a list if tag was a string
            tag = [tag]
        return self.update_collection(cid, tags=tag)


    ##########################################################################
    # Adds a ticker to an existing collection
    ##########################################################################
    def add_ticker(self,
                   cid, #required
                   ticker, #required
                  ):
        """Adds a ticker to an existing collection.
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        ticker        : str, required
                        Text ticker for the collection
        """
        if isinstance(ticker, str): # add string to a list
            ticker = [ticker]
        return self.update_collection(cid, tickers=ticker)


    ##########################################################################
    # Updates credits of an existing collection
    ##########################################################################
    def update_credits(self,
                       cid, #required
                       credits, #required
                      ):
        """Updates credits of an existing collection
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        credits       : str, required
                        New credits for the collection
        """
        return self.update_collection(cid, credits=credits)


    ##########################################################################
    # Updates description of an existing collection
    ##########################################################################
    def update_description(self,
                           cid, #required
                           description, #required
                          ):
        """Updates description of an existing collection
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        description   : str, required
                        New description for the collection
        """
        return self.update_collection(cid, description=description)


    ##########################################################################
    # Updates license of an existing collection
    ##########################################################################
    def update_license(self,
                       cid, #required
                       license, #required
                      ):
        """Updates license of an existing collection
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        license       : str, required
                        New license for the collection
        """
        return self.update_collection(cid, license=license)


    ##########################################################################
    # Updates privacy, adds emails and notifies for an existing collection
    ##########################################################################
    def update_privacy(self,
                       cid, #required
                       privacy, #required
                       email=None, #str or list of str
                       notify=False #notify shared users
                      ):
        """ Updates privacy, adds emails and notifies users
        for an existing collection
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        privacy       : str, required
                        privacy for the collection (public, group, private)
        email         : str, list or str, optional
                        space or comma separated email str or list of emails
        notify        : bool, optional (default: False)
                        send email notification to users about shared collection
        """
        return self.update_collection(cid, privacy=privacy,
                                      sharing=email, notify=notify)


    ##########################################################################
    # Updates title of an existing collection
    ##########################################################################
    def update_title(self,
                     cid, #required
                     title, #required
                    ):
        """Updates title of an existing collection
        Returns a string which is a JSON array
        Parameters
        ----------
        collection_id : int, required
                        Collection ID to update
        title         : str, required
                        New title for the collection
        """
        return self.update_collection(cid, title=title)




    ##########################################################################
    # INTERNAL METHODS for SeedMe Module
    ##########################################################################


    ##########################################################################
    # Sets authorization from default path ~/.seedme or ~/seedme.txt
    ##########################################################################
    def _auth_default_check_(self):
        """Sets authorization from default path ~/.seedme or ~/seedme"""
        auth1 = '~/.seedme'
        auth2 = '~/seedme.txt'
        #check default locations ~/.seedme or ~/seedme.txt
        if os.path.isfile(os.path.normpath(os.path.expanduser(auth1))):
            self.set_auth_via_file(auth1)
        elif os.path.isfile(os.path.normpath(os.path.expanduser(auth2))):
            self.set_auth_via_file(auth2)
        else:
            self.set_auth_via_file('') # cause error
            if not self.dry_run:
                sys.exit(1) #bail


    ##########################################################################
    # Check whether plausible collection id is provided
    ##########################################################################
    def _cid_sanity_(self, cid):
        """Check whether plausible collection id is provided
        Returns bool or exits"""
        if not cid:
            message = "Invalid collection id = '" + str(cid) + "'"
            log.error(message)
            sys.exit(1) #bail
        return True


    ##########################################################################
    # Finds plot, video or file content type based on file extension
    ##########################################################################
    def _find_content_type_(self, path):
        """Finds content type based on file extension
        Returns content type or exits"""
        if (not path) or (not os.path.isfile(path)):
            message = "Invalid path or file could not be read. '" + path + "'"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        else: #warn for unsupported file extensions
            permitted_ext = {'file': ['dat', 'fig', 'gui', 'gz', 'ipynb',
                                      'kar', 'm', 'p', 'pdf', 'session', 'tar',
                                      'tgz', 'txt', 'xml', 'zip',
                                     ],
                             'plot': ['jpeg', 'jpg', 'png'],
                             'video':['m4v', 'mpg', 'mpeg', 'mp4', 'mov',
                                      'webm'
                                     ],
                            }

            filename, file_ext = os.path.splitext(path)
            file_ext = file_ext.strip('.').lower() # strip dot and lower case

            if file_ext in permitted_ext['plot']:
                return 'plot'
            elif file_ext in permitted_ext['video']:
                return 'video'
            else:
                return 'file'


    ##########################################################################
    # Checks whether the file exists, readable with permitted extension
    ##########################################################################
    def _file_sanity_(self, path, content_type):
        """Check whether the file exists, readable with permitted extension
        Returns True or exits"""
        if (not path) or (not os.path.isfile(path)):
            message = "Invalid path or file could not be read. '" + path + "'"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        else: #warn for unsupported file extensions
            permitted_ext = {'file': ['dat', 'fig', 'gui', 'gz', 'ipynb',
                                      'kar', 'm', 'p', 'pdf', 'session', 'tar',
                                      'tgz', 'txt', 'xml', 'zip',
                                      'jpeg', 'jpg', 'png',
                                      'm4v', 'mpg', 'mpeg', 'mp4', 'mov',
                                      'webm',
                                     ],
                             'plot': ['jpeg', 'jpg', 'png'],
                             'sequence': ['jpeg', 'jpg', 'png'],
                             'video': ['m4v', 'mpg', 'mpeg', 'mp4', 'mov',
                                       'webm'
                                      ],
                            }

            filename, file_ext = os.path.splitext(path)
            file_ext = file_ext.strip('.').lower() # strip dot and lower case

            if not file_ext in permitted_ext[content_type]:
                message = "File extension not permitted for " +\
                        str(content_type) + " : " + str(path) +\
                        "\nPermitted extensions for " + str(content_type) +\
                        " are : " + ', '.join(permitted_ext[content_type])
                log.warning(message)

        return True


    ##########################################################################
    # Reads file at a specified path
    ##########################################################################
    def _read_file_(self, pathname):
        """Reads file at a specified path"""
        if self.dry_run:
            return
        else:
            with open(pathname, 'rb') as my_file:
                return my_file.read()


    ##########################################################################
    # Checks for valid privacy setting
    ##########################################################################
    def _privacy_sanity_(self, privacy):
        """Checks for valid privacy setting
        Returns bool or exits"""
        if privacy == 'private' \
           or privacy == 'group' \
           or privacy == 'public':
            return True
        else:
            message = "Invalid privacy = '" + privacy + "'"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail


    ##########################################################################
    # Sanitizes user input text
    ##########################################################################
    def _sanitize_text_(self, text):
        """Sanitizes user input text"""
        #todo
        pass
        #return text


    ##########################################################################
    # Checks compatible service version and url
    ##########################################################################
    def _url_sanity_(self, my_url=''):
        """Checks compatible service version and url
        Returns bool"""
        if not my_url: # no url
            message = 'URL not found'
            log.error(message)
        elif not(('http://' in my_url or 'https://' in my_url)
                 and 'seedme.org' in my_url):
            message = 'Invalid url specified: ' + my_url
            log.error(message)
        else:
            u_list = my_url.split("/")
            # domain check
            #if u_list[2] == 'dev.seedme.org' \
            #        or u_list[2] == 'www.seedme.org' \
            #        or u_list[2] == 'seedme.org':
            if 'seedme.org' in u_list[2]:
                if u_list[-1] == 'update':
                    ver = u_list[-4]
                else:
                    ver = u_list[-2]

                if ver == self.service_version: # version check
                    return True
                else: # incompatible service version
                    message = 'Incompatible seedme client vs ' +\
                              ' web-services version ' + str(u_list[-2]) +\
                              '\nDownload corresponding client ' +\
                              'from www.seedme.org/downloads'
                    log.error(message)
            else: # bad domain
                message = 'Invalid url ' + str(my_url)
                log.error(message)
        return False


    ##########################################################################
    # Checks sequence and video internal options
    ##########################################################################
    def _seq_vid_internal_(self, my_dict='', content_type=''):
        """Checks sequence and video internal options"""
        dtext = encode = fpath = fps = ttext = ''
        if 'filepath' in my_dict:
            fpath = my_dict['filepath']
        if 'title' in my_dict:
            ttext = my_dict['title']
        if 'description' in my_dict:
            dtext = my_dict['description']
        if 'fps' in my_dict:
            fps = my_dict['fps']
        if 'encode' in my_dict:
            encode = my_dict['encode']

        # encode set without title and filepath
        if encode and (not ttext) and (not fpath):
            message = "Invalid " + content_type +\
                      " encode setting without title and filepath"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        # fps set without title and filepath
        elif fps and (not ttext) and (not fpath):
            message = "Invalid " + content_type +\
                      " fps setting without title and filepath"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        elif dtext and (not fpath): # desc set without filepath
            message = "Invalid " + content_type +\
                      " description without filepath"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail
        return True


    ##########################################################################
    # Checks Sequence and Video options sanity
    ##########################################################################
    def _seq_vid_sanity_(self, src_data='', content_type=''):
        """Checks Sequence and Video options sanity"""
        if isinstance(src_data, list): # data has a list of dict items
            for my_dict in src_data:
                self._seq_vid_internal_(my_dict, content_type)

        elif type(src_data) == dict: # data has items in a dict
            self._seq_vid_internal_(src_data, content_type)

        else: # bail input structure is invalid for data
            message = "Data format is invalid for \n" + str(src_data) +\
                      "\nCorrect data format is a 'dict' or a 'list' of 'dict'"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail


    ##########################################################################
    # Adds break points to accommodate max upload limit imposed by server
    ##########################################################################
    def _add_break_point_(self, prefix, c_text_data, c_file_data):
        """Adds break points to accommodate max upload limit imposed by server
        """
        fcount = c_file_data[0]['file_count'] + c_file_data[0]['global_count']
        c_file_data[0]['global_count'] = fcount

        index = c_file_data[0]['index'] # fetch current chunk index

        if fcount > 0: # dont add break points at start
            break_ltk = 'break_last_title_key' + str(fcount)
            break_ltv = 'break_last_title_value' + str(fcount)
            break_cp = 'break_cur_prefix' + str(fcount)
            #print 'LTK, prefix', break_ltk, prefix
            #print 'index, len', index, len(c_file_data)

            # When clean break found
            # do not add new dictionaries and
            # do not overwrite break_ltk, break_ltv and break_cp
            if index == len(c_file_data) -1:
                if break_cp in c_file_data[index]:
                    #print "\n\n\nCLEAN BREAK"
                    #print break_cp, c_file_data[index]
                    #print c_file_data[index][break_cp]
                    return

            #Add dictionaries
            c_text_data.append(OrderedDict())
            c_file_data.append(OrderedDict())


            # Add break info to file dictionary
            c_file_data[index][break_ltk] = c_file_data[0]['last_title_key']
            c_file_data[index][break_ltv] = c_file_data[0]['last_title_value']
            c_file_data[index][break_cp] = prefix
            c_file_data[0]['chunk_filesize'] = 0 #reset chunk sum
            c_file_data[0]['file_count'] = 0 #reset chunk file count
            c_file_data[0]['index'] += 1 #increment chunk index
            if not fcount %  c_file_data[0]['max']:
                log.debug('count break')
            else:
                log.debug('size break')

            new_index = index + 1
            if  self.overwrite['all_types']:
                c_text_data[new_index]['overwrite'] = True
            else:
                if  self.overwrite['files']:
                    c_text_data[new_index]['file[overwrite]'] = True
                if  self.overwrite['plots']:
                    c_text_data[new_index]['plot[overwrite]'] = True
                if  self.overwrite['sequences']:
                    c_text_data[new_index]['sequence[overwrite]'] = True
                if  self.overwrite['videos']:
                    c_text_data[new_index]['video[overwrite]'] = True


    ##########################################################################
    # Process and add content to c_text_data and c_file_data
    ##########################################################################
    def _append_content_(self, data, content_type, c_text_data, c_file_data):
        """Processes and adds content to c_text_data and c_file_data"""
        # add dict into at a list so it can be handled easily
        if isinstance(data, dict):
            data = [data]

        if isinstance(data, list): # data has a list of dict items
            for i, my_dict in enumerate(data, 1):
                #todo investigate if filepath requirement can be waived
                # Bail when required filepath is not found
                #if not 'filepath' in my_dict:
                #    message = "'filepath' field not found in \n" +
                #                str(my_dict)
                #    log.error(message)
                #    if not self.dry_run:
                #        sys.exit(1) #bail
                # Add automatic title for sequence when not found
                if ('sequence' == content_type) and \
                     (not 'title' in list(my_dict.keys())): #py3 comp
                    message = "Sequence title not found\n" +\
                              str(my_dict)
                    log.warning(message)
                    auto_title = 'Auto sequence title ' + \
                           str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    my_dict['title'] = auto_title
                    log.info("Auto-generating seqeunce title as: " +
                             str(auto_title))

                #todo investigate clean break
                '''
                if c_file_data[0]['file_count'] == c_file_data[0]['max']:
                    print 'adding clean break 1'
                    self._add_break_point_('clean_break', c_text_data,
                                            c_file_data)
                '''

                # Now parse each key except 'filepath', 'encode', 'transcode'
                # to ensure clean breaks and trigger encoding after
                # adding files

                #fpath_key = fpath_val = en_key = en_val = '' #pre plot bork
                fpath_key = fpath_val = en_key = en_val = None
                for key, val in list(my_dict.items()): #py3 comp
                    if key == 'filepath': #capture and hold filepath k, v
                        fpath_key = key
                        fpath_val = val
                    elif key == 'encode' or key == 'transcode':
                        # capture and hold encode or transcode k, v
                        en_key = key
                        en_val = val
                    else:
                        self._parse_content_(key, val, content_type, i,
                                             c_text_data, c_file_data)

                # Now parse the 'filepath' key if it was set
                if fpath_key:
                    self._parse_content_(fpath_key, fpath_val, content_type, i,
                                         c_text_data, c_file_data)

                # Now parse the 'encode' or 'transcode' key if it was set
                if en_key:
                    # unclean break boundary to handle encode
                    prefix = content_type + '[' + str(i) + ']'
                    if c_file_data[0]['file_count'] == c_file_data[0]['max']:
                        self._add_break_point_(prefix, c_text_data,
                                               c_file_data)
                    self._parse_content_(en_key, en_val, content_type, i,
                                         c_text_data, c_file_data)

        else: # bail input structure is invalid for data
            message = "Data format is invalid for \n" + str(data) +\
                      "\nCorrect data format is a 'dict' or a 'list' of 'dict'"
            log.error(message)
            if not self.dry_run:
                sys.exit(1) #bail

    ##########################################################################
    # Download files from the server
    ##########################################################################
    def _do_download_(self, url, filename, path):
        """Downloads files from the server"""
        local_filename = path + '/' + filename

        my_method = self._find_post_method_()
        if my_method == 'curl':
            if self.curl_path: #use specified or found path
                my_buffer = str(self.curl_path)
            else: # use environment path
                my_buffer = 'curl'

            if not self.c_log: #silent
                my_buffer += ' -s'

            #add cacert if provided
            if self.cacert_path:
                my_buffer += ' -cacert ' + self.cacert_path

            #disable ssl only when asked and no cert provide
            if not self.ssl and not self.cacert_path:
                my_buffer += ' -k '


            my_buffer += ' -o ' + local_filename + ' ' + url

            if self.curl_commands: # show curl command line
                #hide apikey
                log.info(my_buffer.replace(self.apikey, '***')
                         .replace('username=' +self.username, 'username=***'))
            elif self.curl_commands_auth:
                log.info(my_buffer) #show apikey

            if self.dry_run:
                return '{"message": "Dry Run"}'

            #http://pymotw.com/2/subprocess/
            #http://www.pythonforbeginners.com/os/
                        #subprocess-for-system-administrators

            my_p = subprocess.Popen(my_buffer, stdout=subprocess.PIPE,
                                    shell=True, stderr=None, stdin=None)
            result = my_p.communicate()[0]
            my_p.stdout.close()

        else:
            # NOTE the stream=True parameter
            r = requests.get(url, stream=True)
            total_length = int(r.headers.get('content-length'))
            if not total_length:
                total_length = 1

            with open(local_filename, 'wb') as f:
                dl = 0
                for chunk in r.iter_content(chunk_size=1024):
                    dl += len(chunk)
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        #progress bar
                        #done = int(50 * dl / total_length)
                        #sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )

                        done = str(100 * dl / total_length)
                        sys.stdout.write("[%s%s]\r" % (done, ' %'))
                        sys.stdout.flush()
                    f.flush()
            return local_filename


    ##########################################################################
    # Query the server
    ##########################################################################
    def _do_query_(self, q_data):
        """Queries the server.
        Returns string as JSON array
        """
        result = ''
        my_method = self._find_post_method_()

        my_buffer = ''
        if my_method == 'curl':
            #my_buffer = 'curl -v -X POST ' + str(self.url)
            if self.curl_path: #use specified or found path
                my_buffer += str(self.curl_path)
            else: # use environment path
                my_buffer = 'curl'

            if not self.c_log: #silent
                my_buffer += ' -s'

            #add cacert if provided
            if self.cacert_path:
                my_buffer += ' -cacert ' + self.cacert_path

            #disable ssl only when asked and no cert provide
            if not self.ssl and not self.cacert_path:
                my_buffer += ' -k '


            my_buffer += ' -g -X GET "' + str(self.url) + '?'

            first = True
            for key, val in list(q_data.items()): #py3 comp
                if first:
                    #my_buffer += 'parameters[' + str(key) + ']=' +\
                                             #str(_escape_text_(val))
                    my_buffer += str(key) + '=' + str(_escape_text_(val))
                else: #add ampersand & prefix
                    #my_buffer += '&parameters[' + str(key) + ']=' +\
                    #                         str(_escape_text_(val))
                    my_buffer += '&' + str(key) + '=' +str(_escape_text_(val))

                first = False
            # close quote
            my_buffer += '"'


            if self.curl_commands: # show curl command line
                #hide apikey
                log.info(my_buffer.replace(self.apikey, '***')
                         .replace('username=' +self.username, 'username=***'))
            elif self.curl_commands_auth:
                log.info(my_buffer) #show apikey

            if self.dry_run:
                return '{"message": "Dry Run"}'

            #http://pymotw.com/2/subprocess/
            #http://www.pythonforbeginners.com/os/
                        #subprocess-for-system-administrators

            my_p = subprocess.Popen(my_buffer, stdout=subprocess.PIPE,
                                    shell=True, stderr=None, stdin=None)
            result = my_p.communicate()[0]
            my_p.stdout.close()

        else: #post method will use requests module
            payload = dict()
            for key, val in list(q_data.items()): #py3 comp
                #payload['parameters['+ str(key) +']'] = str(_escape_text_(val))
                payload[str(key)] = str(_escape_text_(val))

            if self.dry_run:
                return '{"message": "Dry Run"}'

            # use ssl settings if provided
            if self.cacert_path:
                r_get = requests.get(self.url, params=payload,
                                     verify=self.cacert_path)
            elif not self.ssl: # if ssl turned off
                r_get = requests.get(self.url, params=payload,
                                     verify=False)
            else: # use ssl cert from default location
                try:
                    r_get = requests.get(self.url, params=payload)
                # warn if cert was not found
                except requests.exceptions.SSLError as e:
                    message = "SSL certificate not found on your system." +\
                              "Please set its path for secure communication" +\
                              str(e)
                    log.warning(message)
                    r_get = requests.get(self.url, params=payload)

            #print r_get.url
            result = r_get.text

        if result: # We got some result back from server
            if 'Site under maintenance' in result:
                message = "\nSeedMe.org is under Maintenance." +\
                          " Please try later."
                log.info(result)
                log.critical(message)
                sys.exit(1) #bail
            else:
                #log.info(result) # ugly print
                try:
                # Pretty print result
                    p_json = json.loads(result)
                    log.info(json.dumps(p_json, indent=4, sort_keys=True,
                                        separators=(',', ': ')))
                except (ValueError, TypeError) as e:
                    log.error('Invalid JSON response from server. ' + str(e))

                log.info('NOTICE: Query omits sequence information at present'+
                         ' (Under development).')
                return result
        else: #no response from server
            message = "No response from server"
            log.error(message)
            sys.exit(1) #bail

        log.info('NOTICE: Query omits sequence information at present'+
                 ' (Under development).')
        return result #return original output



    ##########################################################################
    # Posts content to server
    ##########################################################################
    def _do_post_(self, c_text_data, c_file_data):
        """Posts content to server.
        Returns string as JSON array
        """
        result = ''
        my_method = self._find_post_method_()

        #clean up extra overwrite flags if any
        if  any(v for v in list(self.overwrite.values())):
            fp = list(k for k in list(c_file_data.keys()) if 'file[' in k)
            td = list(k for k in list(c_text_data.keys())
                      if 'file[overwrite]' in k)
            if not any('filepath' in s for s in fp) and td:
                del c_text_data['file[overwrite]']
                #print 'DELETED file overwrite'

            fp = list(k for k in list(c_file_data.keys()) if 'plot[' in k)
            td = list(k for k in list(c_text_data.keys())
                      if 'plot[overwrite]' in k)
            if not any('filepath' in s for s in fp) and td:
                del c_text_data['plot[overwrite]']
                #print 'DELETED PLOT overwrite'

            fp = list(k for k in list(c_file_data.keys()) if 'sequence[' in k)
            td = list(k for k in list(c_text_data.keys())
                      if 'sequence[overwrite]' in k)
            if not any('filepath' in s for s in fp) and td:
                del c_text_data['sequence[overwrite]']

            fp = list(k for k in list(c_file_data.keys()) if 'video[' in k)
            td = list(k for k in list(c_text_data.keys())
                      if 'video[overwrite]' in k)
            if not any('filepath' in s for s in fp) and td:
                del c_text_data['video[overwrite]']

        if my_method == 'curl':
            #my_buffer = 'curl -v -X POST ' + str(self.url)
            if self.curl_path: #use specified or found path
                my_buffer = str(self.curl_path)
            else: # use environment path
                my_buffer = 'curl'

            if not self.c_log: #silent
                my_buffer += ' -s'

            #add cacert if provided
            if self.cacert_path:
                my_buffer += ' -cacert ' + self.cacert_path

            #disable ssl only when asked and no cert provide
            if not self.ssl and not self.cacert_path:
                my_buffer += ' -k '

            my_buffer += ' -X POST ' + str(self.url)

            for key, val in list(c_text_data.items()): #py3 comp
                my_buffer += ' -F "' + str(key) + '=' +\
                                       str(_escape_text_(val)) + '"'

            for key, val in list(c_file_data.items()): #py3 comp
                my_buffer += ' -F "' + str(key) + '=@' + str(val) + '"'

            if self.curl_commands: # show curl command line
                #hide apikey
                log.info(my_buffer.replace(self.apikey, '***')
                         .replace('username=' +self.username, 'username=***'))
            elif self.curl_commands_auth:
                log.info(my_buffer) #show apikey

            if self.dry_run:
                return '{"collection_id":"-1",' +\
                       '"status" : "success", "message": "Dry Run"}'

            #http://pymotw.com/2/subprocess/
            #http://www.pythonforbeginners.com/os/
                        #subprocess-for-system-administrators

            my_p = subprocess.Popen(my_buffer, stdout=subprocess.PIPE,
                                    shell=True, stderr=None, stdin=None)

            #DEVNULL portability
            #http://stackoverflow.com/questions/11269575
                        #/how-to-hide-output-of-subprocess-in-python-2-7

            # todo check whether stderr should be redirected to STDOUT
            #my_p = subprocess.Popen(my_buffer,
            #                        shell=True, stdout=subprocess.PIPE,
            #                        stderr=subprocess.STDOUT, stdin=None)
            result = my_p.communicate()[0]
            my_p.stdout.close()

        else: #post method will use requests module
            #print c_text_data
            #print c_file_data

            # create temp dict where we can open files for POST
            upload_files = OrderedDict()

            for key, val in list(c_file_data.items()): #py3 comp
                filename = os.path.basename(val)
                # populate temp dict
                upload_files[key] = [filename, self._read_file_(val)]

            if self.dry_run:
                return '{"collection_id":"-1",' +\
                       '"status" : "success", "message": "Dry Run"}'

            # Reuse requests session whenever possible
            if not self.session:
                # Create session when none exists
                self.session = requests.Session()

            # use ssl settings if provided
            if self.cacert_path:
                r_post = self.session.post(self.url, data=c_text_data,
                                           files=upload_files,
                                           verify=self.cacert_path)
            elif not self.ssl: # if ssl turned off
                r_post = self.session.post(self.url, data=c_text_data,
                                           files=upload_files, verify=False)
            else: # use ssl cert from default location
                try:
                    r_post = self.session.post(self.url, data=c_text_data,
                                               files=upload_files)
                # warn if cert was not found
                except requests.exceptions.SSLError as e:
                    message = "SSL certificate not found on your system." +\
                              "Please set its path for secure communication" +\
                              str(e)
                    log.warning(message)
                    r_post = self.session.post(self.url, data=c_text_data,
                                               files=upload_files)

            # toss older POST without requests sessions
            #r_post = requests.post(self.url, data=c_text_data,
            #                       files=upload_files)

            result = r_post.text

        """
        # old response handling
        if result: # We got some result back from server
            try:
                p_result = json.loads(result) # create dict from string result
                #if web service responds with a list it is an error
                if isinstance(p_result, list):
                    raise ValueError
            except ValueError:
                if 'Site under maintenance' in result:
                    message = "\nSeedMe.org is under Maintenance." +\
                              " Please try later."
                    log.info(result)
                    log.critical(message)
                    sys.exit(1) #bail

                if self.url[-6:] == 'update':
                    message = "Collection update could not be fulfilled"
                else:
                    message = "Collection creation could not fulfilled"
                log.info(result)
                log.error(message)
                sys.exit(1) #bail
        """

        if result: # We got some result back from server
            p_result = None
            if 'Site under maintenance' in result:
                message = "\nSeedMe.org is under Maintenance." +\
                          " Please try later."
                log.info(result)
                log.critical(message)
                sys.exit(1) #bail
            else:
                try:
                    # create dict from string result
                    p_result = json.loads(result)
                except (ValueError, TypeError) as e:
                    if self.url[-6:] == 'update':
                        message = "Collection update could not be fulfilled"
                    else:
                        message = "Collection creation could not fulfilled"
                    log.error(message)
                    log.error('Invalid JSON response from server. ' + str(e))
                    sys.exit(1) #bail

            # Success
            #if p_result and (p_result['status'] == 'success'):
            if 'status' in p_result:
                if p_result['status'] == 'success':
                    if self.url[-6:] == 'update':
                        u_list = self.url.split("/")
                        cid = u_list[-2]
                        log.info("Success: Collection updated at " +\
                                 "collection id " + str(cid))
                        log.info(result)
                    else:
                        if 'collection_id' not in p_result:
                            message = "Failed POST, collection id not recieved"
                            log.error(message)
                            sys.exit(1) #bail
                        cid = p_result['collection_id']
                        log.info("Success: Collection created at " +\
                                 "collection id " + str(cid))
                        log.info(result)

                # Partial success
                elif p_result['status'] == 'partial':
                    if self.url[-6:] == 'update':
                        u_list = self.url.split("/")
                        cid = u_list[-2]
                        log.info(result)
                        log.warning("Partial: Incomplete Collection update " +\
                                    "at " + "collection id " + str(cid))
                    else:
                        log.info(result)
                        log.warning("Partial: Incomplete Collection creation")

                # Errors in POST
                else:
                    if self.url[-6:] == 'update':
                        u_list = self.url.split("/")
                        cid = u_list[-2]
                        message = "Failed collection update at " +\
                                  "collection id " + str(cid)
                        log.info(result)
                        log.error(message)
                        sys.exit(1) # bail
                    else:
                        message = "Failed new collection creation"
                        log.info(result)
                        log.error(message)
                        sys.exit(1) #bail

            else: #status not returned in response
                if self.url[-6:] == 'update':
                    u_list = self.url.split("/")
                    cid = u_list[-2]
                    message = "Failed collection update at collection id " +\
                               str(cid)
                    log.info(result)
                    log.error(message)
                    sys.exit(1) # bail
                else:
                    message = "Failed new collection creation"
                    log.info(result)
                    log.error(message)
                    sys.exit(1) #bail


        else: # No result recieved in POST
            if self.url[-6:] == 'update':
                u_list = self.url.split("/")
                cid = u_list[-2]
                message = "Failed to update collection id " + str(cid)
                message += "\nNo response from server"
                log.info(result)
                log.error(message)
                sys.exit(1) #bail
            else:
                message = "Failed to create new collection"
                message += "\nNo response from server"
                log.info(result)
                log.error(message)
                sys.exit(1) #bail

        return result #return original output


    ###########################################################################
    # Find which method to use for POST
    # Returns string as 'curl' or 'requests' or exits when none found
    ###########################################################################
    def _find_post_method_(self):
        """Finds which method to use for POST
        Returns string as 'curl' or 'requests'
        Exits when none found
        """
        bad_input = False
        if self.post_method:
            # return if post method is correctly set
            if self.post_method == 'requests' or self.post_method == 'curl':
                return self.post_method
            else: # Warn and continue execution to find a valid post method
                bad_input = True
                message = 'Warning: Invalid POST method: ' +\
                          str(self.post_method) +\
                          "\nValid POST methods are 'requests' or 'curl'\n"
                log.warning(message)

        curl_exists = False
        # Does curl exists in provided path?
        if _which_(self.curl_path):
            #print 'Curl found at: ' + self.curl_path
            curl_exists = True

        # Does curl exist in default system path?
        elif _which_('curl'):
            self.curl_path = _which_('curl')
            #print 'System curl found at: ' + self.curl_path
            curl_exists = True

        else:
            curl_exists = False


        # Identify POST method to use
        if self.requests_loaded: # Preferred method
            if bad_input:
                log.warning('Defaulting to "requests" method for POST')
            self.post_method = 'requests'
            return self.post_method

        elif curl_exists:
            if bad_input:
                log.warning('Defaulting to "curl" method for POST')
            self.post_method = 'curl'
            return self.post_method

        else:
            message = 'python requests module or curl executible not found' +\
                      'Either install python requests module Or install ' +\
                      'curl executible and add it to your system path'
            log.error(message)
            sys.exit(1) #bail


    ##########################################################################
    # Parse data and append to c_text_data and c_file_data
    ##########################################################################
    def _parse_content_(self, k, v, content_type, i, c_text_data, c_file_data):
        """Parse data and append to c_text_data and c_file_data"""
        #index = int(c_file_data[0]['file_count'] / c_file_data[0]['max'])
        index = c_file_data[0]['index']
        prefix = content_type + '[' + str(i) + ']'
        j = 1

        if k == 'filepath': # required
            v = os.path.abspath(v)
            filename = os.path.basename(v)
            # check whether wild card or dir path used
            if '*' in filename or os.path.isdir(v):
                #filelist = [] #pre plot bork
                filelist = None
                if os.path.isdir(v):
                    # todo can this be done more efficiently?
                    # glob files only above skip dirs
                    filelist = [os.path.join(v, f) for f in os.listdir(v) \
                                if os.path.isfile(os.path.join(v, f))]

                else:
                    filelist = glob.glob(v) # fetch files with wild card

                if not filelist: # bail if empty dir
                    message = "No files found at '" + v + "'"
                    log.error(message)
                    if not self.dry_run:
                        sys.exit(1) #bail

                #print 'no of files ', len(filelist)
                for n, fpath in enumerate(filelist, i):
                    self._file_sanity_(fpath, content_type)
                    if content_type == 'sequence':
                        prefix = content_type + \
                                '[' + str(i) + '][filepath][' + str(j) + ']'
                    else:
                        prefix = content_type + '[' + str(n) + '][filepath]'

                    #filesize
                    fsize = os.path.getsize(fpath)
                    if fsize > c_file_data[0]['post_max_size']:
                        message = 'File over maximum permitted size : ' +\
                            human_readable_size(fsize) +\
                            "\nMaximum permitted size : " +\
                            human_readable_size(c_file_data[0]['post_max_size'])
                        log.warning(message)
                        #if not self.dry_run:
                        #    sys.exit(1) #bail
                    temp_cumu = c_file_data[0]['chunk_filesize'] + fsize
                    log.debug('SIZE ' + str(temp_cumu) +
                              ', CUMU ' +
                              str(c_file_data[0]['chunk_filesize']) +
                              ', MAX ' + str(c_file_data[0]['post_max_size']))
                    if c_file_data[0]['file_count'] == c_file_data[0]['max']\
                        or temp_cumu > c_file_data[0]['post_max_size']:
                        self._add_break_point_(prefix, c_text_data,
                                               c_file_data)
                    new_index = c_file_data[0]['index']
                    #filesize

                    #if not c_file_data[0]['file_count']%c_file_data[0]['max']:
                    #  self._add_break_point_(prefix, c_text_data, c_file_data)
                    #new_index = int(c_file_data[0]['file_count'] /
                    #                                    c_file_data[0]['max'])
                    #filename = os.path.basename(fpath)
                    #c_file_data[new_index][prefix]=[filename, open(f, 'rb')]
                    c_file_data[new_index][prefix] = fpath
                    c_file_data[0]['file_count'] += 1
                    c_file_data[0]['chunk_filesize'] += fsize
                    j += 1

            else: # no wildcard used
                self._file_sanity_(v, content_type)
                prefix = prefix + '[filepath]'

                #filesize
                fsize = os.path.getsize(v)
                if fsize > c_file_data[0]['post_max_size']:
                    message = 'File over maximum permitted size : ' +\
                        human_readable_size(fsize) +\
                        "\nMaximum permitted size : " +\
                        human_readable_size(c_file_data[0]['post_max_size'])
                    log.warning(message)
                    #if not self.dry_run:
                    #    sys.exit(1) #bail
                temp_cumu = c_file_data[0]['chunk_filesize'] + fsize
                log.debug('SIZE ' + str(temp_cumu) +
                          ', CUMU ' + str(c_file_data[0]['chunk_filesize']) +
                          ', MAX ' + str(c_file_data[0]['post_max_size']))
                if not c_file_data[0]['file_count'] % c_file_data[0]['max']\
                    or temp_cumu > c_file_data[0]['post_max_size']:
                    self._add_break_point_(prefix, c_text_data, c_file_data)
                new_index = c_file_data[0]['index']
                #filesize

                #if not c_file_data[0]['file_count'] % c_file_data[0]['max']:
                #    self._add_break_point_(prefix, c_text_data, c_file_data)
                #new_index = int(c_file_data[0]['file_count'] /
                #                                        c_file_data[0]['max'])
                #filename = os.path.basename(fpath)
                #c_file_data[new_index][prefix]=[filename, open(v, 'rb')]
                c_file_data[new_index][prefix] = v
                c_file_data[0]['file_count'] += 1
                c_file_data[0]['chunk_filesize'] += fsize

        elif k == 'poster':
            #self._file_sanity_(v, content_type)
            self._file_sanity_(v, 'plot')
            prefix = prefix + '[poster]'

            #filesize
            fsize = os.path.getsize(v)
            if fsize > c_file_data[0]['post_max_size']:
                message = 'File over maximum permitted size : ' +\
                    human_readable_size(fsize) +\
                    "\nMaximum permitted size : " +\
                    human_readable_size(c_file_data[0]['post_max_size'])
                log.warning(message)
                #if not self.dry_run:
                #    sys.exit(1) #bail
            temp_cumu = c_file_data[0]['chunk_filesize'] + fsize
            log.debug('SIZE ' + str(temp_cumu) +
                      ', CUMU ' + str(c_file_data[0]['chunk_filesize']) +
                      ', MAX ' + str(c_file_data[0]['post_max_size']))
            if c_file_data[0]['file_count'] == c_file_data[0]['max'] \
                or temp_cumu > c_file_data[0]['post_max_size']:
                self._add_break_point_(prefix, c_text_data, c_file_data)
            new_index = c_file_data[0]['index']
            #filesize

            #if not c_file_data[0]['file_count'] % c_file_data[0]['max']:
            #    self._add_break_point_(prefix, c_text_data, c_file_data)
            #new_index = int(c_file_data[0]['file_count'] /
            #                                        c_file_data[0]['max'])
            #filename = os.path.basename(v)
            #c_file_data[new_index][prefix] =[filename, open(v, 'rb')]
            c_file_data[new_index][prefix] = v
            c_file_data[0]['file_count'] += 1
            c_file_data[0]['chunk_filesize'] += fsize

        elif k == 'title':
            #prefix = prefix + '[title]'
            #c_text_data[index][prefix] = v
            c_text_data[index][prefix + '[title]'] = v
            c_file_data[0]['last_title_value'] = v
            c_file_data[0]['last_title_key'] = prefix + '[title]'

        elif k == 'description':
            #prefix = prefix + '[description]'
            #c_text_data[index][prefix] = v
            c_text_data[index][prefix + '[description]'] = v

        elif k == 'encode':
            #prefix = prefix + '[encode]'
            #c_text_data[index][prefix] = v
            c_text_data[index][prefix + '[encode]'] = v

        elif k == 'transcode':
            prefix = prefix + '[encode]'
            c_text_data[index][prefix] = v

        elif k == 'fps':
            #prefix = prefix + '[fps]'
            #c_text_data[index][prefix] = v
            c_text_data[index][prefix + '[fps]'] = v

        else:
            message = "Invalid field found = " + str(k) + " : " + str(v)
            log.warning(message)
            #sys.exit() #bail invalid field is found


    ##########################################################################
    # Splits c_text_data and c_file_data into multiple dictionaries to
    # accomodate max upload file limits imposed by the server
    #
    # c_file_data contains multiple dicts which are used for splitting uploads
    # c_file_data also contains house keeping options which are used to
    # identify remaining items from previous chunks.
    # break_last_title_key + #
    # break_last_title_value + #
    # break_cur_prefix + #
    # Essentially we need to find title from previous chunk to append
    # remaining content
    ##########################################################################
    def _split_content_(self, c_text_data, c_file_data):
        """Splits c_text_data and c_file_data into multiple dictionaries
           to accomodate max upload file limits imposed by the server
        """
        cid = ''
        result = ''

        # extract cid when updating collection
        if self.url[-6:] == 'update':
            u_list = self.url.split("/")
            cid = u_list[-2]

        # capture info and clean up
        # total number of files to be uploaded
        #tf = c_file_data[0]['file_count']
        max_files = c_file_data[0]['max'] # max upload permitted by server
        del c_file_data[0]['chunk_filesize']
        del c_file_data[0]['file_count']
        del c_file_data[0]['global_count']
        del c_file_data[0]['index']
        del c_file_data[0]['last_title_key']
        del c_file_data[0]['last_title_value']
        del c_file_data[0]['max']
        del c_file_data[0]['post_max_size']

        # number of upload chunks = number of dictionaires found in c_file_data
        upload_chunks = len(c_file_data)
        if upload_chunks - 1:
            log.info('Splitting the content into ' + str(upload_chunks) +\
                     ' chunks for upload')

        for n in range(0, upload_chunks):
            if self.dry_run:
                log.info('Validating chunk ' + str(n+1) + ' of ' +\
                          str(upload_chunks))
            else:
                log.info('Uploading chunk ' + str(n+1) + ' of ' +\
                        str(upload_chunks))
            #brk_point = n*max_files
            #filesize
            #fetch break information
            for key, val in list(c_file_data[n].items()): #py3 comp
                if 'break_last_title_key' in key:
                    ltk = val
                    del c_file_data[n][key] #clean
                if 'break_last_title_value' in key:
                    ltv = val
                    del c_file_data[n][key] #clean
                if 'break_cur_prefix' in key:
                    cur_pre = val
                    del c_file_data[n][key] #clean
            #filesize
            if n: # process file data
                """
                # fetch last title key for checking contents in this chunk
                ltk = c_file_data[n]['break_last_title_key' + str(brk_point)]
                # fetch last title value for checking contents in this chunk
                ltv = c_file_data[n]['break_last_title_value' + str(brk_point)]
                # fetch current prefix for checking contents in this chunk
                cur_pre = c_file_data[n]['break_cur_prefix' + str(brk_point)]

                # clean up the following as we already captured them above
                del c_file_data[n]['break_last_title_key' + str(brk_point)]
                del c_file_data[n]['break_last_title_value' + str(brk_point)]
                del c_file_data[n]['break_cur_prefix' + str(brk_point)]
                """

                # If not a clean break
                    # and file exists from previous content type
                    # and corresponding title is not found in c_file_data[n]
                    # then add title key to this c_file_data[n] dict

                #todo amit relaxed file exits criteria above
                #if (not cur_pre == 'clean_break') and \
                #    (cur_pre in list(c_file_data[n].keys())) and \
                #    (not ltk in list(c_text_data[n].keys())): #py3 comp

                if (not cur_pre == 'clean_break') and \
                    ('sequence' in ltk) and \
                    (not ltk in list(c_text_data[n].keys())): #py3 comp
                    # the title key appends at the bottom of our ordered dict
                    # Note: this does not seem to create any problems

                    # todo amit review
                    #borked multi plots without condition ('sequence' in ltk)
                    c_text_data[n][ltk] = ltv

            # update collection when n >0 ie chunk 2 onwards
            #if n: #process text data #amit
                if not self.dry_run:
                    log.info('Attempting to update collection id ' +\
                             str(cid) + ', updates add upto ' +\
                             str(max_files) + ' items at a time')

                # the title key appends at the bottom of our ordered dict
                # Note: this does not seem to create any problems
                c_text_data[n]['username'] = self.username
                c_text_data[n]['apikey'] = self.apikey

                # update url is not set create it
                if not self.url[-6:] == 'update':
                    self.url = self.url + '/' + str(cid) + '/update'

                result = self._do_post_(c_text_data[n], c_file_data[n])

            # chunk 1 when using update
            # when updating an existing collection use 0 index to start
            elif n == 0 and self.url[-6:] == 'update':
                result = self._do_post_(c_text_data[0], c_file_data[0])

            # chunk 1 when creating collection
            else:
                if not self.dry_run:
                    log.info('Attempting to create a new collection')
                result = self._do_post_(c_text_data[0], c_file_data[0])
                cid = self.get_id(result)

        #reset self.url for subsequent calls
        self.url = '' #todo verify this may be not be needed any more
        return result


###############################################################################
# Custom Exceptions
# todo not implemented
###############################################################################
'''
class AuthFileError(Exception):
    pass

class CIDError(Exception):
    pass

class FilepathError(Exception):
    pass

class LogFileError(Exception):
    pass

class PostMethodError(Exception):
    pass

class PrivacyError(Exception):
    pass

class POSTError(Exception):
    pass

class RESTError(Exception):
    pass

class StructureError(Exception):
    pass

class TitleError(Exception):
    pass

class URLError(Exception):
    pass

class UsernameAPIKeyError(Exception):
    pass
'''


###############################################################################
# Utility & Independent functions
##############################################################################
# Escape text input, escape quotation marks, etc
##############################################################################
def _escape_text_(text):
    """Adds escape characters to string"""
    #todo
    return text


###########################################################################
# Extracts collection id from JSON string
###########################################################################
def extract_cid(result):
    """DEPRECATED use get_id(result) method
    Extracts collection id from JSON string
    Returns int or none
    Parameters
    ----------
    result : string in JSON format
    """
    print('extract_cid() method is deprecated. Plese use get_id() method')
    return get_id(result)


###########################################################################
# Extracts status from JSON string
###########################################################################
def extract_status(result):
    """DEPRECATED use get_status(result) method
    Extracts status from JSON string
    Returns success, partial, failure or None
    Parameters
    ----------
    result : string in JSON format
    """
    print('extract_status() method is deprecated. ' +\
          'Please Use get_status() method')
    return get_status(result)


###########################################################################
# Gets collection id from JSON string
###########################################################################
def get_id(result):
    """Extracts collection id from JSON string
    Returns int or none
    Parameters
    ----------
    result : string in JSON format
    """
    try:
        result = json.loads(result) # create dict from string result
        #if web service responds with a list it is an error
        if isinstance(result, list):
            raise ValueError
    except ValueError:
        log.error("Failed to form JSON from result string" + str(result))
        return None

    # Possible responses for status are success, partial or failure
    if result['status'] == 'success':
        #log.info('Succeded: ' + str(result))
        return result['collection_id']
    elif result['status'] == 'partial':
        log.info('Partial: ' + str(result))
        return result['collection_id']
    else:
        log.error('Failed: ' + str(result))
        return None


###########################################################################
# Gets status from JSON string
###########################################################################
def get_status(result):
    """Gets status from JSON string
    Returns success, partial, failure or None
    Parameters
    ----------
    result : string in JSON format
    """
    try:
        result = json.loads(result) # create dict from string result
        #if web service responds with a list it is an error
        if isinstance(result, list):
            raise ValueError
    except ValueError:
        log.error("Failed to form JSON from result string" + str(result))
        return None

    # Possible responses for status are success, partial or failure
    if result['status'] == 'success':
        #log.info('Succeded: ' + str(result))
        return 'success'
    elif result['status'] == 'partial':
        #log.info('Partial: ' + str(result))
        return 'partial'
    elif result['status'] == 'failure':
        #log.error('Failed: ' + str(result))
        return 'failure'
    else:
        return None


###########################################################################
# Gets message from JSON string when partial or failure
# Useful for extracting and printing problem messages
###########################################################################
def get_message(result):
    """Gets message from JSON string when status is partial or failure
    When status is successful None is returned
    Useful for extracting and printing problem messages
    Returns string or None
    Parameters
    ----------
    result : string in JSON format
    """
    try:
        result = json.loads(result) # create dict from string result
        #if web service responds with a list it is an error
        if isinstance(result, list):
            raise ValueError
    except ValueError:
        log.error("Failed to form JSON from result string" + str(result))
        return None

    if result['status'] == 'success':
        return None
    else: #collect all error/message/etc in a buffer string and return
        buf = ''
        if 'error' in result:
            buf += result['error']

        if 'sharing_error' in result:
            buf += ' ' + result['sharing_error']

        if 'file_error' in result:
            buf += ' ' + result['file_error']

        if 'plot_error' in result:
            buf += ' ' + result['plot_error']

        if 'sequence_error' in result:
            buf += ' ' + result['sequence_error']

        if 'video_error' in result:
            buf += ' ' + result['video_error']

        if 'message' in result:
            buf += ' ' + result['message']

        if 'notify_message' in result:
            buf += ' ' + result['notify_message']

        if 'sequence_message' in result:
            buf += ' ' + result['sequence_message']

        return buf


###########################################################################
# Gets collection URL on success or partial success
###########################################################################
def get_url(result):
    """Gets collection URL on success or partial success
    Returns string (url to the collection)
    Parameters
    ----------
    result : string in JSON format
    """
    if get_id(result):
        cid = get_id(result)
        return "https://www.seedme.org/node/" + cid


###############################################################################
# Calculates and returns human readable file size
###############################################################################
def human_readable_size(nbytes):
    """Calculates and returns human readable file size
    Returns string"""
    suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if nbytes == 0:
        return '0 B'

    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    fsize = ('%.4f' % nbytes).rstrip('0').rstrip('.')
    return '%s %s' % (fsize, suffixes[i])

###############################################################################
# Check file existence and access at a path
###############################################################################
def _is_exe_(fpath):
    """Checks file existence and execute permission at a path
    Returns bool
    """
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)


###############################################################################
# Find if an executible exists
###############################################################################
def _which_(program):
    """Finds if an executible exists
    Returns string
    """
    if not program:
        return False

    fpath, fname = os.path.split(program)
    if fpath:
        if _is_exe_(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if _is_exe_(exe_file):
                return exe_file


##############################################################################
# CLI - Uploads content to SeedMe.org in command line mode.
##############################################################################
def main():
    """CLI - Uploads content to SeedMe.org in command line mode."""
    try:
        #uncomment next line if user's system argparse is not compatible
        #raise ImportError
        import argparse
    except ImportError:
        # use backport for python 2.6 or earlier
        import thirdparty.argparse as argparse

    # Following excerpt is not a comment
    shortcuts = """Command Line Shortcuts
.-------------------.------------------.------------------.--------------------.
| Authorization (R) | Privacy/Sharing +| State            | Misc               |
|-------------------|------------------|------------------|--------------------|
| -ap authfile path |-p permission     | -cmd see curl cmd| -ca SSL cert path  |
|  OR               |-e email &        | -CMD auth in -cmd| -cp curl path      |
| -u username       |-n notify users   | -dry dryrun      | -lf log file path  |
| -a apikey         |   with whom      | -h help          | -post curl/requests|
|                   |   collection is  | -o overwrite     | -url alt REST url  |
|                   |   shared         | -s silent        | -v verbosity : INFO|
|                   |                  | -k disable SSL   |      WARNING, ERROR|
|                   |                  | -V see api ver   |     CRITICAL, DEBUG|
.-------------------.------------------.-----------------.---------------------.

.---------------------.-----------------------------.--------------------------.
| Download Collection | Query One Collection        | Query All Collections    |
|---------------------|-----------------------------| -------------------------|
| -dl ID              | -q ID, collection to query  | -q returns id and title  |
|     [all, video,    | -l list content choose one  |    for all collections   |
|     wildcard-string]|    [all, kv, tic, url]      | -kv keyvalue returns     |
|     retry           |    (Requires -q ID option)  |     id and title of      |
|     interval        | -ta tail n items, must be   |     collections where    |
| (Requires first 2)  |     used in conjunction     |     keyvalue is found    |
| -o overwrite local  |     (Requires -l option)    |     (Requires -q option) |
.---------------------.-----------------------------.--------------------------.

.---------------------.-----------------------------.--------------------------.
| Update Collection   | Upload Metadata             |                          |
|---------------------|-----------------------------|--------------------------|
| -up ID, collection  | -c credits ^                |                          |
|         to update   | -d description ^            |                          |
|                     | -kv keyvalue &^             |                          |
|                     | -lic license ^              |                          |
|                     | -t title #^                 |                          |
|                     | -tag text +&                |                          |
.---------------------.-----------------------------.--------------------------.

.---------------------.-----------------------------.--------------------------.
| Upload Ticker +     | Upload File +               | Upload Sequence +        |
|---------------------|-----------------------------|--------------------------|
| -tic ticker &       | -fd file desc ^             | -sd seq desc ^           |
|                     | -fo file overwrite          | -se seq encode           |
|                     | -fp file path (R)           | -so seq overwrite        |
|                     | -ft file title ^            | -sp dir path OR path     |
|                     |                             |     with '*' wildcard (R)|
|                     | Options for videos only     | -spp seq poster path     |
|                     | -fr video rate^             | -sr seq rate/fps         |
|                     | -fe video transcode         | -st seq title #          |
|                     | -fn video dont transcode    |                          |
|                     | -fpp video poster path      |                          |
|                     |                             |                          |
|                     | Upload multiple files       |                          |
|                     | -fp dir path OR path        |                          |
|                     |     with * wildcard (R)     |                          |
|                     | Must omit other options     |                          |
.---------------------.-----------------------------.--------------------------.
 R Required
 + Multiple allowed in collection
 & Multiple allowed in command line
 ^ Overwrites existing
 # Recommended to be set by user
--------------------------------------------------------------------------------
"""

    # Following excerpt is not a comment
    epilog = """
*******************************************************************************
Usage Examples:
You must download your authorization file from SeedMe.org
*******************************************************************************
Create a private collection with title:
% python seedme.py -t 'Test Title'

Note: Here the authorization is read from file stored at default location
      ~/seedme.txt or ~/.seedme

-------------------------------------------------------------------------------

Create collection with title, using authorization file from custom path
% python seedme.py -ap '/custompath/my_auth_file' -t 'My Title'

-------------------------------------------------------------------------------

Create collection with several fields:
% python seedme.py -p 'public' \\
                   -e 'test1@seedme.org' -e 'test2@seedme.org' \\
                   -t 'CLI Test' \\
                   -d 'Using CLI to interact with SeedMe.org' \\
                   -c 'John Doe, University of Alpha Centuri' \\
                   -lic 'CC-BY, Share alike by attribution' \\
                   -kv 'pressure:10pa' -kv 'temperature:300K' \\
                   -tag 'YT' -tag 'visualizations' \\
                   -tic 't1 is 5%' -tic 't2 is 10%' \\
                   -sp 'sample/sequences/plume_boundary/*' \\
                   -st 'seq title' -sd 'desc of seq' -sr 5 -se \\
                   -fp 'sample/videos/air.mp4' \\
                   -ft 'video title' -fd 'desc of video' -fr 1

Notes: -sp option is a dir path, that scans the dir non-recursively and uploads
           all files from there
       -se option will trigger video creation from the uploaded sequence. The
           sequence itself is not automatically deleted from the collection.
       Here authorization info is read from '~/.seedme' or '~/seedme.txt'

==============================================================================

Update title for collection id 666:
 % python seedme.py -ap '~/.seedme' -up 666" -t 'New Title'

Notes: Update collection id -up 666 option is required to update a collection.
       If this is not provided a new collection will be created.

==============================================================================

Notify users with whom we shared collection id 666:
% python seedme.py -up 666 -n

Notes: Recall we added sharing emails to the collection earlier as:
       -e 'test1@seedme.org' -e 'test2@seedme.org'
       Notification is NOT automatic. You decide when share notification should
       be sent

==============================================================================

Add another file to collection id 666:
% python seedme.py -up 666 -fp 'sample/files/doc.pdf'

Note: Here authorization info is read from '~/seedme.txt' or '~/.seedme'

-------------------------------------------------------------------------------

Upload multiple files and create a new collection with title 'Multi upload'
% python seedme.py -t 'Multi upload' -fp 'sample/files'

This will upload all files in sample/files directory (non-recursive)
Notes: When uploading multiple files omit other -f* options
      Here authorization info is read from '~/seedme.txt' or '~/.seedme'

-------------------------------------------------------------------------------

Append an image to sequence titled 'my sequence title' at collection id 666:
% python seedme.py -up 666
                   -st 'my sequence title'
                   -sp 'sample/seqence/steam/steam_rotation0360.png'

Notes: Sequence title -st 'my sequence title' option is required to append to a
       sequence, as we need to identify the sequence where the image should be
       appended. If sequence title is not provided a new sequence is created.

-------------------------------------------------------------------------------

Add another video to collection id 666:
% python seedme.py -up 666 -fp 'sample/videos/quake.mp4'

Note: videos are always transcoded, to skip transcoding add -fn option

==============================================================================

Query to list all your collections
% python seedme.py -q

Add '-tail 5' to restrict the returned items to last 5

Note: Only the collections you own are returned

-------------------------------------------------------------------------------

Query to find collections that match all specified key value pairs

% python seedme.py -q -kv "ssid:expt11"

Add '-tail 5' to restrict the returned items to last 5

Notes: Only the collections you own are searched.
       Key value pair search is not case sensitive

-------------------------------------------------------------------------------

Query to list all contents for a specified collection
% python seedme.py -q 666

Above is same as
% python seedme.py -q 666 -l all

Add '-tail 5' to restrict the returned items to last 5

Notes: Any collections that you own or shared or public can be queried.
       Urls are only listed for public collections
       Query omits sequence information at present (Under development).

-------------------------------------------------------------------------------

Query to list key value pairs for a specified collection
% python seedme.py -q 666 -l kv

Add '-tail 5' to restrict the returned items to last 5

Note: Any collections that you own or shared or public can be queried

-------------------------------------------------------------------------------

Query to list file urls for a specified collection
% python seedme.py -q 666 -l url

Add '-tail 5' to restrict the returned items to last 5

Note: Any collections that you own or shared or public can be queried
      Urls are only listed for public collections
      Query omits sequence information at present (Under development).

-------------------------------------------------------------------------------

Query to list last 5 tickers for a specified collection
% python seedme.py -q 666 -l tic -ta 5

Note: Any collections that you own or shared or public can be queried

==============================================================================

Download all files from a specified collection
% python seedme.py -dl 666 all  "~/Desktop"

Notes: Only public collection content can be downloaded.
       Sequence file download not supported at present (Under development).
       Default download location is ~/Downloads
       By default existing files are incremented not overwritten
       To overwrite add option -o

-------------------------------------------------------------------------------

Download files with wild card string from a specified collection
% python seedme.py -dl 666 *png  "~/Desktop"

Notes: Only public collection content can be downloaded.
       Sequence file download not supported at present (Under development).
       Default download location is ~/Downloads
       By default existing files are incremented not overwritten
       To overwrite add option -o

-------------------------------------------------------------------------------

Download video files from a specified collection
% python seedme.py -dl 666 video "~/Desktop"

Notes: Only public collection content can be downloaded.
       Default download location is ~/Downloads
       By default existing files are incremented not overwritten
       To overwrite add option -o

==============================================================================
"""

    # Start parser
    parser = argparse.ArgumentParser(description='Upload content to SeedMe.org',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=epilog + shortcuts)

    #formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    #formatter_class=argparse.RawDescriptionHelpFormatter,

    #################################################
    # Parse Miscellaneous Settings
    #################################################
    # Overwrite files
    parser.add_argument('-o', '-overwrite',
                        dest='overwrite',
                        action='store_true',
                        help="Overwrite existing files, if any")
    # Api Key
    parser.add_argument('-a', '-apikey',
                        metavar='YOUR_APIKEY',
                        dest='apikey',
                        action='store',
                        help="Specify your apikey at SeedMe.org")
    # Auth
    parser.add_argument('-ap', '-auth_path',
                        metavar='AUTH_FILE_PATH',
                        #default='~/.seedme',
                        dest='auth_file',
                        action='store',
                        help="Specify path to authorization file" +\
                             "\n(default file at ~/seedme.txt or ~/.seedme" +\
                             "\nis searched when this option not specified)" +\
                             "\nThis file must contain the following" +\
                             "\n{\"username\" : \"YourUserName\", " +\
                             "\"apikey\" : \"YourApiKey\"}" +\
                             "\nDownload this file " +\
                             "from https://www.seedme.org/user")
    # SSL cert
    parser.add_argument('-ca', '-cacert',
                        metavar='SSL_CERTIFICATE_PATH',
                        dest='cacert_path',
                        action='store',
                        help="Set path to SSL certificate")
    # SSL off
    parser.add_argument('-k', '-insecure',
                        dest='no_ssl',
                        action='store_true',
                        help="Disable SSL communication")
    # Update
    parser.add_argument('-up', '-update',
                        metavar='COLLECTION_ID',
                        type=int,
                        dest='update_id',
                        action='store',
                        help="Specify collection id for update or query")
    # URL
    parser.add_argument('-url',
                        metavar='URL',
                        dest='url',
                        action='store',
                        help="Overide default and set new webservices url")
    # Username
    parser.add_argument('-u', '-user', '-username',
                        metavar='YOUR_USER_NAME',
                        dest='username',
                        action='store',
                        help="Specify your username at SeedMe.org")
    # Verbosity
    parser.add_argument('-v', '-verbose',
                        choices=['INFO', 'WARNING', 'ERROR', 'CRITICAL',
                                 'DEBUG'],
                        dest='verbose',
                        action='store',
                        help="verbosity level(default: INFO)")
    # Version
    parser.add_argument('-V', '-version',
                        dest='version',
                        action='store_true',
                        help="Show Web API Version and Web Services URL")
    # Post Method
    parser.add_argument('-post',
                        choices=['curl', 'requests'],
                        dest='post_method',
                        action='store',
                        help="Overide post method\n(default: requests)")
    # Curl Path
    parser.add_argument('-cp', '-curl_path',
                        metavar='/usr/bin/curl',
                        dest='curl_path',
                        action='store',
                        help="Specify absolute path to curl executible" +\
                             "\n(default: environment path)")
    # Show Curl Command Line
    parser.add_argument('-cmd', '-show_curl_commands',
                        dest='ccl',
                        action='store_true',
                        help="Show curl command line options")
    # Show Curl Command Line with Auth
    parser.add_argument('-CMD', '-show_auth_in_curl_commands',
                        dest='ccl_auth',
                        action='store_true',
                        help="Show auth in curl command line options")
    # Dry Run Mode
    parser.add_argument('-dry', '-dry_run',
                        dest='dry_run',
                        action='store_true',
                        help="Enable dry run execution mode to check all " +\
                                "\ninput except authorization")
    # Silent Mode
    parser.add_argument('-s', '-silent',
                        dest='silent',
                        action='store_true',
                        help="Silence all console output including errors" +\
                             "\n(Not recommended during collection creation)")
    # Log Mode
    parser.add_argument('-lf', '-logfile',
                        metavar='FILE',
                        dest='logfile',
                        action='store',
                        help="Appends output to specified log file")

    # Query Mode
    parser.add_argument('-q', '-query',
                        metavar='COLLECTION_ID (required with list args)',
                        dest='query',
                        action='store',
                        nargs='?', #use const if one argument not provided
                        type=int,
                        const=True,
                        help="Query your collections with optional ID" +\
                             "\n(Default: Returns a list of ID and Title)")

    # List collection content
    parser.add_argument('-l', '-list',
                        choices=['all', 'keyvalue', 'kv', 'tic', 'ticker',
                                 'url'],
                        dest='query_content',
                        action='store',
                        help="list content for a collection(default: ticker)" +\
                             "Must be used with -query ID option")

    # Tail items
    parser.add_argument('-ta', '-tail',
                        metavar='LAST N ITEMS',
                        dest='tail',
                        type=int,
                        action='store',
                        help="Only list last n items to show. " +\
                             "Must be used in conjunction with -list option")

    # Download Mode
    parser.add_argument('-dl', '-download',
                        metavar=['ID', 'all|video|wildcard', 'DOWNLOAD_PATH', 'RETRY', 'INTERVAL'],
                        dest='download',
                        action='store',
                        nargs='+', # atleast one argument required
                        help="Download content from a collection" +\
                             "\nArguments: ID  all|video|wildcard " +\
                             "DOWNLOAD_PATH RETRY INTERVAL" +\
                             "(Requires first two arguments)" +\
                             "\n(Default DOWNLOAD_PATH: ~/Downloads )" +\
                             "\n(Default RETRY: 3 )" +\
                             "\n(Default INTERVAL: 60)")

    #################################################
    # Parse Meta Data
    #################################################
    # Collection privacy
    parser.add_argument('-p', '-privacy',
                        choices=['private', 'group', 'public'],
                        dest='privacy',
                        action='store',
                        help="Specify privacy to access the collection" +\
                             "\n(default: private)")
    # Sharing email
    parser.add_argument('-e', '-email',
                        metavar='EMAIL',
                        dest='email_list',
                        action='append',
                        help="Add emails to share a collection" +\
                             "\n(can be used multiple times)")

    # Sharing notify
    parser.add_argument('-n', '-notify',
                        dest='notify',
                        action='store_true',
                        help="Send email to users about a shared collection" +\
                             "\n(default: False)")

    # Title
    parser.add_argument('-t', '-title',
                        metavar='STRING',
                        dest='title',
                        action='store',
                        help="Specify title for the collection (recommended)")
    # Description
    parser.add_argument('-d', '-description',
                        metavar='STRING',
                        dest='description',
                        action='store',
                        help="Specify description for the collection")
    # Tag
    parser.add_argument('-tag',
                        metavar='STRING',
                        dest='tag_list',
                        action='append',
                        help="Add tag to the collection" +\
                             "\n(can be used many times)")
    # Key Value pairs
    parser.add_argument('-kv', '-keyvalue',
                        metavar='"KEY:VALUE"',
                        dest='kv_list',
                        action='append',
                        help="Add key:value pairs to the collection" +\
                             "\n(can be used multiple times)")
    # Credits
    parser.add_argument('-c', '-credits',
                        metavar='STRING',
                        dest='credits',
                        action='store',
                        help="Specify credit information for the collection")
    # License
    parser.add_argument('-lic', '-license',
                        metavar='STRING',
                        dest='license',
                        action='store',
                        help="Specify license for the collection")
    '''
    # Expiry (Not yet implemented)
    parser.add_argument('-e', '-expiry',
                        metavar='100',
                        dest='expiry',
                        action='store',
                        help="Specify expiry date or days after creation" +\
                             "\nfor the collection deletion")
    '''

    #################################################
    # Parse ticker
    #################################################
    parser.add_argument('-tic', '-ticker',
                        metavar='STRING',
                        dest='ticker_list',
                        action='append',
                        help="Add ticker text upto 128 char to the collection")

    #################################################
    # Parse File
    #################################################
    parser.add_argument('-fp', '-file_path',
                        metavar='{FILE, PATH/abc*, DIR}',
                        dest='file_path',
                        action='store',
                        help="Specify FILE | PATH with * wildcard | DIR")
    # File Title
    parser.add_argument('-ft', '-file_title',
                        metavar='STRING',
                        dest='file_title',
                        action='store',
                        help="Add file title to the collection")
    # File Description
    parser.add_argument('-fd', '-file_description',
                        metavar='STRING',
                        dest='file_description',
                        action='store',
                        help="Add file description to the collection")
    # File overwrite
    parser.add_argument('-fo', '-file_overwrite',
                        dest='file_overwrite',
                        action='store_true',
                        help="Overwrite file if it exists" +\
                             "\n(default:False)")
    # Video Frame Rate
    parser.add_argument('-fr', '-file_frame_rate',
                        metavar='30.00',
                        dest='file_fps',
                        action='store',
                        help="Specify video frame rate for video transcoding")
    # Video Encoding
    parser.add_argument('-fe', '-file_transcode',
                        dest='file_transcode',
                        action='store_true',
                        help="Trigger video transcoding to create videos" +\
                             "\nfor different devices")
    # Video Don't Transcode
    parser.add_argument('-fn', '-file_dont_encode', '-file_dont_transcode',
                        dest='file_dont_encode',
                        action='store_true',
                        help="Do not trigger video transcoding")
    # Video Poster
    parser.add_argument('-fpp', '-file_poster_path',
                        metavar='{FILE}',
                        dest='file_poster_path',
                        action='store',
                        help="Specify FILE PATH")

    #################################################
    # Parse Plot
    #################################################
    parser.add_argument('-pp', '-plot_path',
                        metavar='{FILE, PATH/abc*, DIR}',
                        dest='plot_path',
                        action='store',
                        help=argparse.SUPPRESS)
                        #help="Specify FILE | PATH with * wildcard | DIR",)
    # Plot Title
    parser.add_argument('-pt', '-plot_title',
                        metavar='STRING',
                        dest='plot_title',
                        action='store',
                        help=argparse.SUPPRESS)
                        #help="Add plot title to the collection")
    # Plot Description
    parser.add_argument('-pd', '-plot_description',
                        metavar='STRING',
                        dest='plot_description',
                        action='store',
                        help=argparse.SUPPRESS)
                        #help="Add plot description to the collection")
    # Plot overwrite
    parser.add_argument('-po', '-plot_overwrite',
                        dest='plot_overwrite',
                        action='store_true',
                        help=argparse.SUPPRESS)
                        #help="Overwrite plot if it exists" +\
                        #     "\n(default:False)")

    #################################################
    # Parse Sequence
    #################################################
    parser.add_argument('-sp', '-sequence_path',
                        metavar='{DIR, PATH/vel*}',
                        dest='sequence_path',
                        action='store',
                        help="Specify DIR | PATH with * wildcard")
    # Sequence Poster
    parser.add_argument('-spp', '-sequence_poster_path',
                        metavar='{FILE}',
                        dest='sequence_poster_path',
                        action='store',
                        help="Specify FILE PATH")
    # Sequence Title
    parser.add_argument('-st', '-sequence_title',
                        metavar='STRING',
                        dest='sequence_title',
                        action='store',
                        help="Add sequence title to the collection" +\
                             "\n(strongly recommended)")
    # Sequence Description
    parser.add_argument('-sd', '-sequence_description',
                        metavar='STRING',
                        dest='sequence_description',
                        action='store',
                        help="Add sequence description to the collection")
    # Sequence Frame Rate
    parser.add_argument('-sr', '-sequence_frame_rate',
                        metavar='30.00',
                        dest='sequence_fps',
                        action='store',
                        help="Specify sequence frame rate for video encoding")
    # Sequence Encoding
    parser.add_argument('-se', '-sequence_encode',
                        dest='sequence_encode',
                        action='store_true',
                        help="Trigger video encoding to create a video" +\
                             "\nfrom image sequence")
    # Sequence Overwrite
    parser.add_argument('-so', '-sequence_overwrite',
                        dest='sequence_overwrite',
                        action='store_true',
                        help="Overwrite sequence if it exists" +\
                             "\n(default:False)")

    #################################################
    # Parse Video
    #################################################
    parser.add_argument('-vp', '-video_path',
                        metavar='{FILE, PATH/abc*, DIR}',
                        dest='video_path',
                        action='store',
                        help=argparse.SUPPRESS)
                        #help="Specify FILE | PATH with * wildcard | DIR")
    # Video Poster
    parser.add_argument('-vpp', '-video_poster_path',
                        metavar='{FILE}',
                        dest='video_poster_path',
                        action='store',
                        help=argparse.SUPPRESS)
                        #help="Specify FILE PATH")
    # Video Title
    parser.add_argument('-vt', '-video_title',
                        metavar='STRING',
                        dest='video_title',
                        action='store',
                        help=argparse.SUPPRESS)
                        #help="Add video title to the collection")
    # Video Description
    parser.add_argument('-vd', '-video_description',
                        metavar='STRING',
                        dest='video_description',
                        action='store',
                        help=argparse.SUPPRESS)
                        #help="Add video description to the collection")
    # Video Frame Rate
    parser.add_argument('-vr', '-video_frame_rate',
                        metavar='30.00',
                        dest='video_fps',
                        action='store',
                        #help="Specify video frame rate for video transcoding")
                        help=argparse.SUPPRESS)
    # Video Encoding
    parser.add_argument('-ve', '-video_transcode',
                        dest='video_transcode',
                        action='store_true',
                        help=argparse.SUPPRESS)
                        #help="Trigger video transcoding to create videos" +\
                        #     "\nfor different devices")
    # Video Don't Transcode
    parser.add_argument('-vn', '-video_dont_encode', '-video_dont_transcode',
                        dest='video_dont_encode',
                        action='store_true',
                        help=argparse.SUPPRESS)
                        #help="Do not trigger video transcoding")
    # Video Overwrite
    parser.add_argument('-vo', '-video_overwrite',
                        dest='video_overwrite',
                        action='store_true',
                        help=argparse.SUPPRESS)
                        #help="Overwrite video if it exists" +\
                        #     "\n(default:False)")


    # Sort arguments in alphabetic order in help
    #http://stackoverflow.com/questions/12268602/
                        #sort-argparse-help-alphabetically
    for grp in parser._action_groups:
        grp._group_actions.sort(key=lambda x: x.dest)

    # Finish parsing and collect all parsed items
    args = parser.parse_args()


    #################################################
    # Prepare input for calling SeedMe module methods
    #################################################
    # Collect emails as space separated string
    emails = ''
    if args.email_list:
        emails = ' '.join(args.email_list)

    # Notificaton check
    notify = False
    if args.notify:
        notify = True

    # Create key value dictionary from list
    keyvalue_dict = OrderedDict()
    if args.kv_list:
        for item in args.kv_list:
            try:
                key, val = item.split(':', 1) #split on first colon occurrence
                keyvalue_dict[key] = val
            except ValueError:
                print('ERROR: Key-value must be a colon delimited string' +\
                      ' e.g. "han:solo"')
                sys.exit(1) #bail

    # Collect file options in a dict
    file_dict = dict()
    if args.file_path:
        file_dict['filepath'] = args.file_path
    if args.file_title:
        file_dict['title'] = args.file_title
    if args.file_description:
        file_dict['description'] = args.file_description

    # handle video fields
    if args.file_poster_path:
        file_dict['poster'] = args.file_poster_path
    if args.file_fps:
        file_dict['fps'] = args.file_fps
    if args.file_transcode:
        file_dict['encode'] = True
    if args.file_dont_encode:
        file_dict['encode'] = False

    # Collect plot options in a dict
    plot_dict = dict()
    if args.plot_path:
        print("\n*************************************************\n" +\
              "WARNING: Plot specific options are now deprecated\n" +\
              "Please use File options instead\n" +\
              "*************************************************\n")
        plot_dict['filepath'] = args.plot_path
    if args.plot_title:
        plot_dict['title'] = args.plot_title
    if args.plot_description:
        plot_dict['description'] = args.plot_description

    # Collect sequence options in a dict
    sequence_dict = dict()
    if args.sequence_path:
        sequence_dict['filepath'] = args.sequence_path
    if args.sequence_poster_path:
        sequence_dict['poster'] = args.sequence_poster_path
    if args.sequence_title:
        sequence_dict['title'] = args.sequence_title
    if args.sequence_description:
        sequence_dict['description'] = args.sequence_description
    if args.sequence_fps:
        sequence_dict['fps'] = args.sequence_fps
    if args.sequence_encode:
        sequence_dict['encode'] = True

    # Collect video options in a dict
    video_dict = dict()
    if args.video_path:
        print("\n*************************************************\n" +\
              "WARNING: Video specific options are now deprecated\n" +\
              "Please use File options instead\n" +\
              "*************************************************\n")
        video_dict['filepath'] = args.video_path
        if not args.video_dont_encode:
            video_dict['encode'] = True

    if args.video_poster_path:
        video_dict['poster'] = args.video_poster_path

    if args.video_title:
        video_dict['title'] = args.video_title
        if not args.video_dont_encode:
            video_dict['encode'] = True

    if args.video_description:
        video_dict['description'] = args.video_description
    if args.video_fps:
        video_dict['fps'] = args.video_fps
    if args.video_transcode:
        video_dict['encode'] = True
    if args.video_dont_encode:
        video_dict['encode'] = False

    # Collect overwrite options
    overwrite_dict = dict()
    if args.overwrite: # global overwrite
        overwrite_dict['all_types'] = True
    if args.file_overwrite and not args.overwrite: # file overwrite
        overwrite_dict['files'] = True
    if args.plot_overwrite and not args.overwrite: # plot overwrite
        overwrite_dict['plots'] = True
    if args.sequence_overwrite and not args.overwrite: # sequence overwrite
        overwrite_dict['sequences'] = True
    if args.video_overwrite and not args.overwrite: # video overwrite
        overwrite_dict['videos'] = True

    # process query options
    if args.query_content:
        # expand shortcut for 'tic' to 'ticker'
        if args.query_content == 'tic':
            args.query_content = 'ticker'

        # expand shortcut for 'kv' to 'keyvalue'
        if args.query_content == 'kv':
            args.query_content = 'keyvalue'

    # process download options
    if args.download:

        if len(args.download) < 2:
            print('ERROR: Download requires atleast two arguments as:')
            print('ID and one of "all" or "video" or wildcard-string')
            sys.exit(1) #bail

        down_id = args.download[0]

        if args.download[1]:
            down_content = args.download[1]
        else:
            print('ERROR: Download content not provided')
            sys.exit(1) #bail

        down_path = None
        if len(args.download) > 2:
            down_path = args.download[2]

        retry = 3
        if len(args.download) > 4:
            retry = args.download[3]

        interval = 60
        if len(args.download) > 4:
            interval = args.download[4]

    #################################################
    # Set Properties
    #################################################
    # Create SeedMe class object
    seedme = SeedMe()

    # Set Verbosity
    if args.verbose:
        seedme.set_log_level(args.verbose)

    # Set console log
    if args.silent:
        seedme.set_console_log(False)

    # Set Dry Run (Always set this after console log)
    if args.dry_run:
        seedme.set_dry_run()

    # Set SSL certificate path
    if args.cacert_path:
        seedme.set_ssl_cert(args.cacert_path)

    # Disable SSL
    if args.no_ssl:
        seedme.set_ssl(False)

    # Ask Version
    if args.version:
        seedme.version()

    # Set file log
    if args.logfile:
        seedme.set_file_log(True, args.logfile)

    # show python version that is being used
    log.debug("The Python version is %s.%s.%s" % sys.version_info[:3])

    # Set authorization when specified
    # Default auth file at ~/.seedme and ~/seedme.txt is automatically
    # checked when nothing set by user
    if args.username or args.apikey:
        seedme.set_auth_via_string(args.username, args.apikey)
    else:
        if args.auth_file: #if provided by user
            seedme.set_auth_via_file(args.auth_file)

    # Set Web Services URL
    if args.url:
        seedme.set_base_url(args.url)

    # Set Curl Path when not default
    if args.curl_path:
        seedme.set_curl_path(args.curl_path)

    # Set Post Method
    if args.post_method:
        seedme.set_post_method(args.post_method)

    # Show Curl Command Line
    if args.ccl:
        seedme.show_curl_commands()

    # Show Curl Command Line with Auth
    if args.ccl_auth:
        seedme.show_auth_in_curl_commands()

    #################################################
    # Call functions
    #################################################
    num_args = len(sys.argv) - 1
    if num_args and not args.update_id and not args.query and not args.download:
        seedme.create_collection(privacy=args.privacy,
                                 sharing=emails,
                                 notify=notify,
                                 title=args.title,
                                 description=args.description,
                                 overwrite=overwrite_dict,
                                 credits=args.credits,
                                 license=args.license,
                                 keyvalues=keyvalue_dict,
                                 tags=args.tag_list,
                                 tickers=args.ticker_list,
                                 files=file_dict,
                                 plots=plot_dict,
                                 sequences=sequence_dict,
                                 videos=video_dict
                                )
    elif args.update_id and not args.query and not args.download:
        seedme.update_collection(args.update_id,
                                 privacy=args.privacy,
                                 sharing=emails,
                                 notify=notify,
                                 title=args.title,
                                 description=args.description,
                                 overwrite=overwrite_dict,
                                 credits=args.credits,
                                 license=args.license,
                                 keyvalues=keyvalue_dict,
                                 tags=args.tag_list,
                                 tickers=args.ticker_list,
                                 files=file_dict,
                                 plots=plot_dict,
                                 sequences=sequence_dict,
                                 videos=video_dict
                                )
    elif args.query and not args.download:
        if isinstance(args.query, bool): #query all collections
            seedme.query(keyvalues=keyvalue_dict,
                         tail=args.tail,
                        )
        else: # query specified collection ID
            if args.query < 0:
                print ("Error: Query ID should be > 1")
                sys.exit(1) #bail

            seedme.query(qid=args.query,
                         content=args.query_content,
                         tail=args.tail,
                        )
    elif args.download:
        seedme.download(down_id,
                        content=down_content,
                        path=down_path,
                        retry=retry,
                        interval=interval,
                        overwrite=args.overwrite
                       )
    else:
        parser.print_help()



#################################################
# Run in command line mode
#################################################
if __name__ == '__main__':
    main()
