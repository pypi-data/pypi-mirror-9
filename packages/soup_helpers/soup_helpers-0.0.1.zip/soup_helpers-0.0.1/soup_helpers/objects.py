import re

from bs4 import BeautifulSoup

def assertFormFieldExists(content, tag, field_name):
    soup = BeautifulSoup(content)
    assert soup.find(tag, {'name': field_name}), \
        'no {} element found with the name "{}"'.format(
            tag, field_name)

def assertInputValueEquals(content, field_name, value):
    soup = BeautifulSoup(content)
    field = soup.find('input', {'name': field_name})
    assert value == field.get('value'), \
        '{} value "{}" does not equal "{}"'.format(
            field_name, field.get('value', ''), value)

def assertSelectHasOptions(content, field_name, options_tuple):
    soup = BeautifulSoup(content)
    field = soup.find('select', {'name': field_name})
    field_options = tuple(
        o.string for o in field.findAll('option'))
    if field_options != options_tuple:
        raise AssertionError(
            '{} does not match the options given'.format(
                field_name))

def assertSelectHasSelectedOption(content, field_name, text):
    soup = BeautifulSoup(content)
    field = soup.find('select', {'name': field_name})
    desired_option = field.find('option', text=text)

    if desired_option is None:
        raise AssertionError(
            '{} has no option with text "{}"'.format(
                field_name, text))

    assert 'selected' in desired_option.attrs, \
        '{} option "{}" is not selected'.format(
            field_name, text)

def assertTagWithTextExists(content, tag, text):
    soup = BeautifulSoup(content)
    assert soup.find(tag, text=text), \
        'no {} element found with text "{}"'.format(tag, text)

def assertTextAreaContainsText(content, field_name, text):
    soup = BeautifulSoup(content)
    field = soup.find('textarea', {'name': field_name})
    field_text = re.sub(
        r'\s{2,}', ' ', field.text).strip()
    assert text in field_text, \
        '{} text "{}" does not contain "{}"'.format(
            field_name, field_text, text)
