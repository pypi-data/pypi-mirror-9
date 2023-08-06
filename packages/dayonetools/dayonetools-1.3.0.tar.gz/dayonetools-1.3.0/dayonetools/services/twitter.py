#filename = '/Users/durden/Dropbox/twitter_backups/tweets/data/js/tweets/2013_06.js'

from datetime import datetime
import json
import re

# This doesn't work on Python built-in for OS X, 'z' is not valid directive
# even though it's specified in docs??
# Looks like datetime.strptime only supports what time.strftime supports and is
# platform dependent.  So, apparently this isn't supported on the Python
# version that comes with OS X (b/c apple is silly or b/c apple's C runtime
# doesn't support it under the hood).

# As a workaround, could just parse the string's first 4 tokens and last token
# with split() and pass those to datetime.strptime b/c that will strip off
# the timezone.
#datetime.strptime('%a %b %d %H:%M:%S %z %Y', d)


def tweet_to_markdown(tweet):
    text = tweet['text']
    urls = tweet['entities']['urls'] or []

    # Replace all urls with markdown version
    for url in urls:
        text = re.sub(r'(%s)' % (url['url']),
                      r'[%s](%s)' % (url['display_url'], url['expanded_url']),
                      text)
    return text


def main(filename):
    tweets = open(filename, 'r')

    # Discard assignment line
    tweets.readline()

    json_tweets = tweets.read()

    for tweet in json.loads(json_tweets):
        # FIXME: Need to detect date from tweet json:
        #   - Create new dayone file for each day
        print tweet_to_markdown(tweet)


if __name__ == '__main__':
    import sys
    main(sys.argv[1])
