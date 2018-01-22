import os


# search URL:
# https://sfbay.craigslist.org/search/sby/apa?nh=31&nh=32&nh=35&nh=37&nh=41&nh=44&availabilityMode=0&sale_date=all+dates

## Price

# The minimum rent you want to pay per month.
MIN_PRICE = 1800

# The maximum rent you want to pay per month.
MAX_PRICE = 2600

## Location preferences

# The Craigslist site you want to search on.
# For instance, https://sfbay.craigslist.org is SF and the Bay Area.
# You only need the beginning of the URL.
CRAIGSLIST_SITE = 'sfbay'

# What Craigslist subdirectories to search on.
# For instance, https://sfbay.craigslist.org/eby/ is the East Bay, and https://sfbay.craigslist.org/sfc/ is San Francisco.
# You only need the last three letters of the URLs.
AREAS = ["sby"]

# A list of neighborhoods and coordinates that you want to look for apartments in.  Any listing that has coordinates
# attached will be checked to see which area it is in.  If there's a match, it will be annotated with the area
# name.  If no match, the neighborhood field, which is a string, will be checked to see if it matches
# anything in NEIGHBORHOODS.

# I don't think these actually work?!
BOXES = {
    "MountainView": [
        [37.380269, -122.104341],
        [37.406591,	-122.063485],
    ],
    "Sunnyvale": [
        [37.362373,-122.063061],
        [37.395861,-122.003924],
    ]
}

# A list of neighborhood names to look for in the Craigslist neighborhood name field. If a listing doesn't fall into
# one of the boxes you defined, it will be checked to see if the neighborhood name it was listed under matches one
# of these.  This is less accurate than the boxes, because it relies on the owner to set the right neighborhood,
# but it also catches listings that don't have coordinates (many listings are missing this info).
NEIGHBORHOODS = ["campbell", "cupertino", "mountain view", "san jose east", "santa clara", "sunnyvale" ]

## Transit preferences

# The farthest you want to live from a transit stop.
MAX_TRANSIT_DIST = 5 # kilometers
IDEAL_TRANSIT_DIST = 1.5 # kilometers

# Transit stations you want to check against.  Every coordinate here will be checked against each listing,
# and the closest station name will be added to the result and posted into Slack.
TRANSIT_STATIONS = {
    #Mountainview Caltrain
    "Mountain_View_Caltrain":           [37.394548, -122.075945],
    "Mountain_View_Benecia_2":          [37.395312, -122.040757],
    "Mountain_View_Hermosa_CT":         [37.387422, -122.039558],
    "Mountain_View_Mathilda_del_rey":   [37.391188, -122.031386],
    # Los Altos 
    "Mountain_View_El_Monte_At_Marich": [37.390933, -122.095914],
    
    # Sunnyvale Caltrain
    "Sunnyvale_Caltrain":               [37.378460, -122.030692],
    "Sunnyvale_San_Gabriel_4":          [37.375697, -122.015683],
    "Sunnyvale_Wolfe_at_Evelyn":        [37.370494, -122.013825],
    "Sunnyvale_Wolfe_at_Fremont":       [37.352360, -122.014298],
    #Sunnyvale Coach
    "Lawrence_caltrain":                [37.370331, -121.995919],
    "Arques_1":                         [37.378538, -122.000320],
    "De_Guigne_1":                      [37.384505, -122.007099],

    #Milpitas
    "Santa_Clara_station":              [37.353244, -121.936324],

    #Campbel coach
    "Orchard_Glen":                     [37.326240, -121.966821],
    "Saratoga_at_Williams":             [37.307993, -121.978131],
    "Williams_at_Winchester":           [37.309005, -121.950230],
    "Winchester_at_Cadillac":           [37.296851, -121.949951],

    # San Jose
    "Santana_Row":                      [37.323297, -121.948039],

    #Los Gatos
    "Quito_at_Lawrence":                [37.288798, -121.994691],

    #
    "Apple_Park":                       [37.333049, -122.010646],
    "Apple_Vallco_Parkway":             [37.326334, -122.010198],
    "Mariani_One":                      [37.330685, -122.033176]

}

## Search type preferences

# The Craigslist section underneath housing that you want to search in.
# For instance, https://sfbay.craigslist.org/search/apa find apartments for rent.
# https://sfbay.craigslist.org/search/sub finds sublets.
# You only need the last 3 letters of the URLs.

# hacking further filters into here!
# using the neighbourhoods I want. 
CRAIGSLIST_HOUSING_SECTION = 'apa?nh=31&nh=32&nh=35&nh=40&nh=41&nh=44'

## System settings

# How long we should sleep between scrapes of Craigslist.
# Too fast may get rate limited.
# Too slow may miss listings.
SLEEP_INTERVAL = 10 * 60 # 20 minutes

# Which slack channel to post the listings into.
SLACK_CHANNEL = "#housing"

# The token that allows us to connect to slack.
# Should be put in private.py, or set as an environment variable.
SLACK_TOKEN = os.getenv('SLACK_TOKEN', "")

WALKSCORE_API_KEY = os.getenv('WALKSCORE_API_KEY', "")

MIN_WALKSCORE = 50

# Any private settings are imported here.
try:
    from private import *
except Exception:
    pass

# Any external private settings are imported from here.
try:
    from config.private import *
except Exception:
    pass