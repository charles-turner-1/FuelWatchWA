"""
Fuelwatch: Lets you scrape tools via their RSS feed. Basically, we're gonna 
have to send some HTML requests using the requests library, and then play with 
the data we get back.
"""

import requests
import json
import os 
import shutil
import feedparser
import pandas

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_json(filename: str):
    with open(filename) as f_in:
        return json.load(f_in)

class FuelPrice():
    def __init__(self,brand=None,product=None,region=None,suburb=None
                ,surrounding=True):
        self.base_URL = "https://www.fuelwatch.wa.gov.au/fuelwatch/fuelWatchRSS"

        data_path = os.path.join(ROOT_DIR,"data")
        self.brand   = read_json(os.path.join(data_path,"brand.json"))
        self.product = read_json(os.path.join(data_path,"product.json"))
        self.region  = read_json(os.path.join(data_path,"region.json"))
        self.suburb  = read_json(os.path.join(data_path,"suburb.json"))
       
        self.payload = {}
    
        if brand is not None:
            self.payload["Brand"] = self.brand[brand]
        if product is not None:
            self.payload["Product"] = self.product[product]
            self.fuel_name = product
        else:
            self.fuel_name = "Unleaded Petrol"
        
        if region is not None:
            self.payload["Region"] = self.region[region]
        if suburb is not None:
            self.payload["Suburb"] = suburb

        self.payload["Surrounding"] = "yes" if surrounding is True else "no"

        self.request()

    
    def request(self):
        self.response = requests.get(self.base_URL,params=self.payload
                                    ,headers={'user-agent' : ''})
        self.feed = feedparser.parse(self.response.content)['entries']
        #self.data_fields = self.feed[0].keys()

    def print_all(self):
        for feed_val in self.feed:
            print(f"{feed_val['brand']} sells {self.fuel_name} for {feed_val['price']} at {feed_val['address']}")
    
    def get_brands(self):
        return [key for key in self.brand.keys()]
    
    def get_suburbs(self):
        return [key for key in self.suburb.keys()]

    def get_regions(self):
        return [key for key in self.region.keys()]

    def get_products(self):
        return [key for key in self.product.keys()]

    def set_brand(self,brand):
        self.payload["Brand"] = brand
    
    def set_suburb(self,suburb):
        self.payload["Suburb"] = suburb 

    def set_region(self,region):
        self.payload["Region"] = region 

    def set_product(self,product):
        self.payload["Product"] = product

    def set_surrounding(self,surrounding):
        self.payload["Surrounding"] = "yes" if surrounding is True else "no"