#! /usr/bin/env python3
#pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,no-member,unused-argument,unused-variable,missing-class-docstring
import os
import random
import wx
import praw

class mainWindow(wx.Frame):
    def __init__(self, parent, title):
        super(mainWindow, self).__init__(parent, title=title, style=wx.DEFAULT_FRAME_STYLE,
                                         size=(525, 300))
        self.Centre()
        self.InitUI()

    def InitUI(self):
#        menubar = wx.MenuBar()
#        fileMenu = wx.Menu()
#        fileItem = fileMenu.Append(wx.ID_EXIT, 'E&xit', 'Exit application')
#        menubar.Append(fileMenu, '&File')
#        self.SetMenuBar(menubar)
#        self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)
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

        btn1 = wx.Button(panel, label='Login')
        sizer.Add(btn1, pos=(0, 4), flag=wx.ALL, border=5)

        self.comments = wx.CheckBox(panel, label="Wipe comments")
        sizer.Add(self.comments, pos=(1, 2), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        self.submissions = wx.CheckBox(panel, label="Wipe submissions")
        sizer.Add(self.submissions, pos=(1, 1), flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)

        btn2 = wx.Button(panel, label='Wipe')
        sizer.Add(btn2, pos=(1, 4), flag=wx.ALL, border=5)

        self.found = wx.TextCtrl(panel)
        sizer.Add(self.found, pos=(2, 0), span=(0, 5),
                  flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TE_READONLY, border=5)

        self.tc2 = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.tc2, pos=(3, 0), span=(0, 5),
                  flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=5)

        sizer.AddGrowableRow(3)

        panel.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.Login, id=btn1.GetId())
        self.Bind(wx.EVT_BUTTON, self.Process, id=btn2.GetId())
        self.loggedin = False

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
        comment_count = 0
        for reply in self.reddit.redditor(self.uname.GetValue()).comments.new(limit=self.limitation):
            comment_count += 1
        return comment_count

    def get_submission_total(self, e):
        submission_count = 0
        for submission in self.reddit.redditor(self.uname.GetValue()).submissions.new(limit=self.limitation):
            submission_count += 1
        return submission_count

    def start_delete_comments(self, e):
        comment_count = self.get_comment_total(self)
        while comment_count > 0:
            for comment in self.reddit.redditor(self.uname.GetValue()).comments.new(limit=self.limitation):
                comment_to_delete = self.reddit.comment(comment)
                comment_to_delete.edit(self.Random_words())
                comment_to_delete.edit(self.Random_words())
                comment_to_delete.delete()
                comment_count -= 1

    def start_delete_submissions(self, e):
        submission_count = self.get_submission_total(self)
        while submission_count > 0:
            for submission in self.reddit.redditor(self.uname.GetValue()).submissions.new(limit=self.limitation):
                submission_to_delete = self.reddit.submission(submission)
                submission_to_delete.edit(self.Random_words())
                submission_to_delete.edit(self.Random_words())
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

    @staticmethod
    def Random_words():
        return ' '.join(random.choices(phonetic, k=5))

    def Login(self, e):
        sb = self.GetStatusBar()
        sb.SetStatusText('Logging in...')
        clientid = os.environ["REDDIT_CLIENT_ID"]
        clientsecret = os.environ["REDDIT_CLIENT_SECRET"]
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

def main():
    app = wx.App()
    frame = mainWindow(None, title='Reddit wipe utility')
    frame.Show()
    app.MainLoop()

if __name__ == '__main__':
    main()
