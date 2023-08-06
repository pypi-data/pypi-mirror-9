from .pypeg2 import *

#   SYMBOL DEFINITIONS: regex, Symbol, str, and Keyword
rgbRegex = re.compile('\(\d{1,3}\,\s*\d{1,3}\,\s*\d{1,3}\)')
intRegex = re.compile('\d+')
hexRegex = re.compile('\#[A-Fa-f0-9]{6}')
actionPrint = re.compile('"(.*?)"')
optionsRegex = re.compile('\"(.+?)\"|\w+')
textRegex = re.compile('[^"\n](.[^"]*)')
fileRegex = re.compile('.*\.\w+')
varnameRegex = re.compile('[a-z][A-Za-z\d\_]*')

class ColorKeywordValue(Keyword):
    grammar = Enum(K("red"),K("blue"),K("yellow"),K("orange"),K("green"),\
                    K("purple"),K("pink"),K("cyan"),K("magenta"),K("white"),K("black"))

class SizeGridValue(str):
    grammar = attr("columns", [intRegex, varnameRegex]), blank, attr("rows", [intRegex, varnameRegex])

class SizeKeywordValue(Keyword):
    grammar = Enum(K("small"), K("medium"),K("large"))

class PositionGridValue(str):
    grammar = attr("r", [intRegex, varnameRegex]), blank, attr("c", [intRegex, varnameRegex])

class PositionKeywordValue(Keyword):
    grammar = Enum(K("center"), K("top"), K("bottom"), K("left"), K("right"), K("topcenter"), K("bottomcenter"), K("topleft"), K("topright"), K("bottomleft"), K("bottomright"))

class HiddenKeywordValue(Keyword):
    grammar = Enum(K("true"), K("false"))

class QuotedText(str):
    grammar = "\"", textRegex, "\""

class SourceFileText(str):
    grammar = "\"", fileRegex, "\""

class Star(str):
    grammar = "*"

class BooleanValue(Keyword):
    grammar = Enum(K("true"), K("false"))

#Attributes to put in List
class ColorAttribute(List):
    grammar = 'color', blank, attr('value', [rgbRegex, hexRegex, ColorKeywordValue])

#TextColor
class TextColorAttribute:
    grammar = 'textColor', blank, attr('value', [rgbRegex, hexRegex, ColorKeywordValue])

class PositionAttribute(List):
    grammar = 'position', blank, attr('value', [PositionKeywordValue, PositionGridValue])

class TextAttribute(List):
    grammar = 'text', blank, [attr('value', QuotedText), attr('var', varnameRegex)]

class ActionAttribute(List):
    #grammar = 'action', blank, attr("value", word)
#    grammar = "action", blank, attr("value", word), optional(attr("text", actionPrint)), optional(attr("color", [rgbRegex, hexRegex, ColorKeywordValue])), optional(attr("size", [intRegex, SizeGridValue, SizeKeywordValue]))
    grammar = "action", blank, attr("funcname", word), optional(attr("arguments", some([QuotedText, varnameRegex, intRegex])))

class TitleAttribute(List):
    #grammar = 'title', blank, attr('value', QuotedText)
    #grammar = "title", blank, "\"", attr("value", textRegex), "\""
    grammar = 'title', blank, [attr('value', QuotedText), attr('var', varnameRegex)]


#Font
class FontAttribute:
    grammar = "font", blank, attr("value", [QuotedText, varnameRegex])


#   MENUITEM DOES THIS GO IN ATTRIBUTE CLASS????
class MenuItemTerminal(List):
    grammar = "\"", attr("text", word), "\"", ":", attr("action", word)



#Accept anything after options
class MenuItemOptionsAttribute(List):
    # grammar = 'menuoption', blank, attr('value', maybe_some([word, MenuItemTerminal]))
    grammar = 'menuoption', blank, attr('value', maybe_some(MenuItemTerminal))


#   IMAGE
class ImageSourceAttribute(List):
    grammar = 'source', blank, attr('value', SourceFileText)


#   CHECKBOXES and RADIOBUTTONS
class GroupOptionsAttribute(List):
    grammar = 'options', blank, attr('options', some(optional(Star), QuotedText))


#   FORMATTED TEXT
class FTFontAttribute:
    grammar = 'font', blank, attr('name', [QuotedText, varnameRegex])

class FTBoldAttribute:
    grammar = 'bold', blank, attr('value', BooleanValue)

class FTItalicAttribute:
    grammar = 'italic', blank, attr('value', BooleanValue)

class FTUnderlineAttribute:
    grammar = 'underline', blank, attr('value', BooleanValue)

class HiddenAttribute(List):
    grammar = 'hidden', blank, attr('value', HiddenKeywordValue)

class FTSizeAttribute:
    grammar = attr('value', [intRegex, varnameRegex])

class SizeAttribute(List):
#    grammar = 'size', blank, attr('value', [intRegex, SizeGridValue, SizeKeywordValue])
    grammar = 'size', blank, attr('value', [SizeGridValue, SizeKeywordValue, intRegex])


#Wrap as Attribute object and put into AttributeList
class Attribute:
    grammar = [attr('font', FTFontAttribute), attr('size', SizeAttribute), \
    attr('bold', FTBoldAttribute), attr('italic', FTItalicAttribute), \
    attr('underline', FTUnderlineAttribute), attr('options', GroupOptionsAttribute), \
    attr("color", ColorAttribute), attr("textColor", TextColorAttribute), \
    attr("position", PositionAttribute), attr("text", TextAttribute), \
    attr("action", ActionAttribute), attr("title", TitleAttribute), \
    attr("font", FontAttribute),  \
    attr("source", ImageSourceAttribute), attr("hidden", HiddenAttribute), attr("menuoption",MenuItemOptionsAttribute)]

class AttributeList(List):
     grammar = csl(Attribute)
