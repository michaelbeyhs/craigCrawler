from craigslist import CraigslistHousing
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker
from dateutil.parser import parse
from util import post_listing_to_slack, find_points_of_interest, get_walk_score
from slackclient import SlackClient
import time
import settings
import logging

engine = create_engine('sqlite:///listings.db', echo=False)

Base = declarative_base()

class Listing(Base):
    """
    A table to store data on craigslist listings.
    """

    __tablename__ = 'listings'

    id = Column(Integer, primary_key=True)
    link = Column(String, unique=True)
    created = Column(DateTime)
    geotag = Column(String)
    lat = Column(Float)
    lon = Column(Float)
    name = Column(String)
    price = Column(Float)
    location = Column(String)
    cl_id = Column(Integer, unique=True)
    area = Column(String)
    bart_stop = Column(String)
    walkscore = Column(Integer)
    ws_link = Column(String)
    bart_dist = Column(Float)
    img_url = Column(String)

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

def scrape_area(area):
    global loggerOn
    """
    Scrapes craigslist for a certain geographic area, and finds the latest listings.
    :param area:
    :return: A list of results.
    """
    cl_h = CraigslistHousing(site=settings.CRAIGSLIST_SITE, area=area, category=settings.CRAIGSLIST_HOUSING_SECTION,
                             filters={'max_price': settings.MAX_PRICE, "min_price": settings.MIN_PRICE})
    
    # adding some logging to see the URLs
    #cl_h.set_logger(logging.INFO)

    results = []
    gen = cl_h.get_results(sort_by='newest', geotagged=False, limit=35)
    while True:
        try:
            result = next(gen)
        except StopIteration:
            break
        except Exception:
            continue
        listing = session.query(Listing).filter_by(cl_id=result["id"]).first()
        
        # Don't store the listing if it already exists.
        if listing is None:

            # Here we only iterate over listings that we haven't checked in te past.
            # we get the geotags now instead of getting them before for all listings
            # because it requires an aditional GET which is unnecessary if we aleardy have 
            # checked the listing

            if result['has_map']:
                cl_h.geotag_result(result)


            if result["where"] is None:
                # If there is no string identifying which neighborhood the result is from, skip it.
                continue

            lat = 0
            lon = 0
            result["bart_dist"] = 999
            result["walkscore"] = 0
            result["ws_link"]   = "Not found!"
            
            if result["geotag"] is not None:
                # Assign the coordinates.
                lat = result["geotag"][0]
                lon = result["geotag"][1]

                # Annotate the result with information about the area it's in and points of interest near it.
                geo_data = find_points_of_interest(result["geotag"], result["where"])
                result.update(geo_data)


                result["walkscore"], result['ws_link'] = get_walk_score(result["geotag"])

            else:
                result["area"] = ""
                result["bart"] = ""

            # Try parsing the price.
            price = 0
            try:
                price = float(result["price"].replace("$", ""))
            except Exception:
                pass

            if result["img_url"] is None:
                result["img_url"] = ""

            # Create the listing object.
            listing = Listing(
                link=result["url"],
                created=parse(result["datetime"]),
                lat=lat,
                lon=lon,
                name=result["name"],
                price=price,
                location=result["where"],
                cl_id=result["id"],
                area=result["area"],
                bart_stop=result["bart"],
                walkscore=result["walkscore"],
                ws_link=result["ws_link"],
                bart_dist=result["bart_dist"],
                img_url=result["img_url"]
            )

            # Save the listing so we don't grab it again.
            session.add(listing)
            session.commit()

            # Return the result if it's near a bart station, or if it is in an area we defined.
            if len(result["bart"]) > 0 or len(result["area"]) > 0:
                print result["name"]
                print result["walkscore"]
                print result["ws_link"]
                results.append(result)

    return results

def do_scrape():
    """
    Runs the craigslist scraper, and posts data to slack.
    """

    # Create a slack client.
    sc = SlackClient(settings.SLACK_TOKEN)

    # Get all the results from craigslist.
    all_results = []
    for area in settings.AREAS:
        all_results += scrape_area(area)

    print("{}: Got {} results".format(time.ctime(), len(all_results)))

    # Post each result to slack.
    for result in all_results:
        post_listing_to_slack(sc, result)
