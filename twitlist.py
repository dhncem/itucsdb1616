class Twitlist:
    def __init__(self):
        self.twit = {}
        self.last_twit_id = 0

    def add_twit(self, twit):
        self.last_twit_id += 1
        self.twit[self.last_twit_id] = twit
        twit._id = self.last_twit_id

    def delete_twit(self, twit_id):
        del self.twit[twit_id]

    def get_twit(self, twit_id):
        return self.twit[twit_id]

    def get_twit(self):
        return self.twit