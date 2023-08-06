
from enum import Enum

# Takes string names or int indices of a type and an attribute.
# Returns None if that type does not have that attribute.
# Else returns the default value for that attribute.
def getDefault(typeName, attrName):
    # Determine index of type
    if type(typeName) == int:
        typeIndex = typeName
    elif type(typeName) == str:
        typeNameStr = 'TypeName.'+typeName
        typeIndex = eval(typeNameStr).value
    else:
        print("Oops, typeName arg is of the wrong type.")

    #Determine index of attribute
    if type(attrName) == int:
        attrIndex = attrName
    elif type(attrName) == str:
        attrNameStr = 'AttrName.'+attrName
        attrIndex = eval(attrNameStr).value
    else:
        print("Oops, attrName arg is of the wrong type.")

    #Retrieve and return default value for given type and attribute
    return matrix[attrIndex][typeIndex]


class TypeName(Enum):
    Window = 0
    Button = 1
    Checkboxes = 2
    RadioButtons = 3
    DropDown = 4
    Text = 5
    FormattedText = 6
    TextBox = 7
    Menu = 8
    MenuItem = 9
    Search = 10
    Image = 11


class AttrName(Enum):
    title = 0
    text = 1
    options = 2
    position = 3
    size = 4
    color = 5
    action = 6
    hidden = 7
    font = 8
    fontSize = 9
    textColor = 10
    source = 11

matrix = [["""Untitled Window""", """""", """Untitled Checkboxes""", """Untitled Radio Buttons""", """Untitled Drop Down""", None, None, """Untitled Text Box""", None, """Untitled Menu Item""", None, """"""],
[None, """Untitled Button""", None, None, None, """Text""", """Formatted Text""", """Type here""", None, None, """Search""", """Image Caption"""],
[None, None, "*""Option 1"" ""Option 2"" ""Option 3""", "*""Option 1"" ""Option 2"" ""Option 3""", "*""Option 1"" ""Option 2"" ""Option 3""", None, None, None, "menuItem1 menuItem2 menuItem3", """Option 1"" ""Option 2"" ""Option 3""", None, None],
[None, 'center', 'center', 'center', 'center', 'center', None, 'center', 'menuBar', None, 'center', 'center'],
['medium', 'medium', 'medium', 'medium', 'medium', 'medium', None, 'medium', None, None, 'medium', 'medium'],
['white', None, None, None, None, 'white', None, None, None, None, None, None],
["""""", """""", None, None, None, None, None, None, None, None, None, None],
[False, False, False, False, False, False, None, False, False, False, False, False],
["""Times New Roman""", None, None, None, None, None, """Times New Roman""", None, None, None, None, None],
[12, None, None, None, None, None, 12, None, None, None, None, None],
['black', None, None, None, None, None, 'black', None, None, None, None, None],
[None, None, None, None, None, None, None, None, None, None, None, 'defaultIcon']]

NUM_ATTRIBUTES = len(matrix)
NUM_TYPES = len(matrix[0])
