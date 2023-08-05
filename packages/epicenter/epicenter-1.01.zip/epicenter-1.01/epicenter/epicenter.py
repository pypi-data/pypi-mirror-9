"""Module for Persistence in the Python worker
"""
from copy import copy


class Epicenter(object):
    """
    Attributes
    ----------
    data : Dict
        The data that has been passed to record, and not taken for recording
        yet.
    event : Dict

    """

    data = {}
    event = {}
    event['subscribers'] = {}

    @staticmethod
    def subscribe(name, function):
        """Add an event to the subscribed members
        """
        if not callable(function):
            return

        if name not in Epicenter.event['subscribers']:
            Epicenter.event['subscribers'][name] = {}
        Epicenter.event['subscribers'][name] = function

    @staticmethod
    def publish(name, *args):
        """Run all subscribed functions of the given name
        """
        function = Epicenter.event['subscribers'].get(name, None)
        if function is not None:
            function(*args)

    @staticmethod
    def record(name, value):
        """Record a variable. The name must be given as a string. Calling
        this function should be of the form:

        Epicenter.record("my_variable", my_variable)

        Parameters
        ----------
        name : String
            The name of the variable to be saved
        value : Object
            The data saved in the variable.
        """
        Epicenter.data[name] = value

    @staticmethod
    def fetch_records():
        """Retrieve all the records currently tracked.
        """
        return Epicenter.data

    @staticmethod
    def take_records():
        """Retrieve all records currently tracked and reset the tracked
        records.
        """
        # copy.copy is necessary because otherwise tree is a reference to
        # data, and data.clear() empties out data, so then tree would be
        # empty! Choosing not to use deepcopy because of its pitfalls, but
        # hopefully that is not a problem.
        tree = copy(Epicenter.fetch_records())
        Epicenter.data.clear()
        return tree

    @staticmethod
    def _reset_epicenter():
        """Deletes all saved, untaken data and subscribed events.
        """
        Epicenter.data = {}
        Epicenter.event = {}
        Epicenter.event['subscribers'] = {}
