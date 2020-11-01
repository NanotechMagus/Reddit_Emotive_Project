#! python3.exe

import json
import datetime as dt
from pathlib import Path
# import logging


class initMe:

    def __init__(self, loc='./settings.json'):
        with open(Path(loc)) as f:
            self.initparms = json.load(f)
        if not self.initparms["creds"]["client_secret"]:
            with open(Path("./settings-test.json")) as g:
                self.initparms = json.load(g)


class RScraper:

    def __init__(self, creds = None):
        self.__creds = creds
        if not self.__creds:
            self.__creds = initMe().initparms["creds"]
        self.session = self.__get_session()
        self.analyze = Analyzer()

    def __get_session(self):
        import praw
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
            print(f"{err} has occured, could not get session.")
        finally:
            return reddit

    def __checkme(self, checkme):
        if checkme:
            if isinstance(checkme, dt.datetime):
                return checkme.isoformat()
            else:
                return checkme
        else:
            return ""

    def topic_scraper(self, sub, limit, subdict: dict):
        print(f"Scraping {sub} {limit} times at {dt.datetime.now()}")
        try:
            subreddit = self.session.subreddit(sub)

            for submission in subreddit.new(limit=limit):
                subdict["title"].append(self.__checkme(submission.title))
                subdict["score"].append(self.__checkme(submission.score))
                subdict["id"].append(self.__checkme(submission.id))
                subdict["url"].append(self.__checkme(submission.url))
                subdict["comms_num"].append(self.__checkme(submission.num_comments))
                subdict["created"].append(self.__checkme(dt.datetime.fromtimestamp(submission.created)))
                subdict["body"].append(self.__checkme(submission.selftext))
                if submission.num_comments:
                    cf, cs = self.comm_scraper(submission.id)
                    subdict["comments"].append(self.__checkme(cf))
                    subdict["comments_escore"].append(self.__checkme(cs))
                else:
                    subdict["comments"].append("")
                    subdict["comments_escore"].append("")
                subdict["title_escore"].append(self.__checkme(self.analyze.compare(submission.title)))
                subdict["body_escore"].append(self.__checkme(self.analyze.compare(submission.selftext)))
            return subdict
        except Exception as err:
            print(f"There's a problem here: {err}")
            return None

    def comm_scraper(self, sid):
        from praw.models import MoreComments
        subcom = self.session.submission(id=sid).comments
        subcom.replace_more(limit=0)
        commforest = []
        commscore = {
            "trust": 0,
            "anger": 0,
            "anticipation": 0,
            "disgust": 0,
            "fear": 0,
            "joy": 0,
            "negative": 0,
            "positive": 0,
            "sadness": 0,
            "surprise": 0
        }
        icount = 0
        for comment in subcom.list():
            if comment.body:
                commforest.append(comment.body)
                commscore = self.analyze.compare(comment.body, commscore)
                icount += 1
        print(f"{icount} comments scraped!")
        return commforest, commscore

    def out_write(self, outdata, outloc=None):
        if not outloc:
            outloc = Path('./data/outfile.json')
        print(f"Writing data to outfile.json at {dt.datetime.now()}")

        try:
            with open(outloc, 'w') as outfile:
                json.dump(outdata, outfile, indent=4, separators=(',', ': '))
            return True
        except Exception as err:
            print(f"Error in writing outfile: {err}")
            return False


class Analyzer:

    def __init__(self, emotiveloc=None):
        if not emotiveloc:
            self.__eloc = Path('./data/NRC-Emotion-Lexicon-Wordlevel-v0.92.txt')
        else:
            self.__eloc = Path(emotiveloc)
        self.__edataset = self.__getdataset()

    def __getdataset(self):
        print("Getting Comparitive Emotive dataset ready!")
        dataset = {}
        f = open(self.__eloc, "r")
        f.readline()
        for lines in f:
            a, b, c = lines.split("\t")
            if not a in dataset.keys():
                dataset[a] = {
                    b: int(c.replace("\n", ""))
                }
            else:
                dataset[a][b] = int(c.replace("\n", ""))
        print("Dataset prepared.")
        return dataset

    def compare(self, topic, totalemotion=""):
        if not totalemotion:
            totalemotion = {
                "trust": 0,
                "anger": 0,
                "anticipation": 0,
                "disgust": 0,
                "fear": 0,
                "joy": 0,
                "negative": 0,
                "positive": 0,
                "sadness": 0,
                "surprise": 0
            }
        topicstrip = self.textstrip(list(topic.split(" ")))
        for x in topicstrip:
            if x in self.__edataset.keys():
                for y in self.__edataset[x].keys():
                    if self.__edataset[x][y] == 1:
                        totalemotion[y] += 1
        return totalemotion

    def textstrip(self, topic):
        import string
        translator = str.maketrans({key: None for key in string.punctuation})
        return [s.lower().translate(translator) for s in topic]


class DataFrame:

    def __init__(self, of=None):
        if not of:
            self.__of = Path('.')
        else:
            self.__of = of

    def framing(self, infile):
        import pandas as pd
        print(f"Creating dataframe!")
        return pd.DataFrame(infile)

    def csv_out(self, frame, name):
        pathing = f"./data/{name}-dataframe.csv"
        print(f"Writing {name} to {pathing}")
        frame.to_csv(Path(pathing), index=False)
        return 0