import tweepy
import time
import json
from config import create_api
import logging

logging.basicConfig(level=logging.INFO)

class DscFutaBot:
    '''The DscFutaBot class represents a model for a twitter bot that like and retweet posts that contain dsc
       from certain user's timeline'''
    
    def __init__(self,api,since_id_filename,instructor_handles_filename,dsc_handles_filename,
                 keywords,search_query):
        ''' methods for initializing DscFutaBot object
        Args:
            api(tweepy.api.API)
            since_id_filename(str)
            instructor_handles_filename(str)
            dsc_handles_filename(str)
            keywords(list)
            search_query(str)
        Attributes:
                  api(tweepy.api.API):
                  since_id_filename(str): the filename of the last status id the bot responded to
                  instructor_handles_filename(str): the json file where dscfuta instructors handles are stored
                  dsc_handles_filename(str): the json file where handles for dsc in other instituitions are stored
                  keywords(list): A list of terms to search for on user's timeline
                  search_query(str): keywords to search for
            
        '''
        self.api = api
        self.me = api.me()
        self.since_id_filename = since_id_filename
        self.instructor_handles_filename = instructor_handles_filename
        self.dsc_handles_filename = dsc_handles_filename
        self.keywords = keywords
        self.search_query = search_query
        self.new_since_id = []
    
    def get_last_since_id(self):
        '''This method retrieves the new since_id from the text file where it is stored'''
        f_read = open(self.since_id_filename, 'r')
        last_since_id = int(f_read.read().strip())
        f_read.close()
        return last_since_id

    def save_last_since_id(self,last_since_id):
        '''This method saves the latest since_id in the text while executing'''
        f_write = open(self.since_id_filename, 'w')
        f_write.write(str(last_since_id))
        f_write.close()
        return


    def respond_to_dscfuta_instructors(self):
        """ This method checks the timeline of the current dsc
        instructors then retweet and like any post related to developer student club"""
        
        since_id = self.get_last_since_id()
        instructors = json.load(open(self.instructor_handles_filename))['handles']
        for instructor in instructors:
            tweets = api.user_timeline(screen_name= instructor, since_id=since_id, tweet_mode='extended')
            for tweet in reversed(tweets):
                if tweet.in_reply_to_status_id is not None or tweet.id == since_id:
                    continue
                if any(key in tweet.full_text.lower() for key in self.keywords):
                    try:
                        logging.info(f'found a new tweet on {instructor}\'s timeline....')
                        time.sleep(2)
                        tweet.retweet()
                        tweet.favorite()
                        logging.info(f'successfully retweeted and liked this tweet by @{tweet.user.screen_name}')
                    except tweepy.TweepError:
                        logging.error(f'Error while retweeting and liking', exc_info=True)
                self.new_since_id.append(tweet.id)
            time.sleep(5)
            logging.info(f'Done checking {instructor}\'s timeline found no new tweet ')
        if len(self.new_since_id) != 0:
            self.save_last_since_id(max(self.new_since_id))
        self.new_since_id.clear()


    def respond_to_keywords(self):
        '''This method searches for tweets having machine learning, data science and
            artificial intelligence in it and respond to them'''
        
        since_id = self.get_last_since_id()
        results = api.search(q=self.search_query, since_id = since_id,lang='en', tweet_mode='extended')
        for tweet in reversed(results):
            if tweet._json['in_reply_to_status_id'] is not None or tweet.user.id == self.me.id:
                continue
            else:
                try:
                    logging.info(f'found a tweet by @{tweet.user.screen_name}')
                    time.sleep(3)
                    tweet.retweet()
                    tweet.favorite()
                    logging.info(f'successfully liked and retweeted post made by @{tweet.user.screen_name}')
                except tweepy.TweepError:
                    logging.error('error while liking and retweeting', exc_info=True)
            time.sleep(30)
            self.new_since_id.append(tweet._json['id'])
        else:
            logging.info("Done checking for recent tweets on data science, machine learning or AI")

        if len(self.new_since_id) != 0:
            self.save_last_since_id(max(self.new_since_id))
        self.new_since_id.clear()

    def respond_to_dsc_handles(self):
        '''This method retrieves information from dsc handles in various nigeria instituitions and respond to it'''
        
        since_id = self.get_last_since_id()
        dsc_handles = json.load(open(self.dsc_handles_filename))['handles']
        for dsc in dsc_handles:
            tweets = api.user_timeline(screen_name= dsc, since_id=since_id, tweet_mode='extended')
            for tweet in reversed(tweets):
                if tweet.in_reply_to_status_id is not None:
                    continue
                if any(key in tweet.full_text.lower() for key in self.keywords):
                    try:
                        logging.info(f'found a new tweet on {dsc}\'s timeline....')
                        time.sleep(2)
                        tweet.retweet()
                        tweet.favorite()
                        logging.info(f'successfully retweeted and liked this tweet by @{tweet.user.screen_name}')
                    except tweepy.TweepError:
                        logging.error(f'Error while retweeting and liking', exc_info=True)
                self.new_since_id.append(tweet.id)
            time.sleep(2)
            logging.info(f'Done checking {dsc}\'s timeline found no new tweet ')
        if len(self.new_since_id) != 0:
            self.save_last_since_id(max(self.new_since_id))
        self.new_since_id.clear()
        
    def run_dsc_bot(self):
        '''This method combines the three main methods and run them'''
        
        while True:
            logging.info('DSCFUTA BOT ACTIVATED')
            time.sleep(2)
            self.respond_to_dscfuta_instructors()
            
            logging.info('DSCFUTA BOT concluded search on dsc futa instructor\'s timeline')
            time.sleep(5)
            self.respond_to_dsc_handles()
            
            logging.info('I have concluded searches on official DSC\'s account timeline.....')
            time.sleep(5)
            self.respond_to_keywords()
            
            logging.info('I am done searching for related tweets on ML,AI and DS.....')
            logging.info('\nDSCFUTA BOT Temporarily deactivated, will resume in the next 1minute.......')
            time.sleep(60)






since_id = 'since_id.txt'
instructor_handles = 'instructors.json'
dsc_handles = 'dsc_handles.json'
keywords = ['dsc', 'developer student club','developer', '#datascience', 'data science', 'machine learning', 'machineleanring', '#python']
search_query = f''' "Data Science" OR "data science" OR "#DataScience" OR "Machine Learning" OR "#machinelearning"
                      OR "machine learning" OR "#MachineLearning" -filter:retweets'''
if __name__ == "__main__":
    api = create_api()
    dscbot = DscFutaBot(api,since_id,instructor_handles,dsc_handles,keywords,search_query)
    dscbot.run_dsc_bot()

  