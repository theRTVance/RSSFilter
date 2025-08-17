This is a python script to remove content from RSS Feeds allowing you to filter out episodes that you don't want<br>
or<Br>
If you have one of those podcast feeds that they think they are doing you a favor by having multiple podcasts in the same... they aren't!! and I think poorly of their IT people.

The reason for the choice of license is that I am learning and want to know IF there are better ways. 

This was the first project I 'vibe' coded. Blah Blah, **Dyslexic**. Blah Blah can read, edit, and usually debug code... can not start from zero. 


### How I use it:
My home server runs the script nightly. I have a cronjob set up to run a script that runs all the filtering scripts. <br>
Syncthing syncs those eddited RSS files to my phone. <br>
I use Tasker to Launch a Server app (SHTTPS) and press the button to start the server. <br>
My Podcast App is then set to 127.0.0.1/rssFeed.name <br>
It grabs the RSS Feed like normal.<br>
SHTTPS automatically turns off after 15 minutes <br>

Alternatively I have tried TailScale. <br>
I don't recall why I didn't use that method. Probably because I like using duckduckgos app tracking blocker.

### Known Issues:
It doesn't bring in Artwork.<br>
It doesn't grab the chapter tags and of course artwork

I will get back to this at some point to fix these errors. 

RV
