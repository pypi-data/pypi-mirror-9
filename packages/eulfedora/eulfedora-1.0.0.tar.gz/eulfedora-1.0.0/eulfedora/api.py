# file eulfedora/api.py
#
#   Copyright 2010,2011 Emory University Libraries
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import csv
import logging
from urlparse import urljoin
import warnings
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor, \
    user_agent
from StringIO import StringIO
import time

from eulfedora import __version__ as eulfedora_version
from eulfedora.util import datetime_to_fedoratime, \
    RequestFailed, ChecksumMismatch, PermissionDenied, parse_rdf

logger = logging.getLogger(__name__)

# low-level wrappers

def _safe_str(s):
    # helper for _safe_urlencode: utf-8 encode unicode strings, convert
    # non-strings to strings, and leave plain strings untouched.
    if isinstance(s, unicode):
        return s.encode('utf-8')
    else:
        return str(s)

def _get_items(query, doseq):
    # helper for _safe_urlencode: emulate urllib.urlencode "doseq" logic
    if hasattr(query, 'items'):
        query = query.items()
    for k, v in query:
        if isinstance(v, basestring):
            yield k, v
        elif doseq and iter(v): # if it's iterable
            for e in v:
                yield k, e
        else:
            yield k, str(v)

_sessions = {}

class HTTP_API_Base(object):
    def __init__(self, base_url, username=None, password=None):
        # standardize url format; ensure we have a trailing slash,
        # adding one if necessary
        if not base_url.endswith('/'):
            base_url = base_url + '/'

        # TODO: can we re-use sessions safely across instances?
        global _sessions

        # check for an existing session for this fedora
        if base_url in _sessions:
            self.session = _sessions[base_url]
        else:
            # create a new session and add to global sessions
            self.session = requests.Session()
            # Set headers to be passed with every request
            # NOTE: only headers that will be common for *all* requests
            # to this fedora should be set in the session
            # (i.e., do NOT include auth information here)
            self.session.headers = {
                'User-Agent': user_agent('eulfedora', eulfedora_version),
                # 'user-agent': 'eulfedora/%s (python-requests/%s)' % \
                    # (eulfedora_version, requests.__version__),
                'verify': True,  # verify SSL certs by default
            }

            _sessions[base_url] = self.session

        self.base_url = base_url
        self.username = username
        self.password = password
        self.request_options = {}
        if self.username is not None:
            # store basic auth option to pass when making requests
            self.request_options['auth'] = (self.username, self.password)

    def absurl(self, rel_url):
        return urljoin(self.base_url, rel_url)

    def prep_url(self, url):
        return self.absurl(url)

    # thinnest possible wrappers around requests calls
    # - add auth, make urls absolute

    def _make_request(self, reqmeth, url, *args, **kwargs):
        # copy base request options and update with any keyword args
        rqst_options = self.request_options.copy()
        rqst_options.update(kwargs)
        start = time.time()
        response = reqmeth(self.prep_url(url), *args, **rqst_options)
        logger.debug('%s %s=>%d: %f sec' % (reqmeth.__name__.upper(), url,
            response.status_code, time.time() - start))


        # FIXME: handle 3xx (?) [possibly handled for us by requests]
        if response.status_code >= requests.codes.bad:  # 400 or worse
            # separate out 401 and 403 (permission errors) to enable
            # special handling in client code.
            if response.status_code in (requests.codes.unauthorized,
                                        requests.codes.forbidden):
                raise PermissionDenied(response)
            elif response.status_code == requests.codes.server_error:
                # check response content to determine if this is a
                # ChecksumMismatch or a more generic error
                if 'ValidationException: Checksum Mismatch' in response.content:
                    raise ChecksumMismatch(response)
                else:
                    raise RequestFailed(response)
            else:
                raise RequestFailed(response)

        return response

    def get(self, *args, **kwargs):
        return self._make_request(self.session.get, *args, **kwargs)

    def put(self, *args, **kwargs):
        return self._make_request(self.session.put, *args, **kwargs)

    def post(self, *args, **kwargs):
        return self._make_request(self.session.post, *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self._make_request(self.session.delete, *args, **kwargs)

    # also available: head, patch


class REST_API(HTTP_API_Base):
    """
       Python object for accessing `Fedora's REST API <http://fedora-commons.org/confluence/display/FCR30/REST+API>`_.
    """

    # always return xml response instead of html version
    format_xml = { 'format' : 'xml'}

    ### API-A methods (access) ####
    # describeRepository not implemented in REST, use API-A-LITE version

    def findObjects(self, query=None, terms=None, pid=True, chunksize=None, session_token=None):
        """
        Wrapper function for `Fedora REST API findObjects <http://fedora-commons.org/confluence/display/FCR30/REST+API#RESTAPI-findObjects>`_
        and `Fedora REST API resumeFindObjects <http://fedora-commons.org/confluence/display/FCR30/REST+API#RESTAPI-resumeFindObjects>`_

        One and only one of query or terms must be specified.

        :param query: string of fields and terms to search for
        :param terms: phrase search across all fields
        :param pid: include pid in search results
        :param chunksize: number of objects to return at a time
        :param session_token: get an additional chunk of results from a prior search
        :param parse: optional data parser function; defaults to returning
                      raw string data
        :rtype: string
        """
        if query is not None and terms is not None:
            raise Exception("Cannot findObject with both query ('%s') and terms ('%s')" % (query, terms))

        http_args = {'resultFormat': 'xml'}
        if query is not None:
            http_args['query'] = query
        if terms is not None:
            http_args['terms'] = terms

        if pid:
            http_args['pid'] = 'true'
        if session_token:
            http_args['sessionToken'] = session_token
        if chunksize:
            http_args['maxResults'] = chunksize
        return self.get('objects', params=http_args)

    def getDatastreamDissemination(self, pid, dsID, asOfDateTime=None, stream=False):
        """Get a single datastream on a Fedora object; optionally, get the version
        as of a particular date time.

        :param pid: object pid
        :param dsID: datastream id
        :param asOfDateTime: optional datetime; ``must`` be a non-naive datetime
            so it can be converted to a date-time format Fedora can understand
        """
        # TODO: Note that this loads the entire datastream content into
        # memory as a Python string. This will suck for very large
        # datastreams. Eventually we need to either modify this function or
        # else add another to return self.open(), allowing users to stream
        # the result in a with block.

        # /objects/{pid}/datastreams/{dsID}/content ? [asOfDateTime] [download]
        http_args = {}
        if asOfDateTime:
            http_args['asOfDateTime'] = datetime_to_fedoratime(asOfDateTime)
        url = 'objects/%(pid)s/datastreams/%(dsid)s/content' %  \
            {'pid': pid, 'dsid': dsID}
        return self.get(url, params=http_args, stream=stream)

    # NOTE: getDissemination was not available in REST API until Fedora 3.3
    def getDissemination(self, pid, sdefPid, method, method_params={}, return_http_response=False):
        # /objects/{pid}/methods/{sdefPid}/{method} ? [method parameters]
        uri = 'objects/%(pid)s/methods/%(sdefpid)s/%(method)s' % \
            {'pid': pid, 'sdefpid': sdefPid, 'method': method}
        return self.get(uri, params=method_params)

    def getObjectHistory(self, pid):
        # /objects/{pid}/versions ? [format]
        return self.get('objects/%(pid)s/versions' % {'pid': pid},
                        params=self.format_xml)

    def getObjectProfile(self, pid, asOfDateTime=None):
        """Get top-level information aboug a single Fedora object; optionally,
        retrieve information as of a particular date-time.

        :param pid: object pid
        :param asOfDateTime: optional datetime; ``must`` be a non-naive datetime
        so it can be converted to a date-time format Fedora can understand
        """
        # /objects/{pid} ? [format] [asOfDateTime]
        http_args = {}
        if asOfDateTime:
            http_args['asOfDateTime'] = datetime_to_fedoratime(asOfDateTime)
        http_args.update(self.format_xml)
        url = 'objects/%(pid)s' % {'pid': pid}
        return self.get(url, params=http_args)

    def listDatastreams(self, pid):
        """
        Get a list of all datastreams for a specified object.

        Wrapper function for `Fedora REST API listDatastreams <http://fedora-commons.org/confluence/display/FCR30/REST+API#RESTAPI-listDatastreams>`_

        :param pid: string object pid
        :param parse: optional data parser function; defaults to returning
                      raw string data
        :rtype: string xml data
        """
        # /objects/{pid}/datastreams ? [format, datetime]
        return self.get('objects/%(pid)s/datastreams' % {'pid': pid},
                        params=self.format_xml)

    def listMethods(self, pid, sdefpid=None):
        # /objects/{pid}/methods ? [format, datetime]
        # /objects/{pid}/methods/{sdefpid} ? [format, datetime]

        ## NOTE: getting an error when sdefpid is specified; fedora issue?

        uri = 'objects/%(pid)s/methods' % {'pid': pid}
        if sdefpid:
            uri += '/' + sdefpid
        return self.get(uri, params=self.format_xml)

    ### API-M methods (management) ####

    def addDatastream(self, pid, dsID, dsLabel=None,  mimeType=None, logMessage=None,
        controlGroup=None, dsLocation=None, altIDs=None, versionable=None,
        dsState=None, formatURI=None, checksumType=None, checksum=None, content=None):
        # objects/{pid}/datastreams/NEWDS? [opts]
        # content via multipart file in request content, or dsLocation=URI
        # one of dsLocation or filename must be specified

        # if checksum is sent without checksum type, Fedora seems to
        # ignore it (does not error on invalid checksum with no checksum type)
        if checksum is not None and checksumType is None:
            warnings.warn('Fedora will ignore the checksum (%s) because no checksum type is specified' \
                          % checksum)

        http_args = {'dsLabel': dsLabel, 'mimeType': mimeType}
        if logMessage:
            http_args['logMessage'] = logMessage
        if controlGroup:
            http_args['controlGroup'] = controlGroup
        if dsLocation:
            http_args['dsLocation'] = dsLocation
        if altIDs:
            http_args['altIDs'] = altIDs
        if versionable is not None:
            http_args['versionable'] = versionable
        if dsState:
            http_args['dsState'] = dsState
        if formatURI:
            http_args['formatURI'] = formatURI
        if checksumType:
            http_args['checksumType'] = checksumType
        if checksum:
            http_args['checksum'] = checksum


        # Added code to match how content is now handled, see modifyDatastream.
        extra_args = {}
        # could be a string or a file-like object
        if content:
            if hasattr(content, 'read'):    # if content is a file-like object, warn if no checksum
                if not checksum:
                    logging.warning("File was ingested into fedora without a passed checksum for validation, pid was: %s and dsID was: %s." % (pid, dsID))

                extra_args['files'] = {'file': content}

                # m = MultipartEncoder(fields={'file': content})
                # extra_args.update({
                #     'data': m,
                #     'headers': {'Content-Type': m.content_type}
                # })

            else:
                extra_args['data'] = content
                # extra_args['data']
                # extra_args['files'] = StringIO(content)

            # set content-type header ?

        url = 'objects/%s/datastreams/%s' % (pid, dsID)
        return self.post(url, params=http_args, **extra_args)
        # expected response: 201 Created (on success)
        # when pid is invalid, response body contains error message
        #  e.g., no path in db registry for [bogus:pid]
        # return success/failure and any additional information
        # return (r.status_code == requests.codes.created, r.content)

    def addRelationship(self, pid, subject, predicate, object, isLiteral=False,
                        datatype=None):
        """
        Wrapper function for `Fedora REST API addRelationsphi <https://wiki.duraspace.org/display/FEDORA34/REST+API#RESTAPI-addRelationship>`_

        :param pid: persistent id for the object to add the new relationship to
        :param subject: subject of the relationship; object or datastream URI
        :param predicate: predicate of the new relationship
        :param object: object of the relationship
        :param isLiteral: true if object is literal, false if it is a URI;
            Fedora has no default; this method defaults to False
        :param datatype: optional datatype for literal objects

        :returns: boolean success
        """

        http_args = {'subject': subject, 'predicate': predicate,
                     'object': object, 'isLiteral': isLiteral}
        if datatype is not None:
            http_args['datatype'] = datatype

        url = 'objects/%(pid)s/relationships/new' % {'pid': pid}
        r = self.post(url, params=http_args)
        return r.status_code == requests.codes.ok

    def compareDatastreamChecksum(self, pid, dsID, asOfDateTime=None): # date time
        # special case of getDatastream, with validateChecksum = true
        # currently returns datastream info returned by getDatastream...  what should it return?
        return self.getDatastream(pid, dsID, validateChecksum=True, asOfDateTime=asOfDateTime)

    def export(self, pid, context=None, format=None, encoding=None):
        # /objects/{pid}/export ? [format] [context] [encoding]
        # - if format is not specified, use fedora default (FOXML 1.1)
        # - if encoding is not specified, use fedora default (UTF-8)
        # - context should be one of: public, migrate, archive (default is public)
        http_args = {}
        if context:
            http_args['context'] = context
        if format:
            http_args['format'] = format
        if encoding:
            http_args['encoding'] = encoding
        uri = 'objects/%s/export' % pid
        return self.get(uri, params=http_args)

    def getDatastream(self, pid, dsID, asOfDateTime=None, validateChecksum=False):
        """Get information about a single datastream on a Fedora object; optionally,
        get information for the version of the datastream as of a particular date time.

        :param pid: object pid
        :param dsID: datastream id
        :param asOfDateTime: optional datetime; ``must`` be a non-naive datetime
        so it can be converted to a date-time format Fedora can understand
        """
        # /objects/{pid}/datastreams/{dsID} ? [asOfDateTime] [format] [validateChecksum]
        http_args = {}
        if validateChecksum:
            # fedora only responds to lower-case validateChecksum option
            http_args['validateChecksum'] = str(validateChecksum).lower()
        if asOfDateTime:
            http_args['asOfDateTime'] = datetime_to_fedoratime(asOfDateTime)
        http_args.update(self.format_xml)
        uri = 'objects/%(pid)s/datastreams/%(dsid)s' % {'pid': pid, 'dsid': dsID}
        return self.get(uri, params=http_args)

    def getDatastreamHistory(self, pid, dsid, format=None):
        http_args = {}
        if format is not None:
            http_args['format'] = format
        # Fedora docs say the url should be:
        #   /objects/{pid}/datastreams/{dsid}/versions
        # In Fedora 3.4.3, that 404s but /history does not
        uri = 'objects/%(pid)s/datastreams/%(dsid)s/history' % \
            {'pid': pid, 'dsid': dsid}
        return self.get(uri, params=http_args)

    # getDatastreams not implemented in REST API

    def getNextPID(self, numPIDs=None, namespace=None):
        """
        Wrapper function for `Fedora REST API getNextPid <http://fedora-commons.org/confluence/display/FCR30/REST+API#RESTAPI-getNextPID>`_

        :param numPIDs: (optional) get the specified number of pids; by default, returns 1
        :param namespace: (optional) get the next pid in the specified pid namespace;
            otherwise, Fedora will return the next pid in the configured default namespace.
        :rtype: string (if only 1 pid requested) or list of strings (multiple pids)
        """
        http_args = { 'format': 'xml' }
        if numPIDs:
            http_args['numPIDs'] = numPIDs
        if namespace:
            http_args['namespace'] = namespace

        rel_url = 'objects/nextPID'
        return self.post(rel_url, params=http_args)

    def getObjectXML(self, pid):
        """
           Return the entire xml for the specified object.

           :param pid: pid of the object to retrieve
           :param parse: optional data parser function; defaults to returning
                         raw string data
           :rtype: string xml content of entire object
        """
        # /objects/{pid}/objectXML
        return self.get('objects/%(pid)s/objectXML' % {'pid': pid})

    def getRelationships(self, pid, subject=None, predicate=None, format=None):
        '''
        Get information about relationships on an object.

        Wrapper function for `Fedora REST API getRelationships <https://wiki.duraspace.org/display/FEDORA34/REST+API#RESTAPI-getRelationships>`_

        '''
        http_args = {}
        if subject is not None:
            http_args['subject'] = subject
        if predicate is not None:
            http_args['predicate'] = predicate
        if format is not None:
            http_args['format'] = format

        url = 'objects/%(pid)s/relationships' % {'pid': pid}
        return self.get(url, params=http_args)

    def ingest(self, text, logMessage=None):
        """
        Ingest a new object into Fedora. Returns the pid of the new object on success.

        Wrapper function for `Fedora REST API ingest <http://fedora-commons.org/confluence/display/FCR30/REST+API#RESTAPI-ingest>`_

        :param text: full text content of the object to be ingested
        :param logMessage: optional log message
        :rtype: string
        """

        # FIXME/TODO: add options for ingest with pid, values for label/format/namespace/ownerId, etc?
        http_args = {}
        if logMessage:
            http_args['logMessage'] = logMessage

        headers = {'Content-Type': 'text/xml'}

        url = 'objects/new'
        return self.post(url, data=text, params=http_args, headers=headers)
        # FIXME: check response status code first?
        # return r.content  # content is new pid

    def modifyDatastream(self, pid, dsID, dsLabel=None, mimeType=None, logMessage=None, dsLocation=None,
        altIDs=None, versionable=None, dsState=None, formatURI=None, checksumType=None,
        checksum=None, content=None, force=False):
        # /objects/{pid}/datastreams/{dsID} ? [dsLocation] [altIDs] [dsLabel] [versionable] [dsState] [formatURI] [checksumType] [checksum] [mimeType] [logMessage] [force] [ignoreContent]
        # NOTE: not implementing ignoreContent (unneeded)

        # content via multipart file in request content, or dsLocation=URI
        # if dsLocation or content is not specified, datastream content will not be updated
        # content can be string or a file-like object

        # Unlike addDatastream, if checksum is sent without checksum
        # type, Fedora honors it (*does* error on invalid checksum
        # with no checksum type) - it seems to use the existing
        # checksum type if a new type is not specified.

        http_args = {}
        if dsLabel:
            http_args['dsLabel'] = dsLabel
        if mimeType:
            http_args['mimeType'] = mimeType
        if logMessage:
            http_args['logMessage'] = logMessage
        if dsLocation:
            http_args['dsLocation'] = dsLocation
        if altIDs:
            http_args['altIDs'] = altIDs
        if versionable is not None:
            http_args['versionable'] = versionable
        if dsState:
            http_args['dsState'] = dsState
        if formatURI:
            http_args['formatURI'] = formatURI
        if checksumType:
            http_args['checksumType'] = checksumType
        if checksum:
            http_args['checksum'] = checksum
        if force:
            http_args['force'] = force

        content_args = {}
        if content:
            # content can be either a string or a file-like object
            if hasattr(content, 'read'):    # allow content to be a file
                # warn about missing checksums for files
                if not checksum:
                    logging.warning("Updating datastream %s/%s with a file, but no checksum passed" \
                                    % (pid, dsID))

            # either way (string or file-like object), set content as request data
            # (file-like objects supported in requests as of 0.13.1)
            content_args['data'] = content

        url = 'objects/%s/datastreams/%s' % (pid, dsID)
        return self.put(url, params=http_args, **content_args)
        # expected response: 200 (success)
        # response body contains error message, if any
        # return success/failure and any additional information
        # return r.content
        # return (r.status_code == requests.codes.ok, r.content)

    def modifyObject(self, pid, label, ownerId, state, logMessage=None):
        # /objects/{pid} ? [label] [ownerId] [state] [logMessage]
        http_args = {'label' : label,
                    'ownerId' : ownerId,
                    'state' : state}
        if logMessage is not None:
            http_args['logMessage'] = logMessage
        url = 'objects/%(pid)s' % {'pid': pid}
        return self.put(url, params=http_args)
        # returns response code 200 on success
        # return r.status_code == requests.codes.ok

    def purgeDatastream(self, pid, dsID, startDT=None, endDT=None, logMessage=None,
            force=False):
        """
        Purge a datastream, or versions of a dastream, from a Fedora object.

        :param pid: object pid
        :param dsID: datastream ID
        :param startDT: optional start datetime (when purging certain versions)
        :param endDT: optional end datetime (when purging certain versions)
        :param logMessage: optional log message
        :returns: tuple of success/failure and response content; on success,
            response content is a list of timestamps for the datastream purged;
            on failure, response content may contain an error message
        """
        # /objects/{pid}/datastreams/{dsID} ? [startDT] [endDT] [logMessage] [force]
        http_args = {}
        if logMessage:
            http_args['logMessage'] = logMessage
        if startDT:
            http_args['startDT'] = startDT
        if endDT:
            http_args['endDT'] = endDT
        if force:
            http_args['force'] = force

        url = 'objects/%(pid)s/datastreams/%(dsid)s' % {'pid': pid, 'dsid': dsID}
        return self.delete(url, params=http_args)

            # as of Fedora 3.4, returns 200 on success with a list of the
            # timestamps for the versions deleted as response content
            # NOTE: response content may be useful on error, e.g.
            #       no path in db registry for [bogus:pid]
            # is there any useful way to pass this info back?
            # *NOTE*: bug when purging non-existent datastream on a valid pid
            # - reported here: http://www.fedora-commons.org/jira/browse/FCREPO-690
            # - as a possible work-around, could return false when status = 200
            #   but response body is an empty list (i.e., no datastreams/versions purged)

            # NOTE: previously returned this
            # return r.status_code == 200, response.read()

    def purgeObject(self, pid, logMessage=None):
        """
        Purge an object from Fedora.

        Wrapper function for `REST API purgeObject <http://fedora-commons.org/confluence/display/FCR30/REST+API#RESTAPI-purgeObject>`_

        :param pid: pid of the object to be purged
        :param logMessage: optional log message
        """
        # FIXME: return success/failure?
        http_args = {}
        if logMessage:
            http_args['logMessage'] = logMessage

        url = 'objects/%(pid)s' % {'pid': pid}
        return self.delete(url, params=http_args)
        # as of Fedora 3.4, returns 200 on success; response content is timestamp
        # return response.status == requests.codes.ok, response.content

    def purgeRelationship(self, pid, subject, predicate, object, isLiteral=False,
                        datatype=None):
        '''
        Remove a relationship from an object.

        Wrapper function for `Fedora REST API purgeRelationship <https://wiki.duraspace.org/display/FEDORA34/REST+API#RESTAPI-purgeRelationship>`_

        :returns: boolean; indicates whether or not a relationship was
            removed

        '''

        http_args = {'subject': subject, 'predicate': predicate,
                     'object': object, 'isLiteral': isLiteral}
        if datatype is not None:
            http_args['datatype'] = datatype

        url = 'objects/%(pid)s/relationships' % {'pid': pid}
        r = self.delete(url, params=http_args)
        # should have a status code of 200;
        # response body text indicates if a relationship was purged or not
        return r.status_code == requests.codes.ok and r.content == 'true'

    def setDatastreamState(self, pid, dsID, dsState):
        # /objects/{pid}/datastreams/{dsID} ? [dsState]
        http_args = {'dsState' : dsState}
        url = 'objects/%(pid)s/datastreams/%(dsid)s' % {'pid': pid, 'dsid': dsID}
        r = self.put(url, params=http_args)
        # returns response code 200 on success
        return r.status_code == requests.codes.ok

    def setDatastreamVersionable(self, pid, dsID, versionable):
        # /objects/{pid}/datastreams/{dsID} ? [versionable]
        http_args = { 'versionable' : versionable }
        url = 'objects/%(pid)s/datastreams/%(dsid)s' % {'pid': pid, 'dsid': dsID}
        r = self.put(url, params=http_args)
        # returns response code 200 on success
        return r.status_code == requests.codes.ok


    ### utility methods

    def upload(self, data, callback=None):
        '''
        Upload a multi-part file for content to ingest.  Returns a
        temporary upload id that can be used as a datstream location.

        :param data: content string or file-like object to be uploaded
        :param callback: optional callback method to monitor the upload;
            see :mod:`requests-toolbelt` documentation for more
            details: https://toolbelt.readthedocs.org/en/latest/user.html#uploading-data

        :returns: upload id on success
        '''
        url = 'upload'
        # fedora only expects content uploaded as multipart file;
        # make string content into a file-like object so requests.post
        # sends it the way Fedora expects.
        if not hasattr(data, 'read'):
            data = StringIO(data)

        # use requests-toolbelt multipart encoder to avoid reading
        # the full content of large files into memory
        m = MultipartEncoder(fields={'file': data})

        if callback is not None:
            m = MultipartEncoderMonitor(m, callback)

        try:
            r = self.post(url, data=m, headers={'Content-Type': m.content_type})
        except OverflowError as err:
            print err
            # Python __len__ uses integer so it is limited to system maxint,
            # and requests and requests-toolbelt use len() throughout.
            # This results in an overflow error when trying to upload a file
            # larger than system maxint (2GB on 32-bit OSes).
            # See http://bugs.python.org/issue12159
            msg = 'upload content larger than system maxint (32-bit OS limitation)'
            logger.error('OverflowError: %s', msg)
            raise OverflowError(msg)

        if r.status_code == requests.codes.accepted:
            return r.content.strip()
            # returns 202 Accepted on success
            # content of response should be upload id, if successful


# NOTE: the "LITE" APIs are planned to be phased out; when that happens, these functions
# (or their equivalents) should be available in the REST API

class API_A_LITE(HTTP_API_Base):
    """
       Python object for accessing `Fedora's API-A-LITE <http://fedora-commons.org/confluence/display/FCR30/API-A-LITE>`_.
    """
    def describeRepository(self):
        """
        Get information about a Fedora repository.

        :rtype: string
        """
        http_args = { 'xml': 'true' }
        return self.get('describe', params=http_args)


class ApiFacade(REST_API, API_A_LITE):
    """Pull together all Fedora APIs into one place."""
    # as of 3.4, REST API covers everything except describeRepository
    def __init__(self, base_url, username=None, password=None):
        HTTP_API_Base.__init__(self, base_url, username, password)


class UnrecognizedQueryLanguage(EnvironmentError):
    pass

class ResourceIndex(HTTP_API_Base):
    "Python object for accessing Fedora's Resource Index."

    RISEARCH_FLUSH_ON_QUERY = False
    """Specify whether or not RI search queries should specify flush=true to obtain
    the most recent results.  If flush is specified to the query method, that
    takes precedence.

    Irrelevant if Fedora RIsearch is configured with syncUpdates = True.
    """

    def find_statements(self, query, language='spo', type='triples', flush=None):
        """
        Run a query in a format supported by the Fedora Resource Index (e.g., SPO
        or Sparql) and return the results.

        :param query: query as a string
        :param language: query language to use; defaults to 'spo'
        :param type: type of query - tuples or triples; defaults to 'triples'
        :param flush: flush results to get recent changes; defaults to False
        :rtype: :class:`rdflib.ConjunctiveGraph` when type is ``triples``; list
            of dictionaries (keys based on return fields) when type is ``tuples``
        """
        http_args = {
            'type': type,
            'lang': language,
            'query': query,
        }
        if type == 'triples':
            format = 'N-Triples'
        elif type == 'tuples':
            format = 'CSV'
        # else - error/exception ?
        http_args['format'] = format

        return self._query(format, http_args, flush)

    def count_statements(self, query, language='spo', type='triples',
                         flush=None):
        """
        Run a query in a format supported by the Fedora Resource Index
        (e.g., SPO or Sparql) and return the count of the results.

        :param query: query as a string
        :param language: query language to use; defaults to 'spo'
        :param flush: flush results to get recent changes; defaults to False
        :rtype: integer
        """
        format = 'count'
        http_args = {
            'type': type,
            'lang': language,
            'query': query,
            'format': format
        }
        return self._query(format, http_args, flush)


    def _query(self, format, http_args, flush=None):
        # if flush parameter was not specified, use class setting
        if flush is None:
            flush = self.RISEARCH_FLUSH_ON_QUERY
        http_args['flush'] = 'true' if flush else 'false'

        url = 'risearch'
        try:
            r = self.get(url, params=http_args)
            data, abs_url = r.content, r.url
            # parse the result according to requested format
            if format == 'N-Triples':
                return parse_rdf(data, abs_url, format='n3')
            elif format == 'CSV':
                # reader expects a file or a list; for now, just split the string
                # TODO: when we can return url contents as file-like objects, use that
                return csv.DictReader(data.split('\n'))
            elif format == 'count':
                return int(data)

            # should we return the response as fallback?
        except RequestFailed, f:
            if 'Unrecognized query language' in f.detail:
                raise UnrecognizedQueryLanguage(f.detail)
            # could also see 'Unsupported output format'
            else:
                raise f


    def spo_search(self, subject=None, predicate=None, object=None):
        """
        Create and run a subject-predicate-object (SPO) search.  Any search terms
        that are not specified will be replaced as a wildcard in the query.

        :param subject: optional subject to search
        :param predicate: optional predicate to search
        :param object: optional object to search
        :rtype: :class:`rdflib.ConjunctiveGraph`
        """
        spo_query = '%s %s %s' % \
                (self.spoencode(subject), self.spoencode(predicate), self.spoencode(object))
        return self.find_statements(spo_query)

    def spoencode(self, val):
        """
        Encode search terms for an SPO query.

        :param val: string to be encoded
        :rtype: string
        """
        if val is None:
            return '*'
        elif "'" in val:    # FIXME: need better handling for literal strings
            return val
        else:
            return '<%s>' % (val,)

    def get_subjects(self, predicate, object):
        """
        Search for all subjects related to the specified predicate and object.

        :param predicate:
        :param object:
        :rtype: generator of RDF statements
        """
        for statement in self.spo_search(predicate=predicate, object=object):
            yield str(statement[0])

    def get_predicates(self, subject, object):
        """
        Search for all subjects related to the specified subject and object.

        :param subject:
        :param object:
        :rtype: generator of RDF statements
        """
        for statement in self.spo_search(subject=subject, object=object):
            yield str(statement[1])

    def get_objects(self, subject, predicate):
        """
        Search for all subjects related to the specified subject and predicate.

        :param subject:
        :param object:
        :rtype: generator of RDF statements
        """
        for statement in self.spo_search(subject=subject, predicate=predicate):
            yield str(statement[2])

    def sparql_query(self, query, flush=None):
        """
        Run a Sparql query.

        :param query: sparql query string
        :rtype: list of dictionary
        """
        return self.find_statements(query, language='sparql', type='tuples', flush=flush)


