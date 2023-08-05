import string
import nltk


useless_keywords   = ["shared", "likes", "updated", "tagged in", "posted a link"]
punctuation_table  = {ord(c): None for c in string.punctuation}
stopwords          = nltk.corpus.stopwords.words('english')
nonascii_table     = {i: None for i in range(128,1000)}
deletechars        = ''.join([chr(c) for c in range(128,256)])
allowed_ids        = ['facebook_id', 'twitter_id']
sleep_time         = 1


#######################################################################
#####################[ insert your API keys here ]#####################
#######################################################################

twitter_api_credentials = dict(
    consumer_key="t1esVAor6jhvZWUcVaXD2ygg5",
    consumer_secret="lVS7GOMhqd3dotBpFS0bSpbBX6MVN36xreA23ETmUBsSY0BBf1",
    access_token_key="106537958-A9VaJH0WxpGnMpJYqU8k2i4NN0tI58eFyKeun5Ls",
    access_token_secret="zMOANg3Csd1RQpLdrowrUigHvfao1b47bQrzOZNDZlRzT"
)

facebook_license = "CAAEuAis8fUgBAPL80jX4zkJ4OzKVjZBXF7XJMvuOfqlAVJp2d4ycfdiscVIODjJFvqcw1cpYNaSivLRf94juB8LpKVeeZBr3kwJam10dxxZAY0kOXyOioeZAscpPOUok3P99aVPLgQ0FqYheajF5jjktfO27afU3K1JAETexIfLZCTR8kvHoos3bcZB1IlLX8ZD"

