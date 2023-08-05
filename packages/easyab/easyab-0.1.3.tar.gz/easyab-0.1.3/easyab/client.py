#encoding: utf-8
'''
Created on: Dec 10, 2014

@author: chjchen
'''
import time
import urllib
import urllib2
import logging
import simplejson

from easyab.group import group_user

_LOGGER = logging.getLogger('easyab')

_STATUS_VALID = 0
_STATUS_USING_STOP = 1
_STATUS_USING_START = 2

_DELETE_SUCESSED = 0
_DELETE_NOTEXISTED = 1
_DELETE_RUNNING = 2

OK = 0
ERROR = -1

LAST_TIME = 0
TIME_DIFF = 60
GROUPS = []

LAST_TIME_KPI = 0
TIME_DIFF_KPI = 60
TESTS = []


class EasyClient(object):
    '''
    Client for using easyab functions.
    '''

    def __init__(self, server_ip, sync_interval=60):
        global TIME_DIFF
        self._server = server_ip
        self._syn_api = "http://" + self._server + "/report/abtest/syngroup.json"
        self._syn_test_api = "http://" + self._server + "/report/abtest/syntest.json"
        TIME_DIFF = sync_interval

    def _synchronize_from_webservice(self):
        '''
        The function will convey some parameters to the web service,
        and then receives the groups to synchronize the data locally.
        '''
        tmp_groups = {}
        post_dict = {}
        post_data = urllib.urlencode(post_dict)
        req = urllib2.Request(self._syn_api, post_data)
        try:
            page = urllib2.urlopen(req)
            data = page.read()
        except urllib2.HTTPError, e:
            _LOGGER.error('[easyab] Got error when sync groups: %s' % e)
            return False, []
        except urllib2.URLError, e:
            _LOGGER.error('[easyab] Got error when sync groups: %s' % e)
            return False, []
        try:
            data = simplejson.loads(data)
        except Exception, e:
            _LOGGER.error('[easyab] Groups not json format: %s, %s' % (e, tmp_groups))
            return False, []
        if 'sta' not in data or data['sta'] != OK:
            return False, []
        groups = data['tips']
        return True, groups

    def _get_grouptag_from_client(self, group_id, locale, test_name):
        '''
        Search the tag from the client library
        If the group_id, locale, test_name and status are all right, return the flag
        Else, return a string 'none'
        '''
        global LAST_TIME, GROUPS
        now_time = time.time()

        if int(now_time - LAST_TIME) > TIME_DIFF:
            flag_groups, tmp_groups = self._synchronize_from_webservice()
            if flag_groups:
                GROUPS = tmp_groups
                LAST_TIME = now_time
            else:
                _LOGGER.error('[easyab] Get groups from server failed!')
        group_tag = None
        for group in GROUPS:
            if group['group_id'] == group_id and group['locale'] == locale and group['test_name'] == test_name and group['status'] == _STATUS_USING_START:
                group_tag = group['flag']
        return group_tag

    def get_group_tag(self, uid, locale, test_name):
        '''
        Get the tag of the groups, and this group is not the group 1-16, but the
        group which is defined by the user
        This is a function not a api
        '''
        #convey the uid and locale, return the group_id
        group_id = group_user(uid, locale)

        #get the tag of the group locally or from web service
        return self._get_grouptag_from_client(group_id, locale, test_name)

    def _synchronize_test_from_webservice(self):
        '''
        Synchronize the tests from web service
        but we only select the rows which status is not -1
        '''
        tmp_tests = {}
        post_dict = {}
        post_data = urllib.urlencode(post_dict)
        req = urllib2.Request(self._syn_test_api, post_data)
        try:
            page = urllib2.urlopen(req)
            data = page.read()
        except urllib2.HTTPError, e:
            _LOGGER.error('[easyab] Got error when sync groups: %s' % e)
            return False, []
        except urllib2.URLError, e:
            _LOGGER.error('[easyab] Got error when sync groups: %s' % e)
            return False, []
        try:
            data = simplejson.loads(data)
        except Exception, e:
            _LOGGER.error('[easyab] Groups not json format: %s, %s' % (e, tmp_tests))
            return False, []
        if 'sta' not in data or data['sta'] != OK:
            return False, []
        tests = data['tips']
        return True, tests

    def _get_kpi_from_client(self, group_id, locale):
        '''
        Convey the uid, and turn the uid into the group_id
        Convey the group_id and locale, search the kpi locally
        '''
        global LAST_TIME_KPI, TESTS
        now_time = time.time()

        if int(now_time - LAST_TIME_KPI) > TIME_DIFF_KPI:
            flag_tests, tmp_tests = self._synchronize_test_from_webservice()
            if flag_tests:
                TESTS = tmp_tests
                LAST_TIME_KPI = now_time
            else:
                _LOGGER.error('[easyab] Get groups from server failed!')
        for test in TESTS:
            if test['locale'] == locale:
                tmp_kpi = test['kpi']
                tmp_data = test['groups']
                json_data = {}

                try:
                    json_data = simplejson.loads(tmp_data)
                except Exception, e:
                    _LOGGER.error('[easyab] Groups not json format: %s, %s' % (e, tmp_data))
                    return "ERROR"

                for k, _ in json_data.items():
                    if int(k) == group_id:
                        return tmp_kpi

    def get_uid_kpi(self, uid, locale):
        '''
        Convey the uid and locale
        return the kpi(string)
        '''
        group_id = group_user(uid, locale)

        kpi = self._get_kpi_from_client(group_id, locale)
        if kpi != "ERROR":
            test_tips = [group_id, kpi]
            return test_tips
