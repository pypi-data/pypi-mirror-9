__author__ = 'CVoncsefalvay'

from pyrst.client import BirstClient
from pyrst.handlers import JsonHandler, DfHandler

cl = BirstClient(configfile="/Users/CVoncsefalvay/Developer/mediate/config.yaml")
cl.login()
print("logged in, querying")
m = cl.retrieve(space = "1f500014-65f9-40da-9d9d-0c0fa01a4fbf",
                query = "SELECT [store_dim.store_state] 'F3',[item_dim.item_segment] 'F5',[Sum: sales_volume] 'F1' FROM [ALL]",
                handler = JsonHandler)

print m