# coding=utf-8
from datetime import date

import solution as f


to_unicode = f._compat.to_unicode


def test_render_date():
    field = f.Date()
    field.name = u'abc'
    field.load_data(obj_value=date(1979, 5, 13))

    assert field() == field.as_input()
    assert (field(foo='bar') ==
            u'<input foo="bar" name="abc" type="date" value="1979-05-13">')
    assert (field.as_textarea(foo='bar') ==
            u'<textarea foo="bar" name="abc">1979-05-13</textarea>')
    assert (field(foo='bar', type='text') ==
            u'<input foo="bar" name="abc" type="text" value="1979-05-13">')


def test_render_required():
    field = f.Date(validate=[f.Required])
    field.name = u'abc'
    assert field() == u'<input name="abc" type="date" value="" required>'
    assert field.as_textarea() == u'<textarea name="abc" required></textarea>'


def test_render_default():
    field = f.Date(default=date(2013, 7, 28))
    field.name = u'abc'
    assert field() == u'<input name="abc" type="date" value="2013-07-28">'


def test_validate_date():
    field = f.Date()
    assert field.validate() is None

    field = f.Date()
    field.load_data(u'1979-05-13')
    assert field.validate() == date(1979, 5, 13)

    field = f.Date()
    field.load_data([u'1979-05-13'])
    assert field.validate() == date(1979, 5, 13)

    field = f.Date()
    field.load_data(u'invalid')
    assert field.validate() is None


def test_validate_date_with_default():
    today = date.today()
    field = f.Date(default=today)
    assert field.validate() == today

