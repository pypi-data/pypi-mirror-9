# coding: utf-8
from collections import Iterable as IterableType


__author__ = "Dmitry Veselov"
__version__ = "0.1.1"


class Element(object):

    template = "<{name}{attributes}>{content}</{name}>"

    def __init__(self):
        self.attributes = None
        self.content = None

    def __lshift__(self, attributes):
        """
        Used for setting element attributes, like #id or .class.
        """
        if not isinstance(attributes, dict):
            message = "Element attributes must be a dictionary: '{0}'"
            raise ValueError(message.format(attributes))
        else:
            self.attributes = attributes
        return self # allows to chain our magic calls

    def __rshift__(self, content):
        """
        Used for filling content of element, e.g. add <li> tags into <ul>.
        """
        if isinstance(content, str): # plain text (html?) content
            self.content = content
        elif isinstance(content, (Element, ElementProxy)):
            self.content = str(content)
        else:
            if content:
                if isinstance(content, IterableType):
                    self.content = "".join(map(str, content)) # render each element in @content iterable
                else:
                    self.content = str(content)
            else:
                self.content = ""
        return self

    def __str__(self):
        if self.attributes:
            attributes = " ".join(self.rendered_attributes)
            if attributes:
                attributes = " " + attributes
        else:
            attributes = ""
        content = self.content or ""
        return self.template.format(name=self.element_name,
                                    attributes=attributes,
                                    content=content)

    def __repr__(self):
        return str(self)

    # rendering helpers

    @property
    def rendered_attributes(self):
        for name, value in self.attributes.items():
            if isinstance(value, bool):
                if value:
                    template = "{name}"
                else:
                    continue
            else:
                template = "{name}=\"{value}\""
            yield template.format(name=name, value=value)

    @property
    def element_name(self):
        return self.__class__.__name__.lower()

# HTML elements, from https://developer.mozilla.org/en/docs/Web/HTML/Element

class HTML(Element):
    pass

class HTML5(Element):
    # same as HTML element, but with doctype declaration
    template = "<!DOCTYPE html5><html{attributes}>{content}</html>"


class Comment(Element):
    template = "<!-- {content} -->"


class Base(Element):
    template =  "<{name}{attributes}>"


class Head(Element):
    pass


class Link(Element):
    template = "<{name}{attributes}>"


class Meta(Element):
    template = "<{name}{attributes}>"


class Style(Element):
    pass


class Title(Element):
    pass


class Address(Element):
    pass


class Article(Element):
    pass


class Body(Element):
    pass


class Footer(Element):
    pass


class Header(Element):
    pass


class H1(Element):
    pass


class H2(Element):
    pass


class H3(Element):
    pass


class H4(Element):
    pass


class H5(Element):
    pass


class H6(Element):
    pass


class HGroup(Element):
    pass


class Nav(Element):
    pass

class Section(Element):
    pass


class Blockquote(Element):
    pass


class DD(Element):
    pass


class Div(Element):
    pass


class DL(Element):
    pass


class DT(Element):
    pass


class Figcaption(Element):
    pass


class Figure(Element):
    pass


class HR(Element):
    template = "<{name}{attributes}>"


class Li(Element):
    pass


class Main(Element):
    pass


class OL(Element):
    pass


class P(Element):
    pass


class Pre(Element):
    pass


class UL(Element):
    pass


class A(Element):
    pass


class Abbr(Element):
    pass


class B(Element):
    pass


class Bdi(Element):
    pass


class Bdo(Element):
    pass


class Br(Element):
    template = "<{name}>"


class Cite(Element):
    pass


class Code(Element):
    pass


class Data(Element):
    pass


class Dfn(Element):
    pass


class Em(Element):
    pass


class I(Element):
    pass


class Kbd(Element):
    pass


class Mark(Element):
    pass


class Q(Element):
    pass


class Rp(Element):
    pass


class Rt(Element):
    pass


class Ruby(Element):
    pass


class S(Element):
    pass


class Samp(Element):
    pass


class Small(Element):
    pass


class Span(Element):
    pass


class Strong(Element):
    pass


class Sub(Element):
    pass


class Sup(Element):
    pass


class Time(Element):
    pass


class U(Element):
    pass


class Var(Element):
    pass


class Wbr(Element):
    template = "<{name}>"


class Area(Element):
    template = "<{name}{attributes}/>"


class Audio(Element):
    pass


class Img(Element):
    template = "<{name}{attributes}/>"


class Map(Element):
    pass


class Track(Element):
    template = "<{name}{attributes}>"


class Video(Element):
    pass


class Embed(Element):
    template = "<{name}{attributes}>"


class Iframe(Element):
    pass


class Object_(Element):
    template = "<object{attributes}>{content}</object>"


class Param(Element):
    template = "<{name}{attributes}>"


class Source(Element):
    template = "<{name}{attributes}>"


class Canvas(Element):
    pass


class Noscript(Element):
    pass


class Script(Element):
    pass


class Del(Element):
    pass


class Ins(Element):
    pass


class Caption(Element):
    pass


class Col(Element):
    template = "<{name}{attributes}>"


class Colgroup(Element):
    pass


class Table(Element):
    pass


class Tbody(Element):
    pass


class Td(Element):
    pass


class Tfoot(Element):
    pass


class Th(Element):
    pass


class Thead(Element):
    pass


class Tr(Element):
    pass


class Button(Element):
    pass


class Datalist(Element):
    pass


class Fieldset(Element):
    pass


class Form(Element):
    pass


class Input(Element):
    template = "<{name}{attributes}>"


class Keygen(Element):
    template = "<{name}{attributes}>"


class Label(Element):
    pass


class Legend(Element):
    pass


class Meter(Element):
    pass


class Optgroup(Element):
    pass


class Option(Element):
    pass


class Output(Element):
    pass


class Progress(Element):
    pass


class Select(Element):
    pass


class Textarea(Element):
    pass


class ElementProxy(object):

    def __init__(self, cls):
        self.cls = cls

    def __lshift__(self, attributes):
        element = self.cls()
        element << attributes
        return element

    def __rshift__(self, content):
        element = self.cls()
        element >> content
        return element

    def __str__(self):
        return str(self.cls())

    def __repr__(self):
        return repr(self.cls())


html = ElementProxy(HTML)
html5 = ElementProxy(HTML5)

base = ElementProxy(Base)
head = ElementProxy(Head)
link = ElementProxy(Link)
meta = ElementProxy(Meta)
style = ElementProxy(Style)
title = ElementProxy(Title)

address = ElementProxy(Address)
article = ElementProxy(Article)
body = ElementProxy(Body)
footer = ElementProxy(Footer)
header = ElementProxy(Header)
nav = ElementProxy(Nav)
section = ElementProxy(Section)

blockquote = ElementProxy(Blockquote)
dd = ElementProxy(DD)
div = ElementProxy(Div)
dl = ElementProxy(DL)
dt = ElementProxy(DT)
figcaption = ElementProxy(Figcaption)
figure = ElementProxy(Figure)
hr = ElementProxy(HR)
li = ElementProxy(Li)
main = ElementProxy(Main)
ol = ElementProxy(OL)
p = ElementProxy(P)
pre = ElementProxy(Pre)
ul = ElementProxy(UL)

a = ElementProxy(A)
abbr = ElementProxy(Abbr)
b = ElementProxy(B)
bdi = ElementProxy(Bdi)
bdi = ElementProxy(Bdi)
br = ElementProxy(Br)
cite = ElementProxy(Cite)
code = ElementProxy(Code)
data = ElementProxy(Data)
dfn = ElementProxy(Dfn)
em = ElementProxy(Em)
i = ElementProxy(I)
kbd = ElementProxy(Kbd)
mark = ElementProxy(Mark)
q = ElementProxy(Q)
rp = ElementProxy(Rp)
rt = ElementProxy(Rt)
ruby = ElementProxy(Ruby)
s = ElementProxy(S)
samp = ElementProxy(Samp)
small = ElementProxy(Small)
span = ElementProxy(Span)
strong = ElementProxy(Data)
sub = ElementProxy(Sub)
sup = ElementProxy(Sup)
time = ElementProxy(Time)
u = ElementProxy(U)
var = ElementProxy(Var)
wbr = ElementProxy(Wbr)

area = ElementProxy(Area)
audio = ElementProxy(Audio)
img = ElementProxy(Img)
map_ = ElementProxy(Map)
track = ElementProxy(Track)
video = ElementProxy(Video)

embed = ElementProxy(Embed)
iframe = ElementProxy(Iframe)
object_ = ElementProxy(Object_)
param = ElementProxy(Param)
source = ElementProxy(Param)

canvas = ElementProxy(Canvas)
noscript = ElementProxy(Noscript)
script = ElementProxy(Script)

del_ = ElementProxy(Del)
ins = ElementProxy(Ins)

caption = ElementProxy(Caption)
col = ElementProxy(Col)
colgroup = ElementProxy(Colgroup)
table = ElementProxy(Table)
tbody = ElementProxy(Tbody)
td = ElementProxy(Td)
tfoot = ElementProxy(Tfoot)
th = ElementProxy(Th)
thead = ElementProxy(Thead)
tr = ElementProxy(Tr)

button = ElementProxy(Button)
datalist = ElementProxy(Datalist)
fieldset = ElementProxy(Fieldset)
form = ElementProxy(Form)
input = ElementProxy(Input)
keygen = ElementProxy(Keygen)
label = ElementProxy(Label)
legend = ElementProxy(Legend)
meter = ElementProxy(Meter)
optgroup = ElementProxy(Optgroup)
option = ElementProxy(Option)
output = ElementProxy(Output)
progress = ElementProxy(Progress)
select = ElementProxy(Select)
textarea = ElementProxy(Textarea)

h1 = ElementProxy(H1)
h2 = ElementProxy(H2)
h3 = ElementProxy(H3)
h4 = ElementProxy(H4)
h5 = ElementProxy(H5)
h6 = ElementProxy(H6)
hgroup = ElementProxy(HGroup)
