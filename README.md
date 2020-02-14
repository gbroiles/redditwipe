# redditwipe
Python GUI to overwrite, then delete Reddit comments/submissions

Intended for Python 3. Developed (so far) on Windows, but should run with minimal or no changes on OS X and Linux (thanks, wxPython!)

Adapted from 

https://www.reddit.com/r/learnpython/comments/aoq9yj/reddit_script_to_delete_all_comments_and/

Also see:

https://github.com/j0be/PowerDeleteSuite

https://github.com/x89/Shreddit

And be aware of:

https://www.reddit.com/r/PushShift

## Usage

This is intended to be used as a "script", in Reddit API parlance. This means that you must tell Reddit that you are a developer, by going (when logged into Reddit) to Preferences, then Apps, the under "create application", tell it your application is named "redditwipe", choose "script" (instead of "web app" or "installed app"), for description put something like "deletes old comments/submssions", leave about URL blank, for redirect URI put http://localhost:8080. Press "Create App" button. The screen will refresh. You will see a box titled Redditwipe, followed by "personal use script", followed by 14 characters. Those 14 characters are your Reddit Client ID. Below that, you will see a field labeled "secret", followed by 25 characters. Those 25 characters are your Reddit Client Secret. Save the Client ID and the Secret. Ideally, save them as environment variables named REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET. In Bash, this means putting

    export REDDIT_CLIENT_ID='12345678901234'
    export REDDIT_CLIENT_SECRET='1234567890123456789012345'

in your .bashrc folder in your home directory. Or, add them as system environment variables in Windows.

If you're only going to use one username/password set, you can also set two more environment variables:

    export REDDIT_USER='username'
    export REDDIT_PASSWORD='password'

and they'll be available to the program. If you want to use the program with several usernames (** they must all be added as developers in the App section on Reddit **) you can leave those variables blank and enter the username/pw pairs when you run the program. 

to run the program, type

    python redditwipe.py
    
or

    python3 redditwipe.py
    
or on Windows, name the file "redditwipe.pyw" and it will launch as a GUI and you don't need to run the Python interpreter separately. 
