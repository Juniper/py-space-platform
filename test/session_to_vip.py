'''
Created on 04-Dec-2014

@author: rjoyce
'''
import logging.config
from jnpr.space import rest

url = 'https://10.205.57.210'
user = 'super'
passwd = '2juniper'

if __name__ == '__main__':
    logging.config.fileConfig('./logging.conf', disable_existing_loggers=False)

    spc = rest.Space(url, user, passwd, use_session=True, required_node='space-000c2915eb5466')
    try:
        s = spc.connection.get_session()
        for k in s.cookies.iterkeys():
            print k, s.cookies[k]
    finally:
        spc.logout()