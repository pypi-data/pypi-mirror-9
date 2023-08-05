Soup Helpers
--------

Examples

    >>> assertFormFieldExists(content, 'input', 'my_field')
    >>> assertFormFieldExists(content, 'select', 'my_field')
    >>> assertFormFieldExists(content, 'textarea', 'my_field')

    >>> assertInputValueEquals(content, 'my_field', 'my value')
    >>> assertInputValueEquals(content, 'my_field', None)

    >>> assertSelectHasOptions(content, 'my_field', ('One', 'Two'))

    >>> assertSelectHasSelectedOption(content, 'my_field', 'my selected text')

    >>> assertTagWithTextExists(content, 'p', 'some text')

    >>> assertTextAreaContainsText(content, 'my_field', 'some textarea text')