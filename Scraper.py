#! python3.exe


import logging
import datetime as dt
from core import core

'''
Following this concept:
- iterate through each subreddit for the past year (sorted by date?) and each comment.
- Output every topic and body,
- Write to a file as JSON
- compare with NRC to search for words relating to its main emotional content and index responses within dict
- Separate as "response to wholesome // toxic // neutral"
- attribute it to a spreadsheet,
- aggregate data by day,
- create charts to best reflect the attitude of the forum - different charts per:
-- Weight of wholesome vs neutral vs toxic
-- -- different chart per forum
-- -- -- historical and "trending" (coinciding with occasions // incidents)
-- -- -- keywords -- repeated words -- maybe a word cloud? (See extraneous)
-- -- -- Chart for title versus comments (to better answer "Do toxic topics beget toxic comments)
-- -- different chart per sorting technique (is this necessary?)
Extraneous analyses;
-- Wholesomeness/Toxicity of individuals -- are individuals toxic or is sentiment toxic?
-- Wholesomeness/Toxicity as a trend
-- Wholesomeness/Toxicity based on media (image / uploaded video / youtube video / text)

Lastly, use matplotlib and pandas to create the charts // word cloud
-- note:  To make the word cloud, we could split the topic and comment bodies and pipe them out to a .txt document
-- note:  Also, perhaps we can do a full analysis of the overall wholesomeness//toxicity of the entirety of the sample
-- note:  make sure to have important and relevant data in the JSON data file, such as:
-- --        last topic//comment date (continue to append date for every count) - overall for sub, overall for topic
-- --        <add more things here>
Look into breaking this out into classes, which will allow me to encapsulate the function better -- only if necessary
'''

sublist = [
    "starcitizen",
    "politics",
    "ffxiv",
    "thedivision",
    "starcitizen_refunds",
    "foxes",
    "space",
    "wholesomememes",
    "MurderedByWords",
    "LeopardsAteMyFace"
]
limit = 1000


def main():
    # TODO: Set up a help and man page for this thing

    start_logging()

    red = core.RScraper()
    df = core.DataFrame()
    subdict = {}
    now = dt.datetime.now()
    logging.info(f"Starting pull at {now}")

    for subs in sublist:
        subnow = dt.datetime.now()
        logging.info(f"Polling {subs} at {subnow}:")
        subdict[subs] = {
            "title": [],
            "score": [],
            "url": [],
            "comms_num": [],
            "created": [],
            "id": [],
            "body": [],
            "comments": [],
            "title_escore": [],
            "body_escore": [],
            "comments_escore": []
        }

        red.topic_scraper(subs, limit, subdict[subs])

        print(f"{subs} has fininshed polling.  Total time: {str(dt.datetime.now() - subnow)}")

        dataframe = df.framing(subdict[subs])
        print(f"Dataframe created for {subs}")
        df.csv_out(dataframe, subs)
        print(f"Output complete!")

    print("Writing subdict to disk")
    red.out_write(subdict)
    print("Work complete")

    return 0


def start_logging():
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    for logger_name in ("praw", "prawcore"):
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.WARN)
        logger.addHandler(handler)


if __name__ == "__main__":
    main()

