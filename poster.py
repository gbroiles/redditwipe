#! /usr/bin/env python3
# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,no-member,unused-argument,unused-variable,missing-class-docstring,line-too-long
import datetime
import os
import random
import sys
import praw
import pprint


def main():
    try:
        clientid = os.environ["REDDIT_CLIENT_ID"]
        clientsecret = os.environ["REDDIT_CLIENT_SECRET"]
        username = os.environ["REDDIT_USERNAME"]
        password = os.environ["REDDIT_PASSWORD"]
    except KeyError:
        #        print('Environment variables REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set.')
        sys.exit(1)
    try:
        user_agent = os.environ["REDDIT_USER_AGENT"]
    except KeyError:
        user_agent = "redditwipe"
    limitation = None
    reddit = praw.Reddit(
        client_id=clientid,
        client_secret=clientsecret,
        user_agent=user_agent,
        username=username,
        password=password,
    )

    x = random.randint(1, 4)

    if x == 1:
        submissions = []
        for submission in reddit.redditor(username).submissions.new(limit=limitation):
            submissions.append(submission)
        choice = random.randint(0, len(submissions) - 1)
        try:
            submissions[choice].reply(Random_words())
        except Exception as e:
            print(
                "got an error replying to an existing submission. [{}]".format(
                    e.args[0]
                ),
                file=sys.stderr,
            )

    elif x == 2:
        comments = []
        for comment in reddit.redditor(username).comments.new(limit=limitation):
            comments.append(comment)
        choice = random.randint(0, len(comments) - 1)
        try:
            comments[choice].reply(Random_words())
        except Exception as e:
            print(
                "got an error replying to an existing comment. [{}]".format(e.args[0]),
                file=sys.stderr,
            )

    else:
        title = Random_words()
        selftext = Random_words()
        try:
            reddit.subreddit("reddit_api_test").submit(title, selftext=selftext)
        except Exception as e:
            print(
                "got an error making a new submission. [{}]".format(e.args[0]),
                file=sys.stderr,
            )


phonetic = [
    "alfa",
    "bravo",
    "charlie",
    "delta",
    "echo",
    "foxtrot",
    "golf",
    "hotel",
    "india",
    "juliet",
    "kilo",
    "lima",
    "mike",
    "november",
    "oscar",
    "papa",
    "quebec",
    "romeo",
    "sierra",
    "tango",
    "uniform",
    "victor",
    "whiskey",
    "x-ray",
    "yankee",
    "zulu",
]


def Random_words():
    return " ".join(random.choices(phonetic, k=random.randint(3, 8)))


if __name__ == "__main__":
    main()
