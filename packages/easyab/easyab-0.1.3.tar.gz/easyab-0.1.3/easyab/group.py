'''
Created on: Dec 04, 2014

@author: qwang
'''

def group_user(did, locale):
    '''
    Use did to group user, return number between 1 to 16 as group index.
    '''
    did_hash = hash(did)
    return did_hash % 16 + 1
