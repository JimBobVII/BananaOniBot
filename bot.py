#This is the source code for BananaOniBot, a reddit bot designed to post banana
#facts to comments mentioning bananas in specific communities.
#This code is moderately commented in the hopes that it can serve as a tutorial
#on how to (or how *not* to) build a basic reply-bot.

#A basic understanding of Python and PRAW is recommended, but not imperative.
import praw
import pdb
import re
import os
import random
import time
import sys
from praw.models import Message
from praw.models import Comment
from prawcore import PrawcoreException
from prawcore.exceptions import ResponseException

banana_facts = []
#If the bot can't find a file to read its responses from, quit immediately.
#Alternatively, desired comments can be directly inserted into the above array,
#and the code for opening the facts file can be removed. Messy, unrecommended.
if not os.path.isfile("facts.txt"):
	sys.exit()
else: 
	with open("facts.txt", "r") as f:
		#open the facts file for reading, and populate the fact array
		#Facts are separated and split by line breaks - do not use empty lines as separators.
		banana_facts = f.read()
		banana_facts = banana_facts.split("\n")
		banana_facts = list(filter(None, banana_facts))

ignored = []
if not os.path.isfile("ignore.txt"):
	#A file with ignored users is optional,
	#but without one the !ignore function resets its ignored list every time the bot restarts.
	#To prevent this, the bot willl attempt to create a saved ignore list when an ignore command is sent.
	#Without good reason otherwise, the bot should always ignore its own comments,
	#so that it doesn't get stuck in a loop of replying to itself
	ignored = ["BananaOniBot"]
else: 
	with open("ignore.txt", "r") as f:
		ignored = f.read()
		ignored = ignored.split("\n")
		ignored = list(filter(None, ignored))

if not os.path.isfile("replies.txt"):
	#this keeps track of which comments have been seen and acted upon
	#like ignore, this is technically optional but recommended.
	#again, the bot will attempt to create the file later if it doesn't exist
	replied = []
else: 
	with open("replies.txt", "r") as f:
		replied = f.read()
		replied = replied.split("\n")
		replied = list(filter(None, replied))

if not os.path.isfile("message_replies.txt"):
	#the bot has a separate list for handling private messages as well.
	message_replied = []
else: 
	with open("message_replies.txt", "r") as f:
		message_replied = f.read()
		message_replied = message_replied.split("\n")
		message_replied = list(filter(None, message_replied))

def get_fact(): #this simple function chooses a fact at random from the fact array
	return random.choice(banana_facts)

#start the bot labeled [bob] in praw.ini
#note that you will need to fill in this section with your own bot account's information, including username, password, and client secret. DO NOT share that info with others.
reddit = praw.Reddit('bob')
#BananaOniBot was designed to run on specifc subreddits rather than sitewide (unless directly invoked).
#To run on multiple subreddits, the below command needs a single string with all the necessary subreddit names,
#combined with a '+'. As you can see below, this means BananaOniBot only runs on r/grandorder and r/FGOmemes
subreddit = reddit.subreddit("grandorder+FGOmemes")
#bot_footer is a string that the bot deliberately appends as a signature, in this case giving contact information and commands in case someone unwittingly invokes it.
#The line breaks (\n) and --- create a divider line separating the message and footer, while the carets (^) create a smaller superscript-like text
bot_footer="\n\n---\n\n^I'm ^a ^bot ^\(RIP) ^| ^!ignore ^to ^ignore ^you, ^!delete ^to ^ignore, ^clear ^replies ^| [^View ^my ^source](https://github.com/jimbobvii/bananaonibot) ^| ^Thanks: ^Synapsensalat, ^BananaFactBoi"
#phone_home is part of a script that messages the bot's owner when certain events happen
#The message id should be that of a message *from* the owner's account *to* the bot's account, for proper notification
#For example, if the owner sends the bot a message, and the permalink for that message is something like https://reddit.com/message/messages/xyz123,
#the proper line would be "phone_home = reddit.inbox.message('xyz123')"
#this message id must be a valid message to which the bot hass access, or else the bot will crash shortly after starting.
phone_home = reddit.inbox.message('xyz123')

#And now we get to the meat of the bot: A giant, ugly loop that basically just scans for new comments or messages.
#This is wildly inefficient and far from the best setup, but in some ways inefficiency was part of the original goal:
#I was worried that if the bot went through its process to quickly, it might scan for comments too often and get rate-limited
while True:
		try:
			for comment in subreddit.stream.comments(skip_existing=True): #scan subs for new comments since boot or last scan
				if re.search("banana", comment.body, re.IGNORECASE): #check if the comment mentions bananas
					#if it does, make sure it didn't come from this bot or an ignored user, and that it wasn't already handled somewhere else in the loop
					if comment.id not in replied and comment.author.name not in ignored and comment.author != reddit.user.me():
						print(comment)
						if random.random() < 0.75 or re.search("u/bananaonibot", comment.body, re.IGNORECASE): #only reply ~75% of the time or when directly mentioned
							comment.reply(get_fact()+bot_footer) #the response is a random fact plus the footer/signature
						replied.append(comment.id)
						with open ("replies.txt", "a") as f: #mark the comment as seen (even if not replied to) so we know to ignore it in the future
							f.write(comment.id+"\n")
							f.close()
				for reply in reddit.inbox.unread(): #Now we look at our inbox
					if re.search("!ignore", reply.body, re.IGNORECASE): #and see if someone wants to be added to the ignore list
						if reply.id not in replied and reply.id not in message_replied and reply.author.name not in ignored: #check if we already need to ignore this
							ignored.append(reply.author.name) #if not, add to ignore list
							print(reply)
							reply.reply("I'll ignore your comments and messages ;_; (this may take some time to update)"+bot_footer) #write up a response
							if isinstance(reply, Comment): #and send it as a comment
								replied.append(reply.id)
								with open ("replies.txt", "a") as f:
									f.write(reply.id+"\n")
									f.close()
							elif isinstance(reply, Message): #or a dm, depending on how the ignore command was sent
								message_replied.append(reply.id)
								with open ("message_replies.txt", "a") as f:
									f.write(reply.id+"\n")
							with open ("ignore.txt", "a") as f:
								f.write(reply.author.name+"\n")
								f.close()
							reply.mark_read()
					elif re.search("!delete", reply.body, re.IGNORECASE): #check if someone wants to delete the bot's responses to them
						if reply.id not in replied and reply.id not in message_replied:
							ignored.append(reply.author.name) #add them to the ignore list, if necessary
							if isinstance(reply, Comment):
								replied.append(reply.id)
								with open ("replies.txt", "a") as f:
									f.write(reply.id+"\n")
									f.close()
							elif isinstance(reply, Message):
								message_replied.append(reply.id)
								with open ("message_replies.txt", "a") as f:
									f.write(reply.id+"\n")
							ignored.append(reply.author.name)
							with open ("ignore.txt", "a") as f:
									f.write(reply.author.name+"\n")
									f.close()
							#The delete part is horribly inefficient and, in fact, completely broken
							#It was added as an afterthought, and doesn't really work because I never thought to mark each viewed comment's author.
							#Instead the bot looks through every comment ID it has stored, tries to load the comment the ID belongs to, check its author,
							#and if the author matches, look at each *response* to that comment, and delete any response that the bot made.
							#I don't think this actually works at all as written - if it does, it's transparent as designed *when* it does,
							#but I've had to manually go through and delete some stuff after the bot errored out trying.
							#This is a clear example of "don't follow my example" - just scrap this entirely.
							for id in replied:
								old_comment = reddit.comment(id)
								old_comment.refresh()
								old_comment.refresh()
								if reply.author.name == old_comment.author.name:
									for response in old_comment.replies:
										if response.author == reddit.user.me():
											response.delete()
							reply.mark_read()
					#Down here, the bot sends notice back to its owner whenever it gets mentioned or receives a DM.
					#This isn't strictly necessary, but it helps monitor things outside of the bot's scope.
					elif isinstance(reply, Comment) and re.search("u/BananaOniBot", reply.body, re.IGNORECASE):
						phone_home.reply(reply.author.name+" mentioned me at "+ reply.subreddit.name +": " +reply.context)
						reply.mark_read()
					elif isinstance(reply, Message):
						phone_home.reply(reply.author.name+" sent me a message titled "+reply.subject+".\n\n\""+reply.body+"\"")
						reply.mark_read()
			#If we've made it to the end of the loop without any exceptions, we can reset the error counter.
			#The error counter is really only designed to kill the bot if it's malfunctioning nonstop
			errors = 0
		#Exception handling is broken into three parts: Prawcore exceptions, response exceptions, or literally anything else going wrong.
		except PrawcoreException as e:
			#Prawcore exceptions are usually benign and don't need serious handling, but that could just be my own experience.
			#Log the error, timeout the bot for 15 seconds and try again
			print("Prawcore Exception occurred. Check error log. Continuing...")
			with open ("errors.txt", "a") as f:
				f.write("\n"+str(e)+"\n")
				f.close()
			time.sleep(15)
			continue
		except ResponseException as e:
			#*usually* response exceptions stem from reddit being down or API/credential issues.
			#In this case, we wait a full minute before trying again.
			#If we get this exception 60 times in a row, that means it's been at least an hour since the bot has worked properly,
			#and something might actually be wrong; bot terminates. No point in messaging owner first since, by all indications,
			#the bot can't communicate through reddit right now anyways.
			#Changing/eliminating the terminate time might be useful for a bot that you want to keep entirely hands-off, or you could set up a service to restart
			#it at certain intervals.
			errors = errors +1
			if errors > 60: sys.exit()
			print("ResponseException occurred. Check error log. Continuing in 60...")
			with open ("errors.txt", "a") as f:
				f.write("\n"+str(e)+"\n")
				f.close()
			time.sleep(60)
			continue
		except Exception as e:
			#if other exceptions occurred, it's probably something wrong with the code rather than an API or server issue.
			#In this case, we message the owner with the exact error so that they know something's wrong, and then terminate,
			#to avoid making things worse or spamming the owner's inbox if the same error happens repeatedly.
			print("Non-praw exception occurred, messaging owner and exiting\n")
			phone_home.reply("New exception occurred. Code check and reboot required: \n\n"+str(e))
			print(e)
			sys.exit()
