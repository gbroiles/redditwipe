#! /usr/bin/env python3
# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,no-member,unused-argument,unused-variable,missing-class-docstring,line-too-long
import os
import random
import sys
import praw


def main():
    try:
        clientid = os.environ["REDDIT_CLIENT_ID"]
        clientsecret = os.environ["REDDIT_CLIENT_SECRET"]
        username = os.environ["REDDIT_USERNAME"]
        password = os.environ["REDDIT_PASSWORD"]
    except KeyError:
        sys.exit(1)
    reddit = praw.Reddit(
        client_id=clientid,
        client_secret=clientsecret,
        user_agent=os.environ.get("REDDIT_USER_AGENT", "redditwipe"),
        username=username,
        password=password,
    )

    x = random.randint(1, 4)

    if x == 1:
        submissions = list(reddit.redditor(username).submissions.new(limit=None))
        if not submissions:
            print("No submissions found, skipping reply.", file=sys.stderr)
            return
        try:
            random.choice(submissions).reply(Random_words())
        except Exception as e:
            print(
                "got an error replying to an existing submission. [{}]".format(str(e)),
                file=sys.stderr,
            )

    elif x == 2:
        comments = list(reddit.redditor(username).comments.new(limit=None))
        if not comments:
            print("No comments found, skipping reply.", file=sys.stderr)
            return
        try:
            random.choice(comments).reply(Random_words())
        except Exception as e:
            print(
                "got an error replying to an existing comment. [{}]".format(str(e)),
                file=sys.stderr,
            )

    else:
        try:
            reddit.subreddit("reddit_api_test").submit(Random_words(), selftext=Random_words())
        except Exception as e:
            print(
                "got an error making a new submission. [{}]".format(str(e)),
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
