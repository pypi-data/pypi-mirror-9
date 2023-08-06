__author__ = 'CVoncsefalvay'
from pyrst import BirstClient

c = BirstClient(configfile='/Users/CVoncsefalvay/Developer/pyrst/pyrst/config.yaml')
a = c.login()
print a
b = c.listspaces()
print b