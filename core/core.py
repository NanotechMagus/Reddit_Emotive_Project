#! python3.exe

import praw
import json
import datetime as dt
from pathlib import Path
import logging


class initMe:

    def __init__(self, loc='./settings.json'):
        with open(Path(loc)) as f:
            self.initparms = json.load(f)


class RScraper:

    def __init__(self, creds = None):
        self.__creds = creds
        if not self.__creds:
            self.__creds = initMe().initparms["creds"]
        self.session = self.__get_session()

    def __get_session(self):
        reddit = None
        try:
            reddit = praw.Reddit(
                client_id=self.__creds['client_id'],
                client_secret=self.__creds['client_secret'],
                user_agent=self.__creds['user_agent'],
                username=self.__creds['username'],
                password=self.__creds['password']
            )
        except Exception as err:
            logging.warning(f"{err} has occured")
        finally:
            return reddit

    def __checkme(self, checkme):
        if checkme:
            return checkme
        else:
            return ""

    def topic_scraper(self, sub, limit, subdict):
        try:
            subreddit = self.session.subreddit(sub)

            for submission in subreddit.new(limt=limit):
                subdict["title"].append(self.__checkme(submission.title))
                subdict["score"].append(self.__checkme(submission.score))
                subdict["id"].append(self.__checkme(submission.id))
                subdict["url"].append(self.__checkme(submission.url))
                subdict["comms_num"].append(self.__checkme(submission.num_comments))
                subdict["created"].append(self.__checkme(submission.created))
                subdict["body"].append(self.__checkme(submission.selftext))
                subdict["comments"].append(
                    self.__checkme(self.comment_scraper(submission.id))
                )
        except Exception as err:
            return None

    def comment_scraper(self, sid):
        commforest = []
        submission = self.session.subreddit(sid)
        comments = submission.comments
        for comment in comments:
            self.getSubComments(comment, commforest)
        return commforest

    def getSubComments(self, comment, allComments):
        allComments.append(comment)
        if not hasattr(comment, "replies"):
            replies = comment.comments()
            logging.info("Fetching (" + str(len(allComments)) + " comments fetched total)")
        else:
            replies = comment.replies
        for child in replies:
            self.getSubComments(child, allComments)
        return allComments

    def out_write(self, outdata):
        logging.info(f"Writing data to outfile.json at {dt.datetime.now()}")
        try:
            with open('outfile.json', 'w') as outfile:
                json.dump(outdata, outfile)
            return True
        except Exception as err:
            logging.warning(f"Error in writing outfile: {err}")
            return False
