
from abc import ABCMeta
from abc import abstractmethod

from wx.lib.sized_controls import SizedPanel

from pygitissue2todoist.general.Preferences import Preferences


class MyMetaConfigurationPanel(ABCMeta, type(SizedPanel)):        # type: ignore
    """
    I have know idea why this works:
    https://stackoverflow.com/questions/66591752/metaclass-conflict-when-trying-to-create-a-python-abstract-class-that-also-subcl
    """
    pass


class AbstractConfigurationPanel(SizedPanel, metaclass=MyMetaConfigurationPanel):
    """
    A generally abstract class to capture the behaviour of our configuration panels;  It
    is unclear to me whether the constructor here should call the abstract methods or
    have the subclass implementers do so;

    In the current case some amount of code is saved
    from duplication.

    If I went with the former case then subclass implementers would have to remember to call
    the methods, but would be saved from having to juggle when exactly to call this super
    constructor
    """
    def __init__(self, parent, *args, **kwargs):
        """
        This constructor creates an instance of the preferences class for use by
        the subclasses;

        Additionally, it immediately calls the methods necessary to populate the container
        with the implementation controls.
        """
        super().__init__(parent, *args, **kwargs)

        self._preferences: Preferences = Preferences()

        self._layoutContent()
        self._setControlValues()

    @abstractmethod
    def _layoutContent(self):
        """
        Abstract method
        Creates the panel's controls and stashes them as private instance variables
        """
        pass

    @abstractmethod
    def _setControlValues(self):
        """
        Set the default values on the controls.
        """
        pass
