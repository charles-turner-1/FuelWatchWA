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
import geocoder
import ast
import collections

from typing import Union

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
    
        if brand:
            self.payload["Brand"] = self.brand[brand]
        if product:
            self.payload["Product"] = self.product[product]
            self.fuel_name = product
        else:
            self.fuel_name = "Unleaded Petrol"
        
        if region:
            self.payload["Region"] = self.region[region]
        if suburb:
            self.payload["Suburb"] = suburb

        self.payload["Surrounding"] = "yes" if surrounding else "no"

        self.request()

        self.build_data()
    
    def request(self):
        self.response = requests.get(self.base_URL,params=self.payload
                                    ,headers={'user-agent' : ''})
        self.feed = feedparser.parse(self.response.content)['entries']

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
        self.payload["Product"] = self.product[product]
        self.fuel_name = product

    def set_surrounding(self,surrounding):
        self.payload["Surrounding"] = "yes" if surrounding is True else "no"

    def build_data(self):
        """ Take self.feed and extract the useful information: title, price, 
            latitude, longitude, location, address into a list of dicts"""
        fields = ["price","trading-name","address","latitude","longitude"
                 ,"location","address"]
        servo_list = []

        for feed_val in self.feed:  
            servo_list.append({field : feed_val[field] for field in fields})
        
        self.servo_list = servo_list
        
class CarInfo():
    """
    This class contains info about your car / ute ie. mileage, tank size, fuel 
    type.
    """
    def __init__(self,tank_size : Union[None,float] = 50
                     ,mileage   : Union[None,float] = 8
                     ,fuel_type : Union[None,str] = "Petrol"):
        """ Initialise with info about our car """
        self.tank_size = tank_size
        self.mileage = mileage
        self.fuel_type = fuel_type

    def calc_fuel_price(self,fuel_price,tank_frac=0.8):
        return fuel_price * tank_frac

    def set_fuel_type(self,fuel_type : str) -> None:
        """ Should probably start by asserting that our fuel type is acceptable.
            """
        self.fuel_type = fuel_type
    
    def set_mileage(self, mileage : float) -> None:
        self.mileage = mileage

    def set_tank_size(self, tank_size : float) -> None:
        self.tank_size = tank_size

class Journey():
    """
    Contains information about start, stop, maximum acceptable detour.
    """
    def __init__(self
                ,start_address : str = None
                ,end_address : str = None
                ,max_acceptable_detour : Union[None,float] = None):

        if start_address:   
            self.add_start_address(start_address)
        if end_address: 
            self.add_end_address(end_address)  
        if max_acceptable_detour:
            self.set_max_detour(max_acceptable_detour)

    def set_start_address(self, start_address : str = None) -> None:
        self.start_address = start_address
        self.start_coords = self.address_to_coords(start_address)

    def set_end_address(self, end_address : str = None) -> None:
        self.end_address = end_address
        self.end_coords = self.address_to_coords(end_address)

    def set_max_detour(self,max_acceptable_detour : float) -> None:
        self.max_acceptable_detour = max_acceptable_detour
    
    def address_to_coords(self, address):
        """
        USe geocoder.yahoo functionality (looks & seems free to use, no API key 
        nonsense) in order to get coordinates.
        """
        address_coords = geocoder.arcgis(address).json

        return address_coords

    def get_car_info(self, car : CarInfo):
        """
        If a CarInfo object has been instantiated, then get info about the car 
        from it. 
        """
        if type(car) != CarInfo:
            raise TypeError("'car' must be a 'CarInfo' object")
        self.tank_size = car.tank_size
        self.mileage = car.mileage
        self.tank_size = car.tank_size
        self.fuel_type = car.fuel_type

    def set_car_info(self,*args,**kwargs):
        """ Instantiate a CarInfo object and then pull its data into this class"""
        car = CarInfo(*args,**kwargs)
        self.get_car_info(car)

    def get_fuel_info(self):
        """ Send Fuelwatch a request for all the prices of the fuel of our car"""
        fuel_type = self.fuel_type

        fuelwatch_results = [dict(fuelwatch_results) for fuelwatch_results 
                                       in FuelPrice(product=fuel_type).feed]

        keys = ["address","latitude","longitude","price"]

        self.fuelwatch_results = []
        for fuelwatch_result in fuelwatch_results:
            self.fuelwatch_results.append({key : fuelwatch_result[key]
                                       for key in keys})

    def request_distance(self,servo_coords : tuple = None):
        """ Send a request to the OSRM server to get some route info
            Right now, OSRM seems to be picking the shortst route, and maybe not
            the fastest (which is probably default for google). Sort this at 
            some point.

            servo_coords : (lon, lat) tuple
        """
        start_coord_str = f"{self.start_coords['lng']},{self.start_coords['lat']}"
        end_coord_str = f"{self.end_coords['lng']},{self.end_coords['lat']}"
        if servo_coords:
            servo_coord_str = f"{servo_coords[0]},{servo_coords[1]}"
            url = f"http://0.0.0.0:5000/route/v1/driving/{start_coord_str};{servo_coord_str};{end_coord_str}"
        else: 
            url = f"http://0.0.0.0:5000/route/v1/driving/{start_coord_str};{end_coord_str}"

        x = requests.get(url=url).content.decode("utf-8")
        x = ast.literal_eval(x)

        distance = x["routes"][0]["distance"]
        return distance

    def get_all_detour_lengths(self):
        """ First compute start-end distance. Then compute all the distances for
            every trip, stopping at one of the servo's that fuelwatch gives us 
            hits for. Then get all the detour lengths."""

        fuel_type = self.fuel_type

        fuelwatch_results = FuelPrice(product=fuel_type).servo_list

        detour_lengths = []

        base_dist = self.request_distance()
        for result in fuelwatch_results:
            servo_coords = (result.get("longitude"),result.get("latitude"))
            distance = self.request_distance(servo_coords)
            detour_lengths.append(distance - base_dist)

        return detour_lengths

    def get_all_detour_costs(self):
        """ First compute start-end distance. Then compute all the distances for
            every trip, stopping at one of the servo's that fuelwatch gives us 
            hits for. Then get all the detour lengths. Now multiply that by the 
            price of fuel at that servo to figure out how much the detour costs
        """

        fuel_type = self.fuel_type

        fuelwatch_results = FuelPrice(product=fuel_type).servo_list

        detour_costs = {}
        

        base_dist = self.request_distance() / 1000 # Base distance in KM
        for result in fuelwatch_results:
            servo_coords = (result.get("longitude"),result.get("latitude"))
            servo_name = f"{result.get('trading-name')}, {result.get('address')}"
            servo_price = float(result.get("price")) / 100 # Price in Dollars
            car_mileage = self.mileage / 100 # Mileage in litres/km
            distance = self.request_distance(servo_coords) / 1000 # Distance in KM

            try:    
                detour_cost = servo_price * car_mileage * (distance - base_dist)
            except:
                detour_cost = np.NaN
            detour_costs[servo_name] = detour_cost

        detour_costs = dict(sorted(detour_costs.items(), key=lambda item: item[1]))
        return detour_costs

    def get_all_detour_values(self, num_litres):
        """ First compute start-end distance. Then compute all the distances for
            every trip, stopping at one of the servo's that fuelwatch gives us 
            hits for. Then get all the detour lengths. Now multiply that by the 
            price of fuel at that servo to figure out how much the detour costs
        """

        fuel_type = self.fuel_type

        fuelwatch_results = FuelPrice(product=fuel_type).servo_list

        info_dict = {}

        base_dist = self.request_distance() / 1000 # Base distance in KM
        for result in fuelwatch_results:
            servo_coords = (result.get("longitude"),result.get("latitude"))
            servo_name = f"{result.get('trading-name')}, {result.get('address')}"
            servo_price = float(result.get("price")) / 100 # Price in Dollars
            car_mileage = self.mileage / 100 # Mileage in litres/km
            distance = self.request_distance(servo_coords) / 1000 # Distance in KM

            try:    
                detour_cost = servo_price * car_mileage * (distance - base_dist)
                fuel_cost = servo_price * num_litres
            except:
                detour_cost = np.NaN

            info_dict[servo_name] = (distance - base_dist, fuel_cost, detour_cost, fuel_cost + detour_cost)

        info_dict = {key : val for key, val in info_dict.items() if val[0] < self.max_acceptable_detour}

        info_dict = dict(sorted(info_dict.items(), key=lambda item: item[1][3]))
        return info_dict