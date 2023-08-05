=========
Slingshot
=========

Extension for the official ElasticSearch python client providing an ``indices_manager`` to create and manage indices with read and write aliases, and perform no-downtime migrations.


Installation
============
::

    pip install slingshot


Usage
=====

Instantiation
-------------

::

    from weakref import proxy
    from elasticsearch.client import Elasticsearch
    from slingshot.indices_manager import IndiciesManagerClient

    es = Elasticsearch()
    es.indices_manager = IndicesManagerClient(proxy(es))


Creation of a Managed Index
---------------------------

::

    es.indices_manager.create('slingshot', body={"settings": {"number_of_shards": 1, "number_of_replicas": 1}})

This creates an index with read and write aliases:

    * Creates the index "slingshot.{creation_timestamp}"
    * Creates a read alias "slingshot"
    * Creates a write alias "slingshot.write"

Upgrading an Existing Index
---------------------------

Slingshot manages the read and write aliases for the indices it creates. However, you can upgrade an index that was not created with slingshot. It will simply create a write alias to handle migrations.

::

    es.indices_manager.manage('existing_index')


Migration of a Managed Index
----------------------------

::

    es.indices_manager.migrate('slingshot', body={"settings": {"number_of_shards": 5, "number_of_replicas": 1}})

This allows to perform changes to an index and migrate documents to take advantage of new mappings:

    * creates a new index "slingshot.{modification_timestamp}" with a new configuration (e.g. 5 shards instead of 1)
    * swaps write alias to the new index
    * scans and bulk imports all documents (optionally ignoring types or performing transformations)
    * swaps read alias
    * deletes original index (can be skipped)

Note that the index must be created or upgraded with slingshot (by creating a write alias or using the ``manage`` method)


Transforming Documents
**********************

When migrating, it can be useful to transform documents to match a new mapping.

::

    def transform_my_docs(doc):
        # recompute some fields
        doc['_source']['discount'] = doc['_source']['price'] / doc['_source']['value'] * 100.0

        # drop some fields
        doc['_source'].pop('useless')

        # drop documents based on some business rules (assumes the field is first cast to a datetime)
        if doc['_source]]['expires_at'] < datetime.now():
            return None

        # Don't forget to return the modified document
        return doc

    es.indices_manager.migrate('slingshot', body=config_dict_or_string, transform=transform_my_docs)


Ignoring Document Types
***********************

It can also be useful to ignore some document types altogether.
::

    es.indices_manager.migrate('slingshot', body=config_dict_or_string, ignore_types=["my_type_1", "my_type_2"])



Keeping the Source Index
************************

If for any reason you wish to keep the original index (e.g. to rollback in case anything goes wrong) after the migration::

    es.indices_manager.migrate('slingshot', body=config_dict_or_string, keep_source=True)


Warning
*******

Slingshot is unable to predict what needs to be done with the settings, mappings, aliases, etc. of the new index.

Therefore, when migrating, body must contain all the relevant configuration to create an index from scratch.
This can include settings, mappings, aliases, templates, warmers or anything supported by the elasticsearch index API.

However, slingshot manages the migration of the write alias and the read alias (if it exists).

Running Tests
=============

Get a copy of the repository::

    git clone git@github.com:OohlaLabs/slingshot.git .

Install `tox <https://pypi.python.org/pypi/tox>`_::

    pip install tox

Run the tests::

    tox

Future Plans
============

Having an easy API for migrating indices can be useful by itself. However, this usually needs to be done in the context of the deployment of an application of some sort.

The plan is for slingshot to provide a command line interface as well as a programmatic API to support both use-cases.

E.g command line interface::

    $ slingshot indices_manager create my_index --body=settings.json
    $ slingshot indices_manager migrate my_index --body=settings.yml --transform="path.to.module:transform" --ignore_types=type_1,type_2
    $ slingshot indices_manager manage my_existing_index

Since the official ElasticSearch python client provides a very clean and consistent low-level interface, there is no reasons why this command line tool could not interface its methods in the same way::

    $ slingshot indices delete my_index
    $ slingshot cluster health my_index

Hosts urls could be managed by a ~/.slingshot/hosts or passed directly as a command line argument::

    $ slingshot indices create my_index --hosts=my_host,my_other_host
    $ slingshot cluster health my_index --hosts=http://localhost:9200/

That's the plan!

Contributions
=============

All contributions and comments are welcome. Simply create a pull request or report a bug.

Changelog
=========

v0.0.1
------
* Initial


