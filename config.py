import modules.Notifier as Notifier

global NOTIFIER


def init():
    global NOTIFIER
    NOTIFIER = Notifier.Notifier()