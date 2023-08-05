Import requirements::

    >>> import yafowil.loader
    >>> import yafowil.widget.dict
    >>> from yafowil.base import factory

Create empty Dict widget::

    >>> form = factory('form',
    ...                name='myform',
    ...                props={'action': 'myaction'})
    >>> form['mydict'] = factory('dict',
    ...                          props={
    ...                              'head': {
    ...                                  'key': 'Key',
    ...                                  'value': 'Value',
    ...                              }
    ...                          })
    >>> pxml(form())
    <form action="myaction" enctype="multipart/form-data" id="form-myform" method="post" novalidate="novalidate">
      <table class="dictwidget key-keyfield value-valuefield" id="dictwidget_myform.mydict.entry">
        <thead>
          <tr>
            <th>Key</th>
            <th>Value</th>
            <th class="actions">
              <div class="dict_actions">
                <a class="dict_row_add" href="#">
                  <span class="icon-plus-sign"> </span>
                </a>
              </div>
            </th>
          </tr>
        </thead>
        <tbody/>
      </table>
    </form>
    <BLANKLINE>

Create dict widget with preset values::

    >>> from odict import odict
    >>> value = odict()
    >>> value['key1'] = u'Value1'
    >>> value['key2'] = u'Value2'
    >>> form = factory('form',
    ...                name='myform',
    ...                props={'action': 'myaction'})
    >>> form['mydict'] = factory('dict',
    ...                          value=value,
    ...                          props={
    ...                              'head': {
    ...                                  'key': 'Key',
    ...                                  'value': 'Value',
    ...                              }
    ...                          })
    >>> pxml(form())
    <form action="myaction" enctype="multipart/form-data" id="form-myform" method="post" novalidate="novalidate">
      <table class="dictwidget key-keyfield value-valuefield" id="dictwidget_myform.mydict.entry">
        <thead>
          <tr>
            <th>Key</th>
            <th>Value</th>
            <th class="actions">
              <div class="dict_actions">
                <a class="dict_row_add" href="#">
                  <span class="icon-plus-sign"> </span>
                </a>
              </div>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="key">
              <input class="keyfield" id="input-myform-mydict-entry0-key" name="myform.mydict.entry0.key" type="text" value="key1"/>
            </td>
            <td class="value">
              <input class="valuefield" id="input-myform-mydict-entry0-value" name="myform.mydict.entry0.value" type="text" value="Value1"/>
            </td>
            <td class="actions">
              <div class="dict_actions">
                <a class="dict_row_add" href="#">
                  <span class="icon-plus-sign"> </span>
                </a>
                <a class="dict_row_remove" href="#">
                  <span class="icon-minus-sign"> </span>
                </a>
                <a class="dict_row_up" href="#">
                  <span class="icon-circle-arrow-up"> </span>
                </a>
                <a class="dict_row_down" href="#">
                  <span class="icon-circle-arrow-down"> </span>
                </a>
              </div>
            </td>
          </tr>
          <tr>
            <td class="key">
              <input class="keyfield" id="input-myform-mydict-entry1-key" name="myform.mydict.entry1.key" type="text" value="key2"/>
            </td>
            <td class="value">
              <input class="valuefield" id="input-myform-mydict-entry1-value" name="myform.mydict.entry1.value" type="text" value="Value2"/>
            </td>
            <td class="actions">
              <div class="dict_actions">
                ...
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </form>
    <BLANKLINE>

Base Extraction::

    >>> form.printtree()
    <class 'yafowil.base.Widget'>: myform
      <class 'yafowil.base.Widget'>: mydict
        <class 'yafowil.base.Widget'>: table
          <class 'yafowil.base.Widget'>: head
            <class 'yafowil.base.Widget'>: row
              <class 'yafowil.base.Widget'>: key
              <class 'yafowil.base.Widget'>: value
              <class 'yafowil.base.Widget'>: actions
          <class 'yafowil.base.Widget'>: body
            <class 'yafowil.base.Widget'>: entry0
              <class 'yafowil.base.Widget'>: key
              <class 'yafowil.base.Widget'>: value
              <class 'yafowil.base.Widget'>: actions
            <class 'yafowil.base.Widget'>: entry1
              <class 'yafowil.base.Widget'>: key
              <class 'yafowil.base.Widget'>: value
              <class 'yafowil.base.Widget'>: actions

    >>> request = {
    ...     'myform.mydict.entry0.key': 'key1',
    ...     'myform.mydict.entry0.value': 'New Value 1',
    ...     'myform.mydict.entry1.key': 'key2',
    ...     'myform.mydict.entry1.value': 'New Value 2',
    ... }
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict.entry0.value').extracted
    'New Value 1'

    >>> data.fetch('myform.mydict.entry1.value').extracted
    'New Value 2'

    >>> data.fetch('myform.mydict').extracted
    odict([('key1', 'New Value 1'), ('key2', 'New Value 2')])

Dict entries increased in UI::

    >>> request = {
    ...     'myform.mydict.entry0.key': 'key1',
    ...     'myform.mydict.entry0.value': 'New Value 1',
    ...     'myform.mydict.entry1.key': 'key2',
    ...     'myform.mydict.entry1.value': 'New Value 2',
    ...     'myform.mydict.entry2.key': 'key3',
    ...     'myform.mydict.entry2.value': 'New Value 3',
    ... }
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').extracted
    odict([('key1', 'New Value 1'), 
    ('key2', 'New Value 2'), 
    ('key3', 'New Value 3')])

    >>> form(data=data)
    u'<form action="myaction" enctype="multipart/form-data" 
    ... 
    value="New Value 1" 
    ...
    value="New Value 2" 
    ...
    value="New Value 3" 
    ...

Dict entries decreased in UI::

    >>> request = {
    ...     'myform.mydict.entry0.key': 'key1',
    ...     'myform.mydict.entry0.value': 'Very New Value 1',
    ... }
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').extracted
    odict([('key1', 'Very New Value 1')])

    >>> form(data=data)
    u'<form action="myaction" enctype="multipart/form-data" 
    ... 
    value="Very New Value 1" 
    ...

    >>> form(data=data).find('New Value 2')
    -1

Empty keys are ignored::

    >>> request = {
    ...     'myform.mydict.entry0.key': 'key1',
    ...     'myform.mydict.entry0.value': 'Very New Value 1',
    ...     'myform.mydict.entry1.key': '',
    ...     'myform.mydict.entry1.value': '',
    ... }
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').extracted
    odict([('key1', 'Very New Value 1')])

Check required::

    >>> form['mydict'] = factory('error:dict',
    ...                          props={
    ...                              'required': 'I am required',
    ...                              'head': {
    ...                                  'key': 'Key',
    ...                                  'value': 'Value',
    ...                              }
    ...                          })
    >>> request = {}
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').errors
    [ExtractionError('I am required',)]

    >>> data.printtree()
    <RuntimeData myform, value=<UNSET>, extracted=odict([('mydict', <UNSET>)]) at ...>
      <RuntimeData myform.mydict, value=<UNSET>, extracted=<UNSET>, 1 error(s) at ...>

    >>> pxml(form(data=data))
    <form action="myaction" enctype="multipart/form-data" id="form-myform" method="post" novalidate="novalidate">
      <div class="error">
        <div class="errormessage">I am required</div>
        <table class="dictwidget key-keyfield value-valuefield" id="dictwidget_myform.mydict.entry">
          <thead>
            <tr>
              <th>Key</th>
              <th>Value</th>
              <th class="actions">
                <div class="dict_actions">
                  <a class="dict_row_add" href="#">
                    <span class="icon-plus-sign"> </span>
                  </a>
                </div>
              </th>
            </tr>
          </thead>
          <tbody/>
        </table>
      </div>
    </form>
    <BLANKLINE>

    >>> request = {
    ...     'myform.mydict.entry0.key': 'key1',
    ...     'myform.mydict.entry0.value': 'Very New Value 1',
    ... }
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').errors
    []

    >>> form(data=data)
    u'<form action="myaction" enctype="multipart/form-data" 
    ... 
    value="Very New Value 1" 
    ...

    >>> form(data=data).find('error')
    -1

Use dict widget as static widget::

    >>> form['mydict'] = factory('error:dict',
    ...                          value=odict([('k1', 'v1')]),
    ...                          props={
    ...                              'required': 'I am required',
    ...                              'static': True,
    ...                              'head': {
    ...                                  'key': 'Key',
    ...                                  'value': 'Value',
    ...                              }
    ...                          })
    >>> pxml(form())
    <form action="myaction" enctype="multipart/form-data" id="form-myform" method="post" novalidate="novalidate">
      <table class="dictwidget key-keyfield value-valuefield" id="dictwidget_myform.mydict.entry">
        <thead>
          <tr>
            <th>Key</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td class="key">
              <input class="keyfield" disabled="disabled" id="input-myform-mydict-entry0-key" name="myform.mydict.entry0.key" type="text" value="k1"/>
            </td>
            <td class="value">
              <input class="valuefield" id="input-myform-mydict-entry0-value" name="myform.mydict.entry0.value" type="text" value="v1"/>
            </td>
          </tr>
        </tbody>
      </table>
    </form>
    <BLANKLINE>

Static dict extraction. Disabled form fields are not transmitted, but since
order is fixed dict could be reconstructed from original value::

    >>> request = {
    ...     'myform.mydict.entry0.value': 'New Value 1',
    ... }
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').extracted
    odict([('k1', 'New Value 1')])

Since its static, we expect an extraction error if someone tries to add values::

    >>> request = {
    ...     'myform.mydict.entry0.value': 'New Value 1',
    ...     'myform.mydict.entry1.key'  : 'Wrong Key 2',
    ...     'myform.mydict.entry1.value': 'Wrong Value 2',
    ... }
    >>> data = form.extract(request=request)
    >>> data['mydict'].errors
    [ExtractionError('Invalid number of static values',)]

Static dicts required. By default checks if there's a value in every entry::

    >>> request = {}
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').errors
    [ExtractionError('I am required',)]

    >>> request = {
    ...     'myform.mydict.entry0.value': '',
    ... }
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').errors
    [ExtractionError('I am required',)]

Static required rendering::

    >>> pxml(form(data))
    <form action="myaction" enctype="multipart/form-data" id="form-myform" method="post" novalidate="novalidate">
      <div class="error">
        <div class="errormessage">I am required</div>
        <table class="dictwidget key-keyfield value-valuefield" id="dictwidget_myform.mydict.entry">
          <thead>
            <tr>
              <th>Key</th>
              <th>Value</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td class="key">
                <input class="keyfield" disabled="disabled" id="input-myform-mydict-entry0-key" name="myform.mydict.entry0.key" type="text" value="k1"/>
              </td>
              <td class="value">
                <input class="valuefield" id="input-myform-mydict-entry0-value" name="myform.mydict.entry0.value" type="text" value=""/>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </form>
    <BLANKLINE>

Required message not set directly in widget props::

    >>> form['mydict'].attrs['required'] = True
    >>> request = {
    ...     'myform.mydict.entry0.value': '',
    ... }
    >>> data = form.extract(request=request)
    >>> data.fetch('myform.mydict').errors
    [ExtractionError('Mandatory field was empty',)]

Dict display renderer::

    >>> value = odict()
    >>> value['foo'] = 'Foo'
    >>> value['bar'] = 'Bar'
    >>> widget = factory('dict',
    ...                  name='display_dict',
    ...                  value=value,
    ...                  props={
    ...                      'head': {
    ...                          'key': 'Key',
    ...                          'value': 'Value',
    ...                      }
    ...                  },
    ...                  mode='display')
    >>> pxml('<div>' + widget() + '</div>')
    <div>
      <h5>Key: Value</h5>
      <dl>
        <dt>foo</dt>
        <dd>Foo</dd>
        <dt>bar</dt>
        <dd>Bar</dd>
      </dl>
    </div>
    <BLANKLINE>

    >>> widget = factory('dict',
    ...                  name='display_dict',
    ...                  props={
    ...                      'head': {
    ...                          'key': 'Key',
    ...                          'value': 'Value',
    ...                      }
    ...                  },
    ...                  mode='display')
    >>> pxml('<div>' + widget() + '</div>')
    <div>
      <h5>Key: Value</h5>
      <dl/>
    </div>
    <BLANKLINE>
