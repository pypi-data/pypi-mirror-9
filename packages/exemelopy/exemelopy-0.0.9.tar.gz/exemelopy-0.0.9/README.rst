exemelopy
=========
|travis_status|_

exemelopy aims to be an easy-to-use tool for building an XML 
document from native Python data-types without any intervention;
akin to the json_ and simplejson_ modules, but for XML.

This package depends on lxml_ to create valid XML output.

USAGE
-----

::

    from exemelopy import XMLEncoder
    xml = XMLEncoder({'a': 1, 'b': True, 'spam': 'eggs'}).to_string()
    print xml

Which will return the following output::

    <?xml version='1.0' encoding='UTF-8'?>
    <document>
      <a>1</a>
      <b nodetype="boolean">true</b>
      <spam>eggs</spam>
    </document>

.. _simplejson: http://simplejson.readthedocs.org/
.. _json: http://docs.python.org/library/json.html
.. _lxml: http://lxml.de/
.. |travis_status| image:: https://secure.travis-ci.org/unpluggd/exemelopy.png
.. _travis_status: https://secure.travis-ci.org/unpluggd/exemelopy
