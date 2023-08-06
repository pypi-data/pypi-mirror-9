"""
Contains the Trigger classes (e.g., click, text writing) used by Eyes.
"""
from .errors import EyesError
from collections import OrderedDict


MOUSE_ACTION = {'click': 'Click', 'right_click': 'RightClick', 'double_click': 'DoubleClick',
                'move': 'Move', 'down': 'Down', 'up': 'Up'}

_TRIGGER_TYPE_FIELD_NAME = "triggerType"
_TRIGGER_TYPE = {'unknown': 'Unknown', 'mouse': 'Mouse', 'text': 'Text', 'keyboard': 'Keyboard'}


class MouseTrigger(object):
    """Encapsulates a mouse trigger."""

    def __init__(self, action, control, location):
        """
        Args:
            action (str, a key in (MOUSE_ACTION)): The mouse action represented by the trigger.
            control (Region): The region to which the text was entered.
            location (Point): The location which was clicked relative to the control.
        """
        self.action = action
        self.control = control
        self.location = location  # Point. Relative to the control's (left,top) corner.

    def __getstate__(self):
        return OrderedDict([(_TRIGGER_TYPE_FIELD_NAME, _TRIGGER_TYPE['mouse']),
                            ("mouseAction", MOUSE_ACTION[self.action]), ("control", self.control),
                            ("location", self.location)])

    # Required is required in order for jsonpickle to work on this object.
    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError('Cannot create MouseTrigger instance from dict!')

    def __str__(self):
        return "%s [%s] %s" % (self.action, self.control, self.location)


class TextTrigger(object):
    """Encapsulates a text input by the user."""

    def __init__(self, control, text):
        """
        Args:
            control (Region): The region to which the text was entered.
            text (str): The trigger's text.
        """
        self.control = control
        self.text = text

    def __getstate__(self):
        return OrderedDict([(_TRIGGER_TYPE_FIELD_NAME, _TRIGGER_TYPE['text']),
                            ("control", self.control), ("text", self.text)])

    # Required is required in order for jsonpickle to work on this object.
    # noinspection PyMethodMayBeStatic
    def __setstate__(self, state):
        raise EyesError('Cannot create MouseTrigger instance from dict!')

    def __str__(self):
        return "Text [%s] %s" % (self.control, self.text)