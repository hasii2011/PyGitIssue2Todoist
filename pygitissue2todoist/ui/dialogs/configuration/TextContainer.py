
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
    This container is meant to be used whenever the UI needs a labelled input text;
    Conveniently created via a SizedPanel;
    """
    HORIZONTAL_GAP: int = 3

    def __init__(self, parent, labelText: str, valueChangedCallback: Callable, textControlSize: Tuple = (315, -1)):
        """

        Args:
            parent:     The parent window

            labelText:  How to label the text input

            valueChangedCallback:  The method to call when the value changes;  The method should expect the
            first parameter to be a string argument that is the new value

            textControlSize:  A tuple of (width, height) for the text input
        """

        super().__init__(parent)

        self._textControlSize: Tuple = textControlSize
        self.SetSizerType('form')
        self._textId:  int = wxNewIdRef()

        self._callback: Callable = valueChangedCallback

        # noinspection PyUnusedLocal
        textLabel:   StaticText = StaticText(self, ID_ANY, labelText)
        textControl: TextCtrl   = TextCtrl(self, self._textId, "", size=self._textControlSize)

        textControl.SetSizerProps(expand=True, halign='right')

        self._textControl:  TextCtrl = textControl
        self._valueOfText:    str      = ''

        # noinspection PyUnresolvedReferences
        self.SetSizerProps(expand=True)
        parent.Bind(EVT_TEXT, self._onTextValueChanged, id=self._textId)

    def textControlEnabled(self, newValue: bool):
        """
        Allows the developer to either enable or disable the text input control

        Args:
            newValue:  'True' means enable input;  'False' means disable input
        """
        self._textControl.Enable(newValue)

    def _textValue(self, newValue: str):
        """
        This is a write-only property for value of the contained text control;  Presumably, only the user can change the
        value by typing it in.  This invokes a callback to the constructed UI to update the value
        Args:
            newValue:  The value to set
        """
        self._valueOfText = newValue
        self._textControl.SetValue(newValue)

    textValue = property(None, _textValue)

    def _onTextValueChanged(self, event: CommandEvent):

        newValue: str = event.GetString()

        self._valueOfText = newValue
        self._callback(newValue)
