class ListOfLists:
    def __init__(self,name):
        self.lists = {}
        self.lastListID = 0
        self.name=name

    def addList(self,list):
        self.lastListID += 1
        self.lists[self.lastListID] = list

    def deleteList(self, listID):
        del self.messages[message_id]

    def getList(self, listID):
        return self.messages[listID]

    def getLists(self):
        return sorted(self.lists.items())