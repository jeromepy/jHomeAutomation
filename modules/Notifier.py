
"""
Notifier class
This modules should implement an observer pattern, so message can be distributed over different modules.
Classes can subscribe, unsubscribe and publish and receive message with the Notifier class
"""


class Notifier(object):

    def __init__(self):

        self.observers = []

    def subscribe(self, subscriber):
        """
        Method to subsribe for a class
        :param subscriber: (Class): contains object (PriorityQueue) recv_mess go get messages from the notifier
        :return: self -> so subscriber can store this link to get access to publish method
        """

        if subscriber in self.observers:
            return True

        self.observers.append(subscriber)
        #  print(f'Class {str(subscriber)} has been added to subscribers')
        return True

    def unsubscribe(self, subscriber):

        if subscriber in self.observers:
            self.observers.remove(subscriber)
            # print(f'Class {str(subscriber)} has been un-subscribed.')
            return True
        else:
            # print(f'Class {str(subscriber)} wanted to un-subscribe, but was not subscribed...')
            return False

    def publish(self, mess: dict, **kwargs):

        if "priority" in kwargs:
            prio = int(kwargs.get("priority"))
        else:
            prio = 1

        #  print(f'Starting to publish message: {str(mess)}')
        for subsc in self.observers:
            # print(f'[{subsc.__class__.__name__}] has been notified')
            subsc.recv_mess.push(mess, prio)
        return True
