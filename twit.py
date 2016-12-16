class Twit:
    def __init__(self, title, context, twitid, userhandle, numberoflikes, numberofrts):
        self.title = title
        self.context = context
        self.twitid = twitid
        self.userhandle = userhandle
        self.numberoflikes = numberoflikes
        self.numberofrts = numberofrts

class Link:
        def __init__(self, tweetlid, contextl, twitid):
            self.tweetlid = tweetlid
            self.contextl = contextl
            self.twitid = twitid