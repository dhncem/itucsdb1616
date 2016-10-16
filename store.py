class Store:
    def __init__(self):
        self.twits = {}
        self.last_twit_id = 0

    def add_twit(self, twit):
        self.last_twit_id += 1
        self.twits[self.last_twit_id] = twit
        twit._id = self.last_twit_id

    def delete_twit(self, twit_id):
        del self.twits[twit_id]

    def get_twit(self, twit_id):
        return self.twits[twit_id]

    def get_twit(self):
        return self.twits