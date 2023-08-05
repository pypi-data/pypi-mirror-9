"""
Module: scrapers.py
=====================

Description:
------------
        
    Contains methods for scraping text from Facebook and Twitter.
    Uses pattern and twitter libraries.


###############################
Charlie Hack
charlie@205consulting.com 
December 2014
###############################
"""
import time
import requests
from pattern.web import Facebook, NEWS, COMMENTS, LIKES, URLTimeout, URLError
from twitter.error import TwitterError

from profilegrab.utils import print_status
from profilegrab.utils import remove_nonascii
import settings

def get_twitter_text(uri, api):
    """
    take in a uri (screen name or UUID) and twitter API instance
    return a string of profile blurb + recent posts
        - returns: string 
    """
    fetched = False
    user_text = u''

    while not fetched:
        try:
            if isinstance(uri, unicode):
                if all([c.isdigit() for c in uri]):
                    user = api.GetUser(user_id=uri)
                else:
                    user = api.GetUser(screen_name=uri)
            elif isinstance(uri, int):
                user = api.GetUser(user_id=uri)

            timeline   = api.GetUserTimeline(user_id=user.id)
            user_text  = ' '.join([unicode(remove_nonascii(user.description)), ' '.join([unicode(remove_nonascii(s.text)) for s in timeline])])
            fetched    = True
        except TwitterError as e:
            print(e)
            return user_text

    assert isinstance(user_text, unicode), "twitter {user_text} isn't unicode, it's {type}.".format(user_text=user_text, type=type(user_text))
    assert len(user_text) > 0, "twitter {user} text is empty.".format(user=screen_name)
    return remove_nonascii(user_text)


def get_facebook_text(uri, api):
    """
    take in a facebook id and pattern facebook API instance
    return a string of profile blurb + recent posts
    if nothing interesting is returned, return empty string
        - returns: string
    """
    if isinstance(uri, unicode):
        if not all([c.isdigit() for c in uri]):
            fid = requests.get(url='http://graph.facebook.com/' + uri).json().get('id')  # get the Facebook id from graph
        else:
            fid = uri
    elif isinstance(uri, int):
        fid = uri

    fetched = False

    while not fetched:
        user_text = []
        try:
            for post in api.search(fid, type=NEWS, count=100):
                post_text = []
                if not any([x in post.text for x in settings.useless_keywords]):  # i.e. `if the post isn't "Charlie Hack likes a photo":`
                    post_text.append(unicode(remove_nonascii(post.text)))
                if post.comments > 0:
                    post_text.extend([unicode(remove_nonascii(r.text)) for r in api.search(post.id, type=COMMENTS)])
                user_text.append(' '.join(post_text))

            user_text  = unicode(' '.join(user_text))
            fetched    = True

        except URLTimeout as e:
            print(e)
            time.sleep(settings.sleep_time)
        except URLError as e:
            print(e)
            break

    if isinstance(user_text, list):
        if len(user_text) >= 1:
            user_text = unicode(' '.join(user_text))  # sometimes these get popped off before the join
        else:
            user_text = u''  # return empty string

    assert isinstance(user_text, unicode), "facebook {user_text} isn't unicode, it's {type}.".format(user_text=user_text, type=type(user_text))
    return remove_nonascii(user_text)


def scrape_from_id(site, uid, fb=None, tw=None):
    """
    convenience method to delegate to the correct scraper
    """
    if site == "facebook_id":
        return get_facebook_text(uid, fb)
    elif site == "twitter_id":
        return get_twitter_text(uid, tw)




