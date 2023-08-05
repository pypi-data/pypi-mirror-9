Soup Helpers
------------


Misc Methods

    >>> assertPageTitleEquals(content, title='My Title')

    >>> assertTagWithTextExists(content, tag='p', text='some text')


Form Methods

    >>> assertFormFieldExists(content, tag='input', field_name='my_field')
    >>> assertFormFieldExists(content, tag='select', field_name='my_field')
    >>> assertFormFieldExists(content, tag='textarea', field_name='my_field')

    >>> assertInputValueEquals(content, field_name='my_field', value='my value')
    >>> assertInputValueEquals(content, field_name='my_field', value=None)

    >>> assertSelectHasOptions(content, field_name='my_field', options_tuple=('One', 'Two'))

    >>> assertSelectHasSelectedOption(content, field_name='my_field', text='my selected text')

    >>> assertTextAreaContainsText(content, field_name='my_field', text='some textarea text')