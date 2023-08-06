# coding: utf-8
"""
This module defines the events signaled by abinit during the execution. It also
provides a parser to extract these events form the main output file and the log file.
"""
from __future__ import unicode_literals, division, print_function

import os.path
import collections
import yaml

from monty.fnmatch import WildCard
from monty.termcolor import colored
from pymatgen.core import Structure
from pymatgen.serializers.json_coders import PMGSONable, pmg_serialize
from .abiinspect import YamlTokenizer


__all__ = [
    "EventsParser",
]

def indent(lines, amount, ch=' '):
    """indent the lines in a string by padding each one with proper number of pad characters"""
    padding = amount * ch
    return padding + ('\n'+padding).join(lines.split('\n'))


def straceback():
    """Returns a string with the traceback."""
    import traceback
    return traceback.format_exc()


class AbinitEvent(yaml.YAMLObject): #, PMGSONable):
    """
    Example (YAML syntax)::

        Normal warning without any handler:

        --- !Warning
        message: | 
            This is a normal warning that won't 
            trigger any handler in the python code!
        src_file: routine_name
        src_line:  112
        ...

        Critical warning that will trigger some action in the python code.

        --- !ScfConvergeWarning
        message: |
            The human-readable message goes here!
        src_file: foo.F90
        src_line: 112
        tolname: tolwfr
        actual_tol: 1.0e-8
        required_tol: 1.0e-10
        nstep: 50
        ...

    The algorithm to extract the YAML sections is very simple.

    1) We use YamlTokenizer to extract the documents from the output file 
    2) If we have a tag that ends with "Warning", "Error", "Bug", "Comment
       we know we have encountered a new ABINIT event 
    3) We parse the document with yaml.load(doc.text) and we get the object

    Note that:
        # --- and ... become reserved words (whey they are placed at
          the begining of a line) since they are used to mark the beginning and 
          the end of YAML documents.

        # All the possible events should subclass `AbinitEvent` and define 
          the class attribute yaml_tag so that yaml.load will know how to 
          build the instance.
    """
    #color = None

    def __init__(self, message, src_file, src_line):
        """
        Basic constructor for :class:`AbinitEvent`.

        Args:
            message: String with human-readable message providing info on the event.
            src_file: String with the name of the Fortran file where the event is raised.
            src_line Integer giving the line number in src_file.
        """
        self.message = message
        self._src_file = src_file
        self._src_line = src_line

    @pmg_serialize
    def as_dict(self):
        return dict(message=self.message, src_file=self.src_file, src_line=self.src_line)

    @classmethod
    def from_dict(cls, d):
        d = d.copy()
        d.pop('@module', None)
        d.pop('@class', None)
        return cls(**d)

    @property
    def header(self):
        return "%s at %s:%s" % (self.name, self.src_file, self.src_line)

    def __str__(self):
        return "\n".join((self.header, self.message))

    @property
    def src_file(self):
        """String with the name of the Fortran file where the event is raised."""
        try:
            return self._src_file
        except AttributeError:
            return "Unknown"

    @property
    def src_line(self):
        """Integer giving the line number in src_file."""
        try:
            return self._src_line
        except AttributeError:
            return "Unknown"

    @property
    def name(self):
        """Name of the event (class name)"""
        return self.__class__.__name__

    @property
    def baseclass(self):
        """The baseclass of self."""
        for cls in _BASE_CLASSES:
            if isinstance(self, cls):
                return cls

        raise ValueError("Cannot determine the base class of %s" % self.__class__.__name__)

    def log_correction(self, task, message):
        """
        This method should be called once we have fixed the problem associated to this event.
        It adds a new entry in the correction history of the task.

        Args:
            message (str): Human-readable string with info on the action perfomed to solve the problem.
        """
        task._corrections.append(dict(
            event=self.as_dict(), 
            message=message,
        ))

    def correct(self, task):
        """
        This method is called when an error is detected in a :class:`Task` 
        It should perform any corrective measures relating to the detected error.
        The idea is similar to the one used in custodian but the handler receives 
        a :class:`Task` object so that we have access to its methods.

        Returns:
        (dict) JSON serializable dict that describes the errors and actions taken. E.g.
        {"errors": list_of_errors, "actions": list_of_actions_taken}.
        If this is an unfixable error, actions should be set to None.
        """
        return 0


class AbinitComment(AbinitEvent):
    """Base class for Comment events"""
    yaml_tag = '!COMMENT'
    color = "blue"


class AbinitError(AbinitEvent):
    """Base class for Error events"""
    yaml_tag = '!ERROR'
    color = "red"


class AbinitYamlError(AbinitError):
    """Raised if the YAML parser cannot parse the document and the doc tag is an Error."""


class AbinitBug(AbinitEvent):
    """Base class for Bug events"""
    yaml_tag = '!BUG'
    color = "red"


class AbinitWarning(AbinitEvent):
    """
    Base class for Warning events (the most important class).
    Developers should subclass this class to define the different exceptions
    raised by the code and the possible actions that can be performed.
    """
    yaml_tag = '!WARNING'
    color = None


class AbinitCriticalWarning(AbinitWarning):
    color = "red"


class AbinitYamlWarning(AbinitCriticalWarning):
    """
    Raised if the YAML parser cannot parse the document and the doc tas is a Warning.
    """

# Warnings that trigger restart.

class ScfConvergenceWarning(AbinitCriticalWarning):
    """Warning raised when the GS SCF cycle did not converge."""
    yaml_tag = '!ScfConvergenceWarning'


class NscfConvergenceWarning(AbinitCriticalWarning):
    """Warning raised when the GS NSCF cycle did not converge."""
    yaml_tag = '!NscfConvergenceWarning'


class RelaxConvergenceWarning(AbinitCriticalWarning):
    """Warning raised when the structural relaxation did not converge."""
    yaml_tag = '!RelaxConvergenceWarning'


# TODO: for the time being we don't discern between GS and PhononCalculations.
#class PhononConvergenceWarning(AbinitCriticalWarning):
#    """Warning raised when the phonon calculation did not converge."""
#    yaml_tag = u'!PhononConvergenceWarning'


class QPSConvergenceWarning(AbinitCriticalWarning):
    """Warning raised when the QPS iteration (GW) did not converge."""
    yaml_tag = '!QPSConvergenceWarning'


class HaydockConvergenceWarning(AbinitCriticalWarning):
    """Warning raised when the Haydock method (BSE) did not converge."""
    yaml_tag = '!HaydockConvergenceWarning'


# Error classes providing a correct method.

class DilatmxError(AbinitError):
    yaml_tag = '!DilatmxError'

    def correct(self, task):
        #Idea: decrease dilatxm and restart from the last structure.
        #We would like to end up with a structures optimized with dilatmx 1.01
        #that will be used for phonon calculations.

        # Read the last structure dumped by ABINIT before aborting.
        print("in dilatmx")
        filepath = task.outdir.has_abiext("DILATMX_STRUCT.nc")
        last_structure = Structure.from_file(filepath)

        task._change_structure(last_structure)
        #changes = task._modify_vars(dilatmx=1.05)
        task.history.append("Take last structure from DILATMX_STRUCT.nc, will try to restart")
        return 1


# Register the concrete base classes.
_BASE_CLASSES = [
    AbinitComment,
    AbinitError,
    AbinitBug,
    AbinitWarning,
]


class EventReport(collections.Iterable):
    """
    Iterable storing the events raised by an ABINIT calculation.

    Attributes::

        stat: information about a file as returned by os.stat
    """
    def __init__(self, filename, events=None):
        """
        List of ABINIT events.

        Args:
            filename: Name of the file
            events: List of Event objects
        """
        self.filename = os.path.abspath(filename)
        self.stat = os.stat(self.filename)

        self._events = []
        self._events_by_baseclass = collections.defaultdict(list)

        if events is not None:
            for ev in events:
                self.append(ev)

    def __len__(self):
        return len(self._events)

    def __iter__(self):
        return self._events.__iter__()

    def __str__(self):
        #has_colours = stream_has_colours(stream)
        has_colours = True

        lines = []
        app = lines.append

        app("Events for: %s" % self.filename)
        for i, event in enumerate(self):
            if has_colours:
                app("[%d] %s" % (i+1, colored(event.header, color=event.color)))
                app(indent(event.message, 4))
            else:
                app("[%d] %s" % (i+1, str(event)))

        app("num_errors: %s, num_warnings: %s, num_comments: %s, completed: %s" % (
            self.num_errors, self.num_warnings, self.num_comments, self.run_completed))

        return "\n".join(lines)

    def append(self, event):
        """Add an event to the list."""
        self._events.append(event)
        self._events_by_baseclass[event.baseclass].append(event)

    def set_run_completed(self, bool_value):
        """Set the value of _run_completed."""
        self._run_completed = bool_value

    @property
    def run_completed(self):
        """True if the calculation terminated."""
        try:
            return self._run_completed
        except AttributeError:
            return False

    @property
    def comments(self):
        """List of comments found."""
        return self.select(AbinitComment)

    @property
    def errors(self):
        """List of errors found."""
        return self.select(AbinitError)

    @property
    def bugs(self):
        """List of bugs found."""
        return self.select(AbinitBug)

    @property
    def warnings(self):
        """List of warnings found."""
        return self.select(AbinitWarning)

    @property
    def num_warnings(self):
        """Number of warnings reported."""
        return len(self.warnings)

    @property
    def num_errors(self):
        """Number of errors reported."""
        return len(self.errors)

    @property
    def num_comments(self):
        """Number of comments reported."""
        return len(self.comments)

    def select(self, base_class):
        """
        Return the list of events that inherits from class base_class

        Args:
            only_critical: if True, only critical events are returned.
        """
        return self._events_by_baseclass[base_class][:]

    def filter_types(self, event_types):
        events = []
        for ev in self:
            if type(ev) in event_types: events.append(ev)
        return self.__class__(filename=self.filename, events=events)


class EventsParserError(Exception):
    """Base class for the exceptions raised by :class:`EventsParser`."""


class EventsParser(object):
    """
    Parses the output or the log file produced by abinit and extract the list of events.
    """
    Error = EventsParserError

    # Internal flag used for debugging
    DEBUG_LEVEL = 0

    def parse(self, filename):
        """
        Parse the given file. Return :class:`EventReport`.
        """
        run_completed = False
        filename = os.path.abspath(filename)
        report = EventReport(filename)

        # TODO Use CamelCase for the Fortran messages.
        # Bug is still an error of class SoftwareError
        w = WildCard("*Error|*Warning|*Comment|*Bug|*ERROR|*WARNING|*COMMENT|*BUG")

        with YamlTokenizer(filename) as tokens:
            for doc in tokens:
                #print(80*"*")
                #print("doc.tag", doc.tag)
                #print("doc", doc)
                #print(80*"*")
                if w.match(doc.tag):
                    #print("got doc.tag", doc.tag,"--")
                    try:
                        event = yaml.load(doc.text)
                    except:
                        # Wrong YAML doc. Check tha doc tag and instantiate the proper event.
                        message = "Malformatted YAML document at line: %d\n" % doc.lineno
                        message += doc.text

                        # This call is very expensive when we have many exceptions due to malformatted YAML docs.
                        if self.DEBUG_LEVEL:
                            message += "Traceback:\n %s" % straceback()

                        if "error" in doc.tag.lower():
                            print("It seems an error", doc.tag)
                            event = AbinitYamlError(message=message, src_file=__file__, src_line=0)
                        else:
                            event = AbinitYamlWarning(message=message, src_file=__file__, src_line=0)

                    event.lineno = doc.lineno
                    report.append(event)

                # Check whether the calculation completed.
                if doc.tag == "!FinalSummary":
                    run_completed = True

        report.set_run_completed(run_completed)

        return report

    def report_exception(self, filename, exc):
        """
        This method is used when self.parser raises an Exception so that
        we can report a customized :class:`EventReport` object with info the exception.
        """
        return EventReport(filename, events=[AbinitError(str(exc))])
