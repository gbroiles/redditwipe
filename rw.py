#! /usr/bin/env python3
#pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,no-member,unused-argument,unused-variable,missing-class-docstring,line-too-long
import datetime
import os
import random
import sys
import wx
import praw

class mainWindow(wx.Frame):
    def __init__(self, parent, title):
        super(mainWindow, self).__init__(parent, title=title, style=wx.DEFAULT_FRAME_STYLE,
                                         size=(525, 600))
        self.Centre()
        self.InitUI()

    def InitUI(self):
        self.CreateStatusBar()

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        st1 = wx.StaticText(panel, label='Username:')
        sizer.Add(st1, pos=(0, 0), flag=wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.uname = wx.TextCtrl(panel)
        username = os.environ["REDDIT_USERNAME"]
        self.uname.SetValue(username)
        sizer.Add(self.uname, pos=(0, 1), flag=wx.ALL|wx.ALIGN_LEFT, border=5)

        st2 = wx.StaticText(panel, label='Password:')
        sizer.Add(st2, pos=(0, 2), flag=wx.ALL|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.pword = wx.TextCtrl(panel)
        password = os.environ["REDDIT_PASSWORD"]
        self.pword.SetValue(password)
        sizer.Add(self.pword, pos=(0, 3), flag=wx.ALL|wx.ALIGN_LEFT, border=5)

        btn1 = wx.Button(panel, label='Update')
        sizer.Add(btn1, pos=(1, 4), flag=wx.ALL, border=5)

        self.comments = wx.CheckBox(panel, label="Wipe comments")
        sizer.Add(self.comments, pos=(1, 2), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.submissions = wx.CheckBox(panel, label="Wipe submissions")
        sizer.Add(self.submissions, pos=(1, 1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.verbose = wx.CheckBox(panel, label="Verbose output")
        self.verbose.SetValue(True)
        sizer.Add(self.verbose, pos=(1, 3), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        btn2 = wx.Button(panel, label='Wipe')
        sizer.Add(btn2, pos=(2, 4), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.rbox = wx.RadioBox(panel, label='Age for deletion', style=wx.RA_SPECIFY_ROWS,
                                choices=('Any age', 'Older than X minutes'), majorDimension=1)
        sizer.Add(self.rbox, pos=(2, 0), span=(0, 3), flag=wx.ALL, border=5)

        self.age = wx.SpinCtrl(panel, value="0", max=99999999, name="Min age to delete", style=wx.ALIGN_RIGHT)
        sizer.Add(self.age, pos=(2, 3), flag=wx.ALIGN_CENTER_VERTICAL|wx.ALL)

        legendtext = ''.join('1 day = {:,} minutes, 1 month = {:,} minutes, 1 year = {:,} minutes'.format(60*24, 60*24*30, 60*24*365))
        legend = wx.StaticText(panel, label=legendtext)
        sizer.Add(legend, pos=(3, 0), span=(0, 5), flag=wx.ALL|wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.found = wx.TextCtrl(panel)
        sizer.Add(self.found, pos=(4, 0), span=(0, 5),
                  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TE_READONLY, border=5)

        self.tc2 = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.tc2, pos=(5, 0), span=(0, 5),
                  flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)

        sizer.AddGrowableRow(5)

        panel.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.Login, id=btn1.GetId())
        self.Bind(wx.EVT_BUTTON, self.Process, id=btn2.GetId())
        self.Bind(wx.EVT_SPINCTRL, self.UpdateAge)
        self.loggedin = False

    def UpdateAge(self, e):
        if self.age.GetValue() > 0:
            self.rbox.SetSelection(1)
        else:
            self.rbox.SetSelection(0)

    def OnQuit(self, e):
        self.Close()

    def Process(self, e):
        sb = self.GetStatusBar()
        if self.submissions.GetValue:
            sb.SetStatusText('Wiping submissions ...')
            self.start_delete_submissions(self)
        if self.comments.GetValue:
            sb.SetStatusText('Wiping comments ...')
            self.start_delete_comments(self)
        self.Update_counts()

    def get_comment_total(self, e):
        if self.rbox.GetSelection() == 1:
            age = self.age.GetValue()
        else:
            age = 0
        comment_count = 0
        textbox = self.tc2
        now = datetime.datetime.now().timestamp()
        expire_seconds = age * 60
        if self.verbose.GetValue():
            if age > 0:
                textbox.AppendText('Looking for comments older than {:0,} minutes from {}\n'.format(age, self.uname.GetValue()))
            else:
                textbox.AppendText('Looking for all comments from {}\n'.format(self.uname.GetValue()))
        for reply in self.reddit.redditor(self.uname.GetValue()).comments.new(limit=self.limitation):
            comment_age = now-reply.created_utc
            if self.verbose.GetValue():
                subreddit = reply.subreddit
                textbox.AppendText('Found {} in /r/{} it is {:,} minutes old.\n'.format(reply.id, subreddit, int(comment_age/60)))
            if age == 0 or comment_age > expire_seconds:
                comment_count += 1
        return comment_count

    def get_submission_total(self, e):
        age = self.age.GetValue()
        submission_count = 0
        textbox = self.tc2
        now = datetime.datetime.now().timestamp()
        expire_seconds = age * 60
        if self.verbose.GetValue():
            if age > 0:
                textbox.AppendText('Looking for submissions older than {:0,} minutes from {}\n'.format(age, self.uname.GetValue()))
            else:
                textbox.AppendText('Looking for all submissions from {}\n'.format(self.uname.GetValue()))
        for submission in self.reddit.redditor(self.uname.GetValue()).submissions.new(limit=self.limitation):
            submission_age = now-submission.created_utc
            if self.verbose.GetValue():
                subreddit = submission.subreddit
                textbox.AppendText('Found {} in /r/{} it is {:,} minutes old.\n'.format(submission.id, subreddit,
                                                                                        int(submission_age/60)))
            if age == 0 or submission_age > expire_seconds:
                submission_count += 1
        return submission_count

    def start_delete_comments(self, e):
        age = self.age.GetValue()
        now = datetime.datetime.now().timestamp()
        expire_seconds = age * 60
        comment_count = self.get_comment_total(self)
        textbox = self.tc2
        while comment_count > 0:
            for comment in self.reddit.redditor(self.uname.GetValue()).comments.new(limit=self.limitation):
                comment_to_delete = self.reddit.comment(comment)
                comment_age = now - comment_to_delete.created_utc
                if age == 0 or comment_age > expire_seconds:
                    if self.verbose.GetValue():
                        textbox.AppendText('Working on comment {}: {}\n'.format(comment_to_delete.id, comment_to_delete.body[0:15]))
                        for i in range(2):
                            comment_to_delete.edit(self.Random_words())
                            if self.verbose.GetValue():
                                textbox.AppendText('Working on comment {}: Changed text to {}\n'.format(comment_to_delete.id, comment_to_delete.body))
                    textbox.AppendText('Deleted comment {}\n'.format(comment_to_delete.id))
                    comment_to_delete.delete()
                comment_count -= 1

    def start_delete_submissions(self, e):
        age = self.age.GetValue()
        now = datetime.datetime.now().timestamp()
        expire_seconds = age * 60
        submission_count = self.get_submission_total(self)
        textbox = self.tc2
        while submission_count > 0:
            for submission in self.reddit.redditor(self.uname.GetValue()).submissions.new(limit=self.limitation):
                submission_to_delete = self.reddit.submission(submission)
                submission_age = now - submission_to_delete.created_utc
                if age == 0 or submission_age > expire_seconds:
                    if self.verbose.GetValue():
                        textbox.AppendText('Working on submission {}: {}'.format(submission_to_delete.id, submission_to_delete.title))
                        if submission_to_delete.post_hint == "self":
                            textbox.AppendText(' text post\n')
                            for i in range(2):
                                submission_to_delete.edit(self.Random_words())
                                if self.verbose.GetValue():
                                    textbox.AppendText('Working on submission {}: Changed text to {}\n'.format(submission_to_delete.id, submission_to_delete.selftext))
                        else:
                            textbox.AppendText(' link post, cannot overwrite\n')
                    textbox.AppendText('Deleted submission {}\n'.format(submission_to_delete.id))
                    submission_to_delete.delete()
                submission_count -= 1

    def Update_counts(self):
        sb = self.GetStatusBar()
        sb.SetStatusText('Getting submission/comment count ...')
        comments = self.get_comment_total(self.reddit)
        submissions = self.get_submission_total(self.reddit)
        result = ('Found {} submissions, {} comments'.format(submissions, comments))
        self.found.SetValue(result)
        sb.SetStatusText(result)

    def Login(self, e):
        sb = self.GetStatusBar()
        sb.SetStatusText('Logging in...')
        try:
            clientid = os.environ["REDDIT_CLIENT_ID"]
            clientsecret = os.environ["REDDIT_CLIENT_SECRET"]
        except KeyError:
            print('Environment variables REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set.')
            sys.exit(1)
        try:
            user_agent = os.environ["REDDIT_USER_AGENT"]
        except KeyError:
            user_agent = 'redditwipe'
        self.limitation = None
        self.reddit = praw.Reddit(client_id=clientid, client_secret=clientsecret,
                                  user_agent=user_agent, username=self.uname.GetValue(),
                                  password=self.pword.GetValue())
        sb.SetStatusText('Logged in.')
        self.Update_counts()
        self.loggedin = True

phonetic = ['alfa', 'bravo', 'charlie', 'delta', 'echo', 'foxtrot', 'golf', 'hotel',
            'india', 'juliett', 'kilo', 'lima', 'mike', 'november', 'oscar',
            'papa', 'quebec', 'romeo', 'sierra', 'tango', 'uniform', 'victor',
            'whiskey', 'x-ray', 'yankee', 'zulu']

def Random_words():
    return ' '.join(random.choices(phonetic, k=5))

def main():
    app = wx.App()
    frame = mainWindow(None, title='Reddit wipe utility')
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
