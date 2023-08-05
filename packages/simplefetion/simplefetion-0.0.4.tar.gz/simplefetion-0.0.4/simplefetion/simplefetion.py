#!/usr/bin/env python
# coding=utf-8

import requests
from bs4 import BeautifulSoup
from .simple_requests import cole_requests

def get_weather_fetion(city):
    url = r'http://f.10086.cn/weather/sch.do?code=%s' % city
    headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4', 'Host': 'f.10086.cn'}
    resp = requests.get(url, headers=headers)
    respB = BeautifulSoup(resp.content)
    
    today = respB.find(name='dl', attrs={'class', 'info'}).text
    future = respB.find(name='ul', attrs={'id': 'future'})
    tomorrow = future.findAll(name='li')[0].text
    thedayaftertomorrow = future.findAll(name='li')[1].text
    return u'%s 天气:\n' + \
            today + '\n\n' + \
            tomorrow + '\n' % city

def send_a_message(fuser, fpass, rec, msg):
    '''
        description:
            send one message to one of your fetion friends
        Usage:
            send_a_message(fetion_account, 
                           fetion_password,
                           receiver_phone,
                           message_content)
        For example:
            from simplefetion import send_a_message
            send_a_message('fetionaccount', 'fetionpassword', '13011111111', 'msg')    
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

def send_a_weather(fuser, fpass, rec, city_name):
    send_a_message(fuser, fpass, rec, 
                   get_weather_fetion(city_name))

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
        For example:
            from simplefetion import send_group_message
            send_group_message('fetionaccount', 'fetionpassword', ['13011111111', '13011111112'], 'msg')
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

def send_group_weather(fuser, fpass, recs, city_name):
    send_group_message(fuser, fpass, recs, 
                   get_weather_fetion(city_name))

