class Message:
    def __init__(self, sender, reciever, content, sent = None):
        self.sender = sender
        self.reciever = reciever
        self.content = content
        self.sent = sent
