#!/usr/bin/env python

"""
"""

import unittest

from concrete.util.twitter import json_tweet_string_to_TweetInfo

class TestTwitter(unittest.TestCase):
    def test_json_tweet_string_to_TweetInfo(self):
        json_tweet_string = u'{"contributors": null, "truncated": false, "text": "Barber tells me - his son is colorblind / my hair is auburn / and auburn is a shade of green", "in_reply_to_status_id": null, "id": 238426131689242624, "favorite_count": 0, "source": "<a href=\\"http://twitter.com\\" rel=\\"nofollow\\">Twitter Web Client</a>", "retweeted": false, "coordinates": null, "entities": {"symbols": [], "user_mentions": [], "hashtags": [], "urls": []}, "in_reply_to_screen_name": null, "id_str": "238426131689242624", "retweet_count": 0, "in_reply_to_user_id": null, "favorited": false, "user": {"follow_request_sent": null, "profile_use_background_image": true, "default_profile_image": false, "id": 18063351, "profile_background_image_url_https": "https://abs.twimg.com/images/themes/theme5/bg.gif", "verified": false, "profile_text_color": "3E4415", "profile_image_url_https": "https://pbs.twimg.com/profile_images/67158916/n3703917_32092098_7623_normal.jpg", "profile_sidebar_fill_color": "99CC33", "entities": {"url": {"urls": [{"url": "http://t.co/Qb6hKcbqgj", "indices": [0, 22], "expanded_url": "http://craigharman.net", "display_url": "craigharman.net"}]}, "description": {"urls": []}}, "followers_count": 78, "profile_sidebar_border_color": "829D5E", "id_str": "18063351", "profile_background_color": "352726", "listed_count": 5, "is_translation_enabled": false, "utc_offset": -14400, "statuses_count": 26, "description": "", "friends_count": 54, "location": "", "profile_link_color": "D02B55", "profile_image_url": "http://pbs.twimg.com/profile_images/67158916/n3703917_32092098_7623_normal.jpg", "following": null, "geo_enabled": false, "profile_background_image_url": "http://abs.twimg.com/images/themes/theme5/bg.gif", "screen_name": "charman", "lang": "en", "profile_background_tile": false, "favourites_count": 0, "name": "Craig Harman", "notifications": null, "url": "http://t.co/Qb6hKcbqgj", "created_at": "Thu Dec 11 23:07:27 +0000 2008", "contributors_enabled": false, "time_zone": "Eastern Time (US & Canada)", "protected": false, "default_profile": false, "is_translator": false}, "geo": null, "in_reply_to_user_id_str": null, "lang": "en", "created_at": "Thu Aug 23 00:03:14 +0000 2012", "in_reply_to_status_id_str": null, "place": null}\n'
        ti = json_tweet_string_to_TweetInfo(json_tweet_string)


if __name__ == '__main__':
    unittest.main(buffer=True)
