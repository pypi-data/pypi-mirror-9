import string
import nltk


useless_keywords   = ["shared", "likes", "updated", "tagged in", "posted a link"]
punctuation_table  = {ord(c): None for c in string.punctuation}
stopwords          = nltk.corpus.stopwords.words('english')
nonascii_table     = {i: None for i in range(128,1000)}
deletechars        = ''.join([chr(c) for c in range(128,256)])
allowed_ids        = ['facebook_id', 'twitter_id']
sleep_time         = 1



