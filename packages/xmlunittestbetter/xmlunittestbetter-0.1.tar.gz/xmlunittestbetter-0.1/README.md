Python XML-Unittest
===================
[![Build Status](https://travis-ci.org/richardasaurus/python-xmlunittest-better.png?branch=master)](https://travis-ci.org/richardasaurus/python-xmlunittest-better)
[![Downloads](https://pypip.in/d/xmlunittestbetter/badge.png)](https://crate.io/packages/xmlunittestbetter/)

This is a spork of [https://github.com/Exirel/python-xmlunittest](https://github.com/Exirel/python-xmlunittest).
With wider lxml support and Python 2.7, 3.4 & 3.4 support.


Examples
======

- Extend xmlunittest.XmlTestCase
- Write your tests, using the function or method that generate XML document
- Use xmlunittest.XmlTestCase‘s assertion methods to validate
- Keep your test readable

Example:

```

    from xmlunittest import XmlTestCase


    class CustomTestCase(XmlTestCase):

        def test_my_custom_test(self):
            # In a real case, data come from a call to your function/method.
            data = """<?xml version="1.0" encoding="UTF-8" ?>
            <root xmlns:ns="uri">
                <leaf id="1" active="on" />
                <leaf id="2" active="on" />
                <leaf id="3" active="off" />
            </root>"""

            # Everything starts with `assert_xml_document`
            root = self.assert_xml_document(data)

            # Check namespace
            self.assert_xml_namespace(root, 'ns', 'uri')
            # Check
            self.assert_xpaths_unique_value(root, ('./leaf@id', ))
            self.assert_xpath_values(root, './leaf@active', ('on', 'off'))
```

Running the tests
======

To run the unit tests for this package::

```
    pip install tox
    tox
```
