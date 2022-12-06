# Fuel Watcher
### A basic web scraper which will let you scrape ```https://www.fuelwatch.wa.gov.au/``` and returns the best priced fuel.

#### Sample usage   
This is still super new (ie. 50 lines of code new). Right now, you just call it like:
``` FuelPrice(suburb="Balcatta",brand="7-Eleven").print_all()```

You can filter by Suburb, region, product or brand. Pass these as keyword variables.

Alternatively, you can not filter at all, and just let the FuelPrice class spew back all the results it finds at you.

Right now, nothing is sorting the results or anything. Maybe at some point there will be some more sophisticated behaviour.