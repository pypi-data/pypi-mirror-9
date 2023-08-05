#!/usr/bin/env python
# coding=utf-8

from simple_requests import cole_requests


def send_a_message(fuser, fpass, rec, msg):
    '''
        description:
            send one message to one of your fetion friends
        Usage:
            send_a_message(fetion_account, 
                           fetion_password,
                           receiver_phone,
                           message_content)
    '''
    assert(fuser and fpass and rec and msg)
    url = 'https://djangofetion.sinaapp.com/msg/'
    data = {
        'phone': fuser,
        'password': fpass,
        'to_phone': rec,
        'content': msg
    }
    return cole_requests.post(url, data)

def send_group_message(fuser, fpass, recs, msg):
    '''
        description:
            send a group message to your fetion friends
        Usage:
            send_a_message(fetion_account, 
                           fetion_password,
                           receiver_phones,
                           message_content)
        Take Care:
            receiver_phones must be a list type data
    '''
    assert(fuser and fpass and recs and msg)
    assert(isinstance(recs, list))
    
    url = 'https://djangofetion.sinaapp.com/gmsg/'

    recs = ','.join(recs)
    data = {
        'phone': fuser,
        'password': fpass,
        'to_phone': recs,
        'content': msg
    }
    return cole_requests.post(url, data, 10)
