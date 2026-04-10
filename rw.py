#! /usr/bin/env python3
# pylint: disable=missing-module-docstring,missing-function-docstring,invalid-name,no-member,unused-argument,unused-variable,missing-class-docstring,line-too-long
import concurrent.futures
import datetime
import os
import random
import threading
import wx
import praw


class mainWindow(wx.Frame):
    def __init__(self, parent, title):
        super(mainWindow, self).__init__(
            parent, title=title, style=wx.DEFAULT_FRAME_STYLE, size=(525, 600)
        )
        self.Centre()
        self.InitUI()

    def InitUI(self):
        self.sb = self.CreateStatusBar()
        self._count_lock = threading.Lock()

        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(5, 5)

        st1 = wx.StaticText(panel, label="Username:")
        sizer.Add(
            st1,
            pos=(0, 0),
            flag=wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
            border=5,
        )

        self.uname = wx.TextCtrl(panel)
        self.uname.SetValue(os.environ.get("REDDIT_USERNAME", ""))
        sizer.Add(self.uname, pos=(0, 1), flag=wx.ALL | wx.ALIGN_LEFT, border=5)

        st2 = wx.StaticText(panel, label="Password:")
        sizer.Add(
            st2,
            pos=(0, 2),
            flag=wx.ALL | wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL,
            border=5,
        )

        self.pword = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.pword.SetValue(os.environ.get("REDDIT_PASSWORD", ""))
        sizer.Add(self.pword, pos=(0, 3), flag=wx.ALL | wx.ALIGN_LEFT, border=5)

        btn1 = wx.Button(panel, label="Update")
        sizer.Add(btn1, pos=(1, 4), flag=wx.ALL, border=5)

        self.comments = wx.CheckBox(panel, label="Wipe comments")
        sizer.Add(
            self.comments, pos=(1, 2), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5
        )

        self.submissions = wx.CheckBox(panel, label="Wipe submissions")
        sizer.Add(
            self.submissions,
            pos=(1, 1),
            flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL,
            border=5,
        )

        self.verbose = wx.CheckBox(panel, label="Verbose output")
        self.verbose.SetValue(True)
        sizer.Add(
            self.verbose, pos=(1, 3), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5
        )

        self.wipe_btn = wx.Button(panel, label="Wipe")
        self.wipe_btn.Disable()  # enabled after successful login
        sizer.Add(self.wipe_btn, pos=(2, 4), flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL, border=5)

        self.rbox = wx.RadioBox(
            panel,
            label="Age for deletion",
            style=wx.RA_SPECIFY_ROWS,
            choices=("Any age", "Older than X minutes"),
            majorDimension=1,
        )
        sizer.Add(self.rbox, pos=(2, 0), span=(0, 3), flag=wx.ALL, border=5)

        self.age = wx.SpinCtrl(
            panel,
            value="0",
            max=99999999,
            name="Min age to delete",
            style=wx.ALIGN_RIGHT,
        )
        sizer.Add(self.age, pos=(2, 3), flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)

        legendtext = "1 day = {:,} minutes, 1 month = {:,} minutes, 1 year = {:,} minutes".format(
            60 * 24, 60 * 24 * 30, 60 * 24 * 365
        )
        legend = wx.StaticText(panel, label=legendtext)
        sizer.Add(
            legend,
            pos=(3, 0),
            span=(0, 5),
            flag=wx.ALL | wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL,
            border=5,
        )

        self.found = wx.TextCtrl(panel)
        sizer.Add(
            self.found,
            pos=(4, 0),
            span=(0, 5),
            flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TE_READONLY,
            border=5,
        )

        self.tc2 = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(
            self.tc2,
            pos=(5, 0),
            span=(0, 5),
            flag=wx.EXPAND | wx.LEFT | wx.RIGHT,
            border=5,
        )

        sizer.AddGrowableRow(5)
        panel.SetSizer(sizer)

        self.Bind(wx.EVT_BUTTON, self.Login, id=btn1.GetId())
        self.Bind(wx.EVT_BUTTON, self.Process, id=self.wipe_btn.GetId())
        self.Bind(wx.EVT_SPINCTRL, self.UpdateAge)

    def UpdateAge(self, e):
        if self.age.GetValue() > 0:
            self.rbox.SetSelection(1)
        else:
            self.rbox.SetSelection(0)

    def _age_filter(self):
        """Returns the minimum age in seconds, or 0 for any age. Call from main thread only."""
        if self.rbox.GetSelection() == 1:
            return self.age.GetValue() * 60
        return 0

    def Process(self, e):
        # Capture all UI state on the main thread before handing off to the worker.
        do_submissions = self.submissions.GetValue()
        do_comments = self.comments.GetValue()
        expire_seconds = self._age_filter()
        verbose = self.verbose.GetValue()
        username = self.uname.GetValue()

        what = []
        if do_submissions:
            what.append("submissions")
        if do_comments:
            what.append("comments")
        if not what:
            return

        age_desc = ""
        if expire_seconds > 0:
            age_desc = " older than {:,} minutes".format(expire_seconds // 60)
        msg = "Delete all {}{} for {}?\n\nThis cannot be undone.".format(
            " and ".join(what), age_desc, username
        )
        dlg = wx.MessageDialog(
            self, msg, "Confirm Wipe", wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        confirmed = dlg.ShowModal() == wx.ID_YES
        dlg.Destroy()
        if not confirmed:
            return

        self.wipe_btn.Disable()
        threading.Thread(
            target=self._wipe_worker,
            args=(do_submissions, do_comments, expire_seconds, verbose, username),
            daemon=True,
        ).start()

    def _wipe_worker(self, do_submissions, do_comments, expire_seconds, verbose, username):
        try:
            if do_submissions:
                wx.CallAfter(self.sb.SetStatusText, "Wiping submissions ...")
                self.start_delete_submissions(expire_seconds, verbose, username)
            if do_comments:
                wx.CallAfter(self.sb.SetStatusText, "Wiping comments ...")
                self.start_delete_comments(expire_seconds, verbose, username)
            self._fetch_and_show_counts(expire_seconds, username)
        except Exception as exc:
            wx.CallAfter(self.tc2.AppendText, "Wipe error: {}\n".format(exc))
            wx.CallAfter(self.sb.SetStatusText, "Wipe failed: {}".format(exc))
        finally:
            wx.CallAfter(self.wipe_btn.Enable)

    def _get_comment_total(self, expire_seconds, username):
        count = 0
        for reply in self.reddit.redditor(username).comments.new(limit=None):
            comment_age = datetime.datetime.now().timestamp() - reply.created_utc
            if expire_seconds == 0 or comment_age > expire_seconds:
                count += 1
        return count

    def _get_submission_total(self, expire_seconds, username):
        count = 0
        for submission in self.reddit.redditor(username).submissions.new(limit=None):
            submission_age = datetime.datetime.now().timestamp() - submission.created_utc
            if expire_seconds == 0 or submission_age > expire_seconds:
                count += 1
        return count

    def start_delete_comments(self, expire_seconds, verbose, username):
        for comment in self.reddit.redditor(username).comments.new(limit=None):
            comment_age = datetime.datetime.now().timestamp() - comment.created_utc
            if expire_seconds == 0 or comment_age > expire_seconds:
                try:
                    if verbose:
                        wx.CallAfter(
                            self.tc2.AppendText,
                            "Working on comment {}: {}\n".format(comment.id, comment.body[:15]),
                        )
                    for _ in range(2):
                        comment.edit(Random_words())
                        if verbose:
                            wx.CallAfter(
                                self.tc2.AppendText,
                                "Working on comment {}: Changed text to {}\n".format(
                                    comment.id, comment.body
                                ),
                            )
                    comment.delete()
                    wx.CallAfter(
                        self.tc2.AppendText,
                        "Deleted comment {}\n".format(comment.id),
                    )
                except Exception as exc:
                    wx.CallAfter(
                        self.tc2.AppendText,
                        "Error on comment {}: {}\n".format(comment.id, exc),
                    )

    def start_delete_submissions(self, expire_seconds, verbose, username):
        for submission in self.reddit.redditor(username).submissions.new(limit=None):
            submission_age = datetime.datetime.now().timestamp() - submission.created_utc
            if expire_seconds == 0 or submission_age > expire_seconds:
                try:
                    if verbose:
                        kind = "text post" if submission.is_self else "link post, cannot overwrite"
                        wx.CallAfter(
                            self.tc2.AppendText,
                            "Working on submission {}: {} [{}]\n".format(
                                submission.id, submission.title, kind
                            ),
                        )
                    if submission.is_self:
                        for _ in range(2):
                            submission.edit(Random_words())
                            if verbose:
                                wx.CallAfter(
                                    self.tc2.AppendText,
                                    "Working on submission {}: Changed text to {}\n".format(
                                        submission.id, submission.selftext
                                    ),
                                )
                    submission.delete()
                    wx.CallAfter(
                        self.tc2.AppendText,
                        "Deleted submission {}\n".format(submission.id),
                    )
                except Exception as exc:
                    wx.CallAfter(
                        self.tc2.AppendText,
                        "Error on submission {}: {}\n".format(submission.id, exc),
                    )

    def UpdateCounts(self):
        # Capture UI state on the main thread before starting the background fetch.
        expire_seconds = self._age_filter()
        username = self.uname.GetValue()
        threading.Thread(
            target=self._fetch_and_show_counts,
            args=(expire_seconds, username),
            daemon=True,
        ).start()

    def _fetch_and_show_counts(self, expire_seconds, username):
        if not self._count_lock.acquire(blocking=False):
            return  # a count is already in progress; skip this one
        try:
            wx.CallAfter(self.sb.SetStatusText, "Getting submission/comment count ...")
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                f_comments = executor.submit(self._get_comment_total, expire_seconds, username)
                f_submissions = executor.submit(self._get_submission_total, expire_seconds, username)
                comments = f_comments.result()
                submissions = f_submissions.result()
            result = "Found {} submissions, {} comments".format(submissions, comments)
            wx.CallAfter(self.found.SetValue, result)
            wx.CallAfter(self.sb.SetStatusText, result)
        except Exception as exc:
            wx.CallAfter(self.sb.SetStatusText, "Error getting counts: {}".format(exc))
        finally:
            self._count_lock.release()

    def Login(self, e):
        self.sb.SetStatusText("Logging in...")
        clientid = os.environ.get("REDDIT_CLIENT_ID")
        clientsecret = os.environ.get("REDDIT_CLIENT_SECRET")
        if not clientid or not clientsecret:
            dlg = wx.MessageDialog(
                self,
                "Environment variables REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set.",
                "Login Error",
                wx.OK | wx.ICON_ERROR,
            )
            dlg.ShowModal()
            dlg.Destroy()
            self.sb.SetStatusText("Login failed.")
            return
        if not self.uname.GetValue().strip() or not self.pword.GetValue().strip():
            dlg = wx.MessageDialog(
                self,
                "Username and password are required.",
                "Login Error",
                wx.OK | wx.ICON_ERROR,
            )
            dlg.ShowModal()
            dlg.Destroy()
            self.sb.SetStatusText("Login failed.")
            return
        self.reddit = praw.Reddit(
            client_id=clientid,
            client_secret=clientsecret,
            user_agent=os.environ.get("REDDIT_USER_AGENT", "redditwipe"),
            username=self.uname.GetValue(),
            password=self.pword.GetValue(),
        )
        self.sb.SetStatusText("Logged in.")
        self.wipe_btn.Enable()
        self.UpdateCounts()


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
    "juliett",
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
    return " ".join(random.choices(phonetic, k=5))


def main():
    app = wx.App()
    frame = mainWindow(None, title="Reddit wipe utility")
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    main()
