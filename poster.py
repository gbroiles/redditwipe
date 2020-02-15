#! /usr/bin/env python3
#pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,no-member,unused-argument,unused-variable,missing-class-docstring,line-too-long
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
        print('Environment variables REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set.')
        sys.exit(1)
    try:
        user_agent = os.environ["REDDIT_USER_AGENT"]
    except KeyError:
        user_agent = 'redditwipe'
    limitation = None
    print("logging in... ",end='')
    reddit = praw.Reddit(client_id=clientid, client_secret=clientsecret,
                              user_agent=user_agent, username=username,
                              password=password)
    print("done.")
    submissions=[]

    for submission in reddit.redditor(username).submissions.new(limit=limitation):
        submissions.append(submission)

    choice = random.randint(0,len(submissions)-1)
    try:
        submissions[choice].reply(Random_words())
    except:
        pass

    comments=[]

    for comment in reddit.redditor(username).comments.new(limit=limitation):
        comments.append(comment)

    choice = random.randint(0,len(comments)-1)
    try:
        comments[choice].reply(Random_words())
    except:
        pass

    title = Random_words()
    selftext = Random_words()
    try:
        reddit.subreddit('reddit_api_test').submit(title, url=url)
    except:
        pass



phonetic = ['alfa', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel',
            'india', 'juliett', 'kilo', 'lima', 'mike', 'november', 'oscar',
            'papa', 'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor',
            'whiskey', 'x-ray', 'yankee', 'zulu']

def Random_words():
    return ' '.join(random.choices(phonetic, k=5))

if __name__ == '__main__':
    main()
