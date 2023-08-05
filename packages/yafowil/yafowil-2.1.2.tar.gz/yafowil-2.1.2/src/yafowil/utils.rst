Test entry_point support tools
------------------------------

::
    >>> import yafowil.loader
    >>> from yafowil.utils import get_entry_points
    >>> get_entry_points()
    [...EntryPoint.parse('register = yafowil.loader:register')...]

    >>> get_entry_points('nonexisting')
    []

    >>> from yafowil.utils import get_plugin_names
    >>> get_plugin_names()
    [...'yafowil'...]

    >>> get_plugin_names('nonexisting')
    []


Test examples lookup
--------------------

::
    >>> from yafowil.utils import get_example_names
    >>> sorted(get_example_names())
    ['yafowil'...]

    >>> from yafowil.base import factory
    >>> factory.register_macro('field', 'field:label:error', {})

    >>> from yafowil.utils import get_example
    >>> get_example('inexistent')

    >>> examples = get_example('yafowil')
    >>> examples[0]['doc']
    "Plain Text\n----------..."

    >>> examples[0]['title']
    'Plain Text'

    >>> examples[0]['widget']
    <Widget object 'yafowil-plaintext' at ...>


Test the Vocabulary
-------------------

::
    >>> from yafowil.utils import vocabulary
    >>> vocabulary('foo')
    [('foo', 'foo')]

    >>> vocabulary({'key': 'value'})
    [('key', 'value')]

    >>> vocabulary(['value', 'value2'])
    [('value', 'value'), ('value2', 'value2')]

    >>> vocabulary([('key', 'value'), ('key2', 'value2', 'v2.3'), ('key3',)])
    [('key', 'value'), ('key2', 'value2'), ('key3', 'key3')]

    >>> def callme():
    ...     return 'bar'

    >>> vocabulary(callme)
    [('bar', 'bar')]

    >>> vocabulary(None) is None
    True


Test Tag renderer
-----------------

::
    >>> from node.utils import UNSET
    >>> from yafowil.utils import Tag
    >>> tag = Tag(lambda msg: msg)
    >>> a = {'class': u'fancy', 'id': '2f5b8a234ff'}
    >>> tag('p', 'Lorem Ipsum. ', u'Hello World!',
    ...     class_='fancy', id='2f5b8a234ff')
    u'<p class="fancy" id="2f5b8a234ff">Lorem Ipsum. Hello World!</p>'

    >>> tag('dummy', name='foo', **{'data-foo': 'bar'})
     u'<dummy data-foo=\'bar\' name="foo" />'

    >>> tag('dummy', name=None)
    u'<dummy />'

    >>> tag('dummy', name=UNSET)
    u'<dummy />'

deprecated test::

    >>> from yafowil.utils import tag as deprecated_tag
    >>> deprecated_tag('div', 'foo')
    u'<div>foo</div>'


Test CSS Classes
----------------

::
    >>> from plumber import plumbing
    >>> from node.base import OrderedNode
    >>> from node.behaviors import Nodespaces
    >>> from node.behaviors import Attributes
    >>> @plumbing(Nodespaces, Attributes)
    ... class CSSTestNode(OrderedNode):
    ...     pass
    >>> widget = CSSTestNode()
    >>> widget.attrs['required'] = False
    >>> widget.attrs['required_class'] = None
    >>> widget.attrs['required_class_default'] = 'required'
    >>> widget.attrs['error_class'] = None
    >>> widget.attrs['error_class_default'] = 'error'
    >>> widget.attrs['class'] = None
    >>> widget.attrs['class_add'] = None

    >>> class DummyData(object):
    ...     def __init__(self):
    ...         self.errors = []
    >>> data = DummyData()

    >>> from yafowil.utils import cssclasses
    >>> print cssclasses(widget, data)
    None

    >>> widget.attrs['class'] = 'foo bar'
    >>> print cssclasses(widget, data)
    bar foo

    >>> widget.attrs['class'] = None
    >>> widget.attrs['required'] = True
    >>> print cssclasses(widget, data)
    None

    >>> widget.required = False
    >>> data.errors = True
    >>> print cssclasses(widget, data)
    None

    >>> widget.attrs['error_class'] = True
    >>> print cssclasses(widget, data)
    error

    >>> widget.attrs['class'] = 'foo bar'
    >>> print cssclasses(widget, data)
    bar error foo

    >>> widget.attrs['class'] = lambda w, d: 'baz'
    >>> print cssclasses(widget, data)
    baz error

    >>> widget.attrs['class_add'] = lambda w, d: 'addclass_from_callable'
    >>> print cssclasses(widget, data)
    addclass_from_callable baz error

    >>> widget.attrs['class_add'] = 'addclass'
    >>> print cssclasses(widget, data)
    addclass baz error

    >>> widget.attrs['class'] = None
    >>> widget.attrs['class_add'] = None
    >>> widget.attrs['error_class'] = 'othererror'
    >>> print cssclasses(widget, data)
    othererror

    >>> data.errors = False
    >>> print cssclasses(widget, data)
    None

    >>> widget.attrs['required'] = True
    >>> print cssclasses(widget, data)
    None

    >>> widget.attrs['required_class'] = True
    >>> print cssclasses(widget, data)
    required

    >>> widget.attrs['required_class'] = 'otherrequired'
    >>> print cssclasses(widget, data)
    otherrequired

    >>> widget.attrs['error_class'] = True
    >>> data.errors = True
    >>> widget.attrs['required_class'] = 'required'
    >>> print cssclasses(widget, data)
    error required

    >>> widget.attrs['class'] = 'foo bar'
    >>> print cssclasses(widget, data)
    bar error foo required

    >>> print cssclasses(widget, data, additional=['zika', 'akiz'])
    akiz bar error foo required zika


Test managedprops annotation
----------------------------

::
    >>> from yafowil.utils import managedprops
    >>> @managedprops('foo', 'bar')
    ... def somefunc(a, b, c):
    ...     return a, b, c
    >>> somefunc(1, 2, 3)
    (1, 2, 3)
    >>> somefunc.__yafowil_managed_props__
    ('foo', 'bar')


Test attr_value
---------------

::
    >>> from node.base import AttributedNode
    >>> from yafowil.utils import attr_value

    >>> widget = AttributedNode()
    >>> data = AttributedNode()

    >>> widget.attrs['attr'] = 'value'
    >>> attr_value('attr', widget, data)
    'value'

    >>> def func_callback(widget, data):
    ...     return 'func_callback value'
    >>> widget.attrs['attr'] = func_callback
    >>> attr_value('attr', widget, data)
    'func_callback value'

    >>> def failing_func_callback(widget, data):
    ...     raise Exception('failing_func_callback')
    >>> widget.attrs['attr'] = failing_func_callback
    >>> attr_value('attr', widget, data)
    Traceback (most recent call last):
      ...
    Exception: failing_func_callback

    >>> def bc_func_callback(widget, data):
    ...     return 'bc_func_callback value'
    >>> widget.attrs['attr'] = bc_func_callback
    >>> attr_value('attr', widget, data)
    'bc_func_callback value'

    >>> def failing_bc_func_callback(widget, data):
    ...     raise Exception('failing_bc_func_callback')
    >>> widget.attrs['attr'] = failing_bc_func_callback
    >>> attr_value('attr', widget, data)
    Traceback (most recent call last):
      ...
    Exception: failing_bc_func_callback

    >>> class FormContext(object):
    ...     def instance_callback(self, widget, data):
    ...         return 'instance_callback'
    ...
    ...     def failing_instance_callback(self, widget, data):
    ...         raise Exception('failing_instance_callback')
    ...
    ...     def instance_bc_callback(self):
    ...         return 'instance_bc_callback'
    ...
    ...     def failing_instance_bc_callback(self, widget, data):
    ...         raise Exception('failing_instance_bc_callback')

    >>> context = FormContext()
    >>> widget.attrs['attr'] = context.instance_callback
    >>> attr_value('attr', widget, data)
    'instance_callback'

    >>> widget.attrs['attr'] = context.failing_instance_callback
    >>> attr_value('attr', widget, data)
    Traceback (most recent call last):
      ...
    Exception: failing_instance_callback

    >>> widget.attrs['attr'] = context.instance_bc_callback
    >>> attr_value('attr', widget, data)
    'instance_bc_callback'

    >>> widget.attrs['attr'] = context.failing_instance_bc_callback
    >>> attr_value('attr', widget, data)
    Traceback (most recent call last):
      ...
    Exception: failing_instance_bc_callback


Test generic_html5_attrs
------------------------

::
    >>> from yafowil.utils import generic_html5_attrs
    >>> generic_html5_attrs(
    ...     {'foo': 'bar', 'baz': ['bam'], 'nada': None, 'unset': UNSET})
    {'data-baz': '["bam"]', 'data-foo': 'bar'}


Test data_attrs_helper
----------------------

::
    >>> from node.base import AttributedNode
    >>> from yafowil.utils import data_attrs_helper

    >>> widget = AttributedNode()
    >>> data = AttributedNode()

    >>> widget.attrs['testattr1'] = 'value'
    >>> widget.attrs['testattr2'] = True
    >>> widget.attrs['testattr3'] = False
    >>> widget.attrs['testattr4'] = None
    >>> widget.attrs['testattr5'] = ['item1', 'item2', 'item3']
    >>> widget.attrs['testattr6'] = {'key1': 'item1', 'key2': 'item2', 'key3': 'item3'}
    >>> widget.attrs['testattr7'] = 1234
    >>> widget.attrs['testattr8'] = 1234.5678
    >>> widget.attrs['camelAttrName'] = 'camelValue'

    >>> data_attrs_keys = ['testattr1', 'testattr2', 'testattr3', 'testattr4', 'testattr5', 'testattr6', 'testattr7', 'testattr8', 'camelAttrName']
    >>> data_attrs = data_attrs_helper(widget, data, data_attrs_keys)

    >>> data_attrs['data-testattr1']
    'value'

    >>> data_attrs['data-testattr2']
    'true'

    >>> data_attrs['data-testattr3']
    'false'

    >>> 'data-testattr4' in data_attrs
    False

    >>> data_attrs['data-testattr5']
    '["item1", "item2", "item3"]'

    >>> data_attrs['data-testattr6']
    '{"key3": "item3", "key2": "item2", "key1": "item1"}'

    >>> data_attrs['data-testattr7']
    '1234'

    >>> data_attrs['data-testattr8']
    '1234.5678'

    >>> data_attrs['data-camel-attr-name']
    'camelValue'


    Test with Tag renderer

    >>> from yafowil.utils import Tag
    >>> tag = Tag(lambda msg: msg)
    >>> tag('dummy', name='foo', **data_attrs)
    u'<dummy data-camel-attr-name=\'camelValue\' data-testattr1=\'value\' data-testattr2=\'true\' data-testattr3=\'false\' data-testattr5=\'["item1", "item2", "item3"]\' data-testattr6=\'{"key3": "item3", "key2": "item2", "key1": "item1"}\' data-testattr7=\'1234\' data-testattr8=\'1234.5678\' name="foo" />'
