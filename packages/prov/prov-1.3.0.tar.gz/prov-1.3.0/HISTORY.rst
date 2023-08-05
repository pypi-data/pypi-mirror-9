.. :changelog:

History
-------

1.3.0 (2015-02-03)
^^^^^^^^^^^^^^^^^^
* Python 3.3 and 3.4 supported
* Updated prov-convert script to support XML output
* Added missing test JSON and XML files in distributions


1.2.0 (2014-12-19)
^^^^^^^^^^^^^^^^^^
* Added: :py:meth:`prov.graph.prov_to_graph` to convert a :py:class:`~prov.model.ProvDocument` to a `MultiDiGraph <http://networkx.github.io/documentation/latest/reference/classes.multidigraph.html>`_
* Added: PROV-N serializer
* Fixed: None values for empty formal attributes in PROV-N output (issue #60)
* Fixed: PROV-N representation for xsd:dateTime (issue #58)
* Fixed: Unintended merging of Identifier and QualifiedName values
* Fixed: Cloning the records when creating a new document from them
* Fixed: incorrect SoftwareAgent records in XML serialization

1.1.0 (2014-08-21)
^^^^^^^^^^^^^^^^^^
* Added: Support for `PROV-XML <http://www.w3.org/TR/prov-xml/>`_ serialization and deserialization
* A :py:class:`~prov.model.ProvRecord` instance can now be used as the value of an attributes
* Added: convenient assertions methods for :py:class:`~prov.model.ProvEntity`, :py:class:`~prov.model.ProvActivity`, and :py:class:`~prov.model.ProvAgent`
* Added: :py:meth:`prov.model.ProvDocument.update` and :py:meth:`prov.model.ProvBundle.update`
* Fixed: Handling default namespaces of bundles when flattened

1.0.1 (2014-08-18)
^^^^^^^^^^^^^^^^^^
* Added: Default namespace inheritance for bundles
* Fixed: :py:meth:`prov.model.NamespaceManager.valid_qualified_name` did not support :py:class:`~prov.model.XSDQName`
* Added: Convenience :py:func:`prov.read` method with a lazy format detection
* Added: Convenience :py:meth:`~prov.model.ProvBundle.plot` method on the :py:class:`~prov.model.ProvBundle` class (requiring matplotlib).
* Changed: The previous :py:meth:`!add_record` method renamed to :py:meth:`~prov.model.ProvBundle.new_record`
* Added: :py:meth:`~prov.model.ProvBundle.add_record` function which takes one argument, a :py:class:`~prov.model.ProvRecord`, has been added
* Fixed: Document flattening (see :py:meth:`~prov.model.ProvDocument.flattened`)
* Added: :py:meth:`~prov.model.ProvRecord.__hash__` function added to :py:class:`~prov.model.ProvRecord` (**at risk**: to be removed as :py:class:`~prov.model.ProvRecord` is expected to be mutable)
* Added: :py:attr:`~prov.model.ProvRecord.extra_attributes` added to mirror existing :py:attr:`~prov.model.ProvRecord.formal_attributes`

1.0.0 (2014-07-15)
^^^^^^^^^^^^^^^^^^

* The underlying data model has been rewritten and is **incompatible** with pre-1.0 versions.
* References to PROV elements (i.e. entities, activities, agents) in relation records are now QualifiedName instances.
* A document or bundle can have multiple records with the same identifier.
* PROV-JSON serializer and deserializer are now separated from the data model. 
* Many tests added, including round-trip PROV-JSON encoding/decoding.
* For changes pre-1.0, see CHANGES.txt.
