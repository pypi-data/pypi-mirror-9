"""
The role of a backend is to handle the communication with a backend tool that
will store the timesheets and provide projects and activities.
"""
from __future__ import unicode_literals

import six


class BaseBackend(object):
    """
    All Taxi backends should inherit from the :class:`BaseBackend` class.
    Backends are usually constructed from a URL in the form
    `<backend_name>://<username>:<password>@<hostname>:<port><path>?<options>`.
    The information you get in the :meth:`__init__` method will be already
    parsed so you don't need to do the parsing yourself. The ``options``
    parameter is a dictionary constructed from the backend URL querystring.
    """
    def __init__(self, username, password, hostname, port, path, options):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port
        self.path = path
        self.options = options

    def push_entry(self, date, entry):
        """
        Called when an entry should be pushed to the backend. `date` is a
        :func:`datetime.date` object. `entry` is a
        :class:`taxi.timesheet.entry.TimesheetEntry` object.

        If the push fails, this method should raise a :class:`PushEntryFailed`
        exception.
        """
        pass

    def get_projects(self):
        """
        Return a list of projects and activities. These will be then stored for
        further use. The list should contain :class:`taxi.projects.Project`
        objects.
        """
        return []

    def post_push_entries(self):
        """
        Called after the entries have been pushed. Useful if you need to do
        post-processing like closing connection, or sending entries buffered in
        :meth:`push_entry`.

        If an exception is raised in this method, the status of all the entries
        of the backend will be considered failed. You can also raise
        :class:`PushEntriesFailed` with a custom user message to mark their
        status as failed. If you want to mark individual entries as failed,
        raise :class:`PushEntriesFailed` with ``entries`` being a dictionary
        containing entries as keys, and error messages as values.
        """
        pass


class PushEntryFailed(Exception):
    """
    Exception indicating that an entry couldn't be pushed.
    """
    pass


@six.python_2_unicode_compatible
class PushEntriesFailed(Exception):
    """
    Exception indicating that a set of entries couldn't be pushed. Typically
    raised by :meth:`BaseBackend.post_push_entries`.

    If ``entries`` is set, it should be a dictionary mapping
    :class:`taxi.timesheet.entry.TimesheetEntry` with errors as strings.
    """

    def __init__(self, message=None, entries=None):
        self.entries = entries
        self.message = message

    def __str__(self):
        return self.message
