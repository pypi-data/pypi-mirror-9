"""
Module: profilegrab.py
=====================

Description:
------------
        
    Contains ProfileGrab class, which exposes the user interface.

###############################
Charlie Hack
charlie@205consulting.com 
December 2014
###############################
"""
import twitter
import pattern

from profilegrab.scrapers import get_twitter_text
from profilegrab.scrapers import get_facebook_text
from profilegrab.scrapers import scrape_from_id
import settings


class BaseProfileGrab(object):
    """
    Class: BaseProfileGrab
    ======================

    Description:
    ------------
    Contains base properties of ProfileGrab. 
    Instantiates API connections.
    """
    def __init__(self):
        self.facebook  = pattern.web.Facebook(license=settings.facebook_license)
        self.twitter   = twitter.Api(**settings.twitter_api_credentials)


class ProfileGrab(BaseProfileGrab):
    """
    Class: ProfileGrab
    ==================

    Description:
    ------------
    Implements the user interface for pulling down text from social media
    Main method is `grab`, which can take in a variety of pointers to one or more profiles,
    disambiguate, and pull down a block of contentful text from those profiles.

    Usage:
    ------

    In [1]: from profilegrab import ProfileGrab
    In [2]: pg = ProfileGrab()
    In [3]: charlie_twitter = pg.grab("@c_hack")
    In [4]: charlie_facebook = pg.grab("charlie.hack")
    In [5]: fb_from_id = pg.grab(facebook_id="100000823926890")
    In [6]: tw_from_id = pg.grab(twitter_id="106537958")
    In [7]: multiple = pg.grab("charlie.hack", "KevinDurant", "@drose")
    In [8]: multiple_id = pg.grab(facebook_id=["100000823926890", "81781281654"])

    """
    def __init__(self):
        super(ProfileGrab, self).__init__()


    def grab(self, *args, **kwargs):
        """
        The main method for ProfileGrab.
        Disambiguates the uids and calls the appropriate scraper method.
        Specify twitter screen names with a leading '@' character.
        Numeric IDs should be specified as keyword arguments.
            - returns: dict, in the format {"twitter:@c_hack":u"Check out this link I found! [...]"} 
        """
        text = {}

        assert set(kwargs.keys()).issubset(settings.allowed_ids), "Unrecognized keyword argument. Please supply one of: %s" % str(settings.allowed_ids)

        for arg in args:
            if isinstance(arg, str):
                arg = unicode(arg) 
            if isinstance(arg, unicode):
                if arg.startswith('@'):
                    text['twitter:' + arg] = get_twitter_text(arg, self.twitter)
                else:
                    text['facebook:' + arg] = get_facebook_text(arg, self.facebook)
            elif isinstance(arg, int):
                raise TypeError("When specifying a numeric id, please use a keyword argument, e.g. facebook_id=1287364581")
                
            elif isinstance(arg, list):
                assert all([isinstance(x, str) or isinstance(x, unicode) for x in arg]), "Unrecognized input. Please supply a uri or list of uris."
                for uri in list:
                    text.update(self.grab(uri))
            elif arg is None:
                continue

            else:
                raise TypeError("Unrecognized input type: %s" % type(arg))

        for site, arg in kwargs.items():
            if isinstance(arg, str):
                arg = unicode(arg)
            if isinstance(arg, unicode):
                text[site + ":" + arg] = scrape_from_id(site, arg, fb=self.facebook, tw=self.twitter)
            elif isinstance(arg, int):
                text[site + ":" + str(arg)] = scrape_from_id(site, arg, fb=self.facebook, tw=self.twitter)
            elif isinstance(arg, list):
                for uid in arg:
                    text.update(self.grab(**{site:uid}))
            elif arg is None:
                continue
            else:
                raise TypeError("Unrecognized input type: %s" % type(arg))

        return text









