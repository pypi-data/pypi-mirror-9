import copy
from query.selection import ScalarSelectable


class Rule(object):
    key = ScalarSelectable('rules', 'key')

    def __init__(self, name, alert_by=None, key=None, selection=None,
                 conditions=[], action=None):
        self.name = name
        self.alert_by = alert_by
        self.key = key
        self.selection = selection
        #make sure to avoid mutability of kwargs that default to list here
        self.conditions = copy.deepcopy(conditions)
        self.action = action


class Trigger(object):
    def __init__(self, trigger_type, args):
        self.trigger_type = trigger_type
        self.args = args


class Filter(object):
    def __init__(self, inclusion, filter_type, args):
        self.inclusion = inclusion
        self.filter_type = filter_type
        self.args = args


class Condition(object):
    def __init__(self, filters, trigger):
        self.filters = filters
        self.trigger = trigger


class Action(object):
    pass


class Webhook(Action):
    def __init__(self, url):
        self.url = url
