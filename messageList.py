class MessageList:
    def __init__(self):
        self.messages = {}
        self.last_message_id = 0	

    def add_message(self, message):
        self.last_message_id += 1
        self.messages[self.last_message_id] = message

    def delete_message(self, message_id):
        del self.messages[message_id]

    def get_message(self, message_id):
        return self.messages[message_id]

    def get_messages(self):
        return sorted(self.messages.items())