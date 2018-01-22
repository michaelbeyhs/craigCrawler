import settings
import math
from walkscore.api import WalkScore

colorGradient = [
    "#FF0000",
    "#FF2300",
    "#FF4600",
    "#FF6900",
    "#FF8C00",
    "#FFAF00",
    "#FFD300",
    "#FFF600",
    "#E5FF00",
    "#C2FF00",
    "#9FFF00",
    "#7CFF00",
    "#58FF00",
    "#35FF00",
    "#12FF00",
]
numOfColoGradients = 15

def clamp(n, minn, maxn):
    return max(min(maxn, n), minn)

def coord_distance(lat1, lon1, lat2, lon2):
    """
    Finds the distance between two pairs of latitude and longitude.
    :param lat1: Point 1 latitude.
    :param lon1: Point 1 longitude.
    :param lat2: Point two latitude.
    :param lon2: Point two longitude.
    :return: Kilometer distance.
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    km = 6367 * c
    return km

def in_box(coords, box):
    """
    Find if a coordinate tuple is inside a bounding box.
    :param coords: Tuple containing latitude and longitude.
    :param box: Two tuples, where first is the bottom left, and the second is the top right of the box.
    :return: Boolean indicating if the coordinates are in the box.
    """
    if box[0][0] < coords[0] < box[1][0] and box[1][1] < coords[1] < box[0][1]:
        return True
    return False

def post_listing_to_slack(sc, listing):
    """
    Posts the listing to slack.
    :param sc: A slack client.
    :param listing: A record of the listing.
    """
    priceGrade = int(numOfColoGradients-(float(listing["price"][1:])-settings.MIN_PRICE)/((settings.MAX_PRICE-settings.MIN_PRICE))*numOfColoGradients)
    walkGrade = int((float(listing["walkscore"])-settings.MIN_WALKSCORE)/(90-settings.MIN_WALKSCORE)*numOfColoGradients)
    distGrade = int(numOfColoGradients-(float(listing["bart_dist"])-0)/(settings.IDEAL_TRANSIT_DIST-0)*numOfColoGradients)

    priceGrade = clamp(priceGrade,0,numOfColoGradients-1)
    walkGrade = clamp(walkGrade,0,numOfColoGradients-1)
    distGrade = clamp(distGrade,0,numOfColoGradients-1)

    walkscoreColor = colorGradient[walkGrade]
    priceColor = colorGradient[priceGrade]
    distColor = colorGradient[distGrade]

    attach_json = [
            {
                "fallback": "Required plain-text summary of the attachment.",
                "color": "" + priceColor,
                "author_name": "" + listing["area"],
                "title": "*" + listing["price"] + " - " + listing["name"] + "*",
                "title_link": ""+ listing["url"],
                #"text": "Cool info here!",
                "image_url": ""+listing["img_url"],
                #"thumb_url": ""+listing["img_url"],
                "footer": "-",

                "ts": 123456789
                    },
            {
                "color": ""+walkscoreColor,
                "fields": [
                    {
                        "title": "Walkscore",
                        "value": "" + str(listing["walkscore"]) + " | <" + listing["ws_link"] + "|Walkscore Link>",
                        "short": True
                    }
                ]
            },
            {
                "color": "" + distColor,
                "fields": [
                    {
                        "title": "Distance",
                        "value": "" + str(listing["bart_dist"]) + " - " + listing["bart"] + " | <" +"https://www.google.com/maps/dir/" + listing["bart"] + "/" + str(listing["geotag"][0]) + "," + str(listing["geotag"][1]) + "|Maps>",
                        "short": True
                    }
                ],
            }
        ]


    googleLink = "https://www.google.com/maps/dir/" + listing["bart"] + "/" + str(listing["geotag"][0]) + "," + str(listing["geotag"][1])
    desc = "{0} | {1} | {2}km - {3} | *{4}* \r\n".format(listing["area"], listing["price"], listing["bart_dist"], listing["bart"], listing["name"])
    desc = desc + "<" + listing["url"] + "|Craigslist> | <" + listing["ws_link"] + "|Walkscore " + str(listing["walkscore"]) + "> | <" + googleLink + "|Google Maps>" 
    sc.api_call(
        "chat.postMessage", channel=settings.SLACK_CHANNEL, text=desc,
        username='pybot',  icon_emoji=':robot_face:', attachments=attach_json
    )
    #print "posting to Slack \r\n " + desc

def find_points_of_interest(geotag, location):
    """
    Find points of interest, like transit, near a result.
    :param geotag: The geotag field of a Craigslist result.
    :param location: The where field of a Craigslist result.  Is a string containing a description of where
    the listing was posted.
    :return: A dictionary containing annotations.
    """
    area_found = False
    area = ""
    min_dist = None
    near_bart = False
    bart_dist = "N/A"
    bart = ""
    # Look to see if the listing is in any of the neighborhood boxes we defined.
    for a, coords in settings.BOXES.items():
        if in_box(geotag, coords):
            area = a
            area_found = True
            print "------------------listing is in defined GEO Box" + area

    # Check to see if the listing is near any transit stations.
    for station, coords in settings.TRANSIT_STATIONS.items():
        dist = coord_distance(coords[0], coords[1], geotag[0], geotag[1])
        if (min_dist is None or dist < min_dist) and dist < settings.MAX_TRANSIT_DIST:
            bart = station
            near_bart = True
            print "listing is close to " + station

        if (min_dist is None or dist < min_dist):
            bart_dist = round(dist,1)
            min_dist = dist
            print "Distance is " + str(dist)

    # If the listing isn't in any of the boxes we defined, check to see if the string description of the neighborhood
    # matches anything in our list of neighborhoods.
    if len(area) == 0:
        for hood in settings.NEIGHBORHOODS:
            if hood in location.lower():
                area = hood
                print "listing is in defined neighborhood " + hood

    return {
        "area_found": area_found,
        "area": area,
        "near_bart": near_bart,
        "bart_dist": bart_dist,
        "bart": bart
    }

def get_walk_score(geotag):
    walkscore = WalkScore(settings.WALKSCORE_API_KEY)

    address=''
    lat=geotag[0]
    lon=geotag[1]
    response = walkscore.makeRequest(address, lat, lon)
    #print(response['walkscore'])
    #print(response['description'])
    #print(response['ws_link'])
    return response['walkscore'], response['ws_link']


