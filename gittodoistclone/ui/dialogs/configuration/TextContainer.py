
from typing import Callable
from typing import Tuple

from wx import EVT_TEXT
from wx import ID_ANY

from wx import CommandEvent
from wx import StaticText
from wx import TextCtrl

from wx import NewIdRef as wxNewIdRef

from wx.lib.sized_controls import SizedPanel


class TextContainer(SizedPanel):
    """
    This container is generic
    """
    HORIZONTAL_GAP: int = 3

    def __init__(self, parent, labelText: str, valueChangedCallback: Callable, textControlSize: Tuple = (315, -1)):
        """

        Args:
            parent:     The parent window
            labelText:  How to label the text input
            valueChangedCallback:  The method to call when the value changes;  The method should expect the
            first parameter to be a string argument that is the new value
        """

        super().__init__(parent)

        self._textControlSize: Tuple = textControlSize
        self.SetSizerType('form')
        self._textId:  int = wxNewIdRef()

        self._callback: Callable = valueChangedCallback

        # noinspection PyUnusedLocal
        textLabel:   StaticText = StaticText(self, ID_ANY, labelText)
        textControl: TextCtrl   = TextCtrl(self, self._textId, "", size=self._textControlSize)
        # noinspection PyUnresolvedReferences
        textControl.SetSizerProps(expand=True, halign='right')

        self._textControl:  TextCtrl = textControl
        self._textValue:    str      = ''

        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True)
        parent.Bind(EVT_TEXT, self._onTextValueChanged, id=self._textId)

    def textControlEnabled(self, newValue: bool):
        self._textControl.Enable(newValue)

    def textValue(self, newValue: str):
        self._textValue = newValue
        self._textControl.SetValue(newValue)

    # Write only property   TODO fix mypy error
    textValue = property(None, textValue)   # type: ignore

    def _onTextValueChanged(self, event: CommandEvent):

        newValue: str = event.GetString()

        self._callback(newValue)
