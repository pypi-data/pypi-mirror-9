Richtext widget
===============


Features
--------

    - renders textarea with richtext css class and provides tinymce resources
      You have to bind the editor via JS in you integration package.

Load requirements::

    >>> import yafowil.loader
    >>> import yafowil.widget.richtext

Test widget::

    >>> from yafowil.base import factory

Render widget::

    >>> widget = factory('richtext', 'rt', props={'required': True})
    >>> widget()
    u'<textarea class="richtext" cols="80" id="input-rt" name="rt" required="required" rows="25"></textarea>'
    
Widget extraction::

    >>> request = {'rt': ''}
    >>> data = widget.extract(request)

No input was given::

    >>> data.errors
    [ExtractionError('Mandatory field was empty',)]

Empty string in extracted::

    >>> data.extracted
    ''

Widget extraction. Returns markup from tinymce::

    >>> request = {'rt': '<p>1</p>'}
    >>> data = widget.extract(request)
    >>> data.errors
    []
    
    >>> data.extracted
    '<p>1</p>'
    
    >>> widget(data)
    u'<textarea class="richtext" cols="80" id="input-rt" name="rt" required="required" rows="25"><p>1</p></textarea>'

Display renderer::

    >>> widget = factory('richtext', 'rt', value='<p>foo</p>', mode='display')
    >>> widget()
    u'<div class="display-richtext"><p>foo</p></div>'
    
    >>> widget = factory('richtext', 'rt', mode='display')
    >>> widget()
    u'<div class="display-richtext"></div>'
