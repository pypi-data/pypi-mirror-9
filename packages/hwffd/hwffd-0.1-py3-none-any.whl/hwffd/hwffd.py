# -*- coding: utf-8 -*-

class TalkingEntity:
    """A talking entity. So cool."""

    def __init__(self, name='Anonymous'):
        self.name = name

    def talk(self, message):
        """Tell a message

        :param message: A string, the message to be told.
        """
        print(self.name + ': ' + message)

if __name__ == "__main__":
    francois = TalkingEntity('Francois Durand')
    francois.talk('Hello World!')