class List:
    def __init__(self,name):
        self.posts = {}
        self.name=name
        self.lastMemberID=0
        self.members={}
        self.lastPostId=0

    def addMember(self,member):
        self.lastMemberID += 1
        self.members[self.lastMemberID] = member

    def deleteMember(self, memberID):
        del self.members[memberID]

    def getPosts(self):
        return sorted(self.posts.items())

    def getMembers(self):
        return sorted(self.members.items())