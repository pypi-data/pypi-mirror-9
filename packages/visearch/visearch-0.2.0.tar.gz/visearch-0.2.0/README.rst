ViSearch Python SDK
===================

.. image:: https://img.shields.io/travis/chrishan/visearch.svg
        :target: https://travis-ci.org/chrishan/visearch

.. image:: https://img.shields.io/pypi/v/visearch.svg
        :target: https://pypi.python.org/pypi/visearch

.. contents::

1. Overview
-----------

ViSearch is an API that provides accurate, reliable and scalable image
search. ViSearch API provides endpoints that let developers index their
images and perform image searches efficiently. ViSearch API can be
easily integrated into your web and mobile applications. More details
about ViSearch API can be found in the
`documentation <http://www.visenze.com/docs/overview/introduction>`__.

The ViSearch Python SDK is an open source software for easy integration
of ViSearch Search API with your application server. It provides three
search methods based on the ViSearch Search API - pre-indexed search,
color search and upload search. The ViSearch Python SDK also provides an
easy integration of the ViSearch Data API which includes data inserting
and data removing. For source code and references, visit the github
`repository <https://github.com/chrishan/visearch-sdk-python>`__.

* Supported on Python 2.7+ and 3.4+

2. Setup
--------

To install visearch, simply:

::

    $ pip install visearch

3. Initialization
-----------------

To start using ViSearch API, initialize ViSearch client with your
ViSearch API credentials. Your credentials can be found in `ViSearch
Dashboard <https://dashboard.visenze.com>`__:

.. code:: python


    from visearch import client

    access_key = 'your app access key'
    secret_key = 'your app secret key'

    api = client.ViSearchAPI(access_key, secret_key)

4. Indexing Images
------------------

4.1 Indexing Your First Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Built for scalability, ViSearch API enables fast and accurate searches
on high volume of images. Before making your first image search, you
need to prepare a list of images and index them into ViSearch by calling
the /insert endpoint. Each image must have a unique identifier and a
publicly downloadable URL. ViSearch will parallelly fetch your images
from the given URLs, and index the downloaded for searching. After the
image indexes are built, you can start searching for `similar images
using the unique
identifier <https://github.com/visenze/visearch-sdk-java/blob/master/README.md#51-pre-indexed-search>`__,
`using a
color <https://github.com/visenze/visearch-sdk-java/blob/master/README.md#52-color-search>`__,
or `using another
image <https://github.com/visenze/visearch-sdk-java/blob/master/README.md#53-upload-search>`__.

To index your images, prepare a list of images and call the /insert
endpoint.

.. code:: python

    # the list of images to be indexed
    # the unique identifier of the image 'im_name', the publicly downloadable url of the image 'im_url'
    images = [
        {'im_name': 'red_dress', 'im_url': 'http://mydomain.com/images/red_dress.jpg'},
        {'im_name': 'blue_dress', 'im_url': 'http://mydomain.com/images/blue_dress.jpg'}
    ]
    # calls the /insert endpoint to index the image
    response = api.insert(images)

    Each ``insert`` call to ViSearch accepts a maximum of 100 images. We
    recommend indexing your images in batches of 100 for optimized image
    indexing speed.

4.2 Image with Metadata
~~~~~~~~~~~~~~~~~~~~~~~

Images usually come with descriptive text or numeric values as metadata,
for example: title, description, category, brand, and price of an online
shop listing image caption, tags, geo-coordinates of a photo.

ViSearch combines the power of text search with image search. You can
index your images with metadata, and leverage text based query and
filtering for even more accurate image search results, for example:
limit results within a price range limit results to certain tags, and
some keywords in the captions For detailed reference for result
filtering, see `Advanced Search
Parameters <https://github.com/visenze/visearch-sdk-php/blob/master/README.md#7-advanced-search-parameters>`__.

To index your images with metadata, first you need to configure the
metadata schema in ViSearch Dashboard (link to). You can add and remove
metadata keys, and modify the metadata types to suit your needs.

Let's assume you have the following metadata schema configured:

+---------------+----------+--------------+
| Name          | Type     | Searchable   |
+===============+==========+==============+
| title         | string   | true         |
+---------------+----------+--------------+
| description   | text     | true         |
+---------------+----------+--------------+
| price         | float    | true         |
+---------------+----------+--------------+

Then index your image with title, decription, and price:

.. code:: python

    images = [{
               'im_name': 'blue_dress',
               'im_url': 'http://mydomain.com/images/blue_dress.jpg',
               'title': 'Blue Dress',
               'description': 'A blue dress',
               'price': 100.0
              },
              ...
             ]
    # calls the /insert endpoint to index the image
    response = api.insert(images)

Metadata keys are case-sensitive, and metadata without a matching key in
the schema will not be processed by ViSearch. Make sure to configure
metadata schema for all of your metadata keys.

4.3 Updating Images
~~~~~~~~~~~~~~~~~~~

If you need to update an image or its metadata, call the ``insert``
endpoint with the same unique identifier of the image. ViSearch will
fetch the image from the updated URL and index the new image, and
replace the metadata of the image if provided.

.. code:: python

    images = [{
               'im_name': 'blue_dress',
               'im_url': 'http://mydomain.com/images/blue_dress.jpg',
               'title': 'Blue Dress',
               'description': 'A blue dress',
               'price': 100.0
              },
              ...
             ]
    # calls the /update endpoint to index the image
    response = api.update(images)

    Each ``insert`` call to ViSearch accepts a maximum of 100 images. We
    recommend updating your images in batches of 100 for optimized image
    indexing speed.

4.4 Removing Images
~~~~~~~~~~~~~~~~~~~

In case you decide to remove some of the indexed images, you can call
the /remove endpoint with the list of unique identifier of the indexed
images. ViSearch will then remove the specified images from the index.
You will not be able to perform pre-indexed search on this image, and
the image will not be found in any search result.

.. code:: python

    image_names = ["red_dress", "blue_dress"]
    response = api.remove(image_names)

    We recommend calling ``remove`` in batches of 100 images for
    optimized image indexing speed.

5. Searching Images
-------------------

5.1 Pre-indexed Search
~~~~~~~~~~~~~~~~~~~~~~

Pre-index search is to search similar images based on the your indexed
image by its unique identifier (im\_name). It should be a valid ID that
is used to index your images in the database.

.. code:: python

    response = api.search("blue_dress")

5.2 Color Search
~~~~~~~~~~~~~~~~

Color search is to search images with similar color by providing a color
code. The color code should be in Hexadecimal and passed to the
colorsearch service.

.. code:: python

    response = api.colorsearch("fa4d4d")

5.3 Upload Search
~~~~~~~~~~~~~~~~~

Upload search is used to search similar images by uploading an image or
providing an image url. ``Image`` class is used to perform the image
encoding and resizing. You should construct the ``Image`` object and
pass it to uploadsearch to start a search.

Using an image from a local file path

.. code:: python

    image_path = 'blue_dress.jpg'
    response = api.uploadsearch(image_path=image_path)

Alternatively, you can pass an image url directly to uploadsearch to
start the search.

.. code:: python

    image_url = 'http://mydomain.com/images/red_dress.jpg'
    response = api.uploadsearch(image_url=image_url)

5.3.1 Selection Box
^^^^^^^^^^^^^^^^^^^

If the object you wish to search for takes up only a small portion of
your image, or other irrelevant objects exists in the same image,
chances are the search result could become inaccurate. Use the Box
parameter to refine the search area of the image to improve accuracy.
Noted that the box coordinated is setted with respect to the original
size of the image passed, it will be automatically scaled to fit the
resized image for uploading:

.. code:: python

    image_url = 'http://mydomain.com/images/red_dress.jpg'
    box = (0,0,10,10)
    response = api.uploadsearch(image_url=image_url, box=box)

5.3.2 Resizing Settings
^^^^^^^^^^^^^^^^^^^^^^^

When performing upload search, you might experience increasing search
latency with increasing image file sizes. This is due to the increased
time transferring your images to the ViSearch server, and the increased
time for processing larger image files in ViSearch.

To reduce upload search latency, by default the ``uploadSearch`` method
makes a copy of your image file if both of the image dimensions exceed
512 pixels, and resizes the copy to dimensions not exceeding 512x512
pixels. This is the optimized size to lower search latency while not
sacrificing search accuracy for general use cases:

.. code:: python

    # client.uploadSearch(params) is equivalent to using STANDARD resize settings, 512x512 and jpeg 75 quality
    image_path = 'blue_dress.jpg'
    response = api.uploadsearch(image_path=image_path, resize='STANDARD')

If your image contains fine details such as textile patterns and
textures, use the HIGH resize settings to get better search results:

.. code:: python

    # for images with fine details, use HIGH resize settings 1024x1024 and jpeg 75 quality
    image_path = 'blue_dress.jpg'
    response = api.uploadsearch(image_path=image_path, resize='HIGH')

Or provide customized resize settings:

.. code:: python

    # using customized resize settings 800x800 and jpeg 80 quality
    image_path = 'blue_dress.jpg'
    response = api.uploadsearch(image_path=image_path, resize=(800, 800, 80))

6. Search Results
-----------------

ViSearch returns a maximum number of 1000 most relevant image search
results. You can provide pagination parameters to control the paging of
the image search results.

Pagination parameters:

+---------+-----------+----------------------------------------------------------------------------------------------------+
| Name    | Type      | Description                                                                                        |
+=========+===========+====================================================================================================+
| page    | Integer   | Optional parameter to specify the page of results. The first page of result is 1. Defaults to 1.   |
+---------+-----------+----------------------------------------------------------------------------------------------------+
| limit   | Integer   | Optional parameter to specify the result per page limit. Defaults to 10.                           |
+---------+-----------+----------------------------------------------------------------------------------------------------+

.. code:: python

    page = 1
    limit = 25
    response = api.uploadsearch(image_url=image_url, page=page, limit=limit)

7. Advanced Search Parameters
-----------------------------

7.1 Retrieving Metadata
~~~~~~~~~~~~~~~~~~~~~~~

To retrieve metadata of your image results, provide the list (or tuple)
of metadata keys for the metadata value to be returned in the ``fl``
(field list) property:

.. code:: python

    fl = ["price", "brand", "title", "im_url"]  #, or fl = ("price", "brand", "title", "im_url")
    response = api.uploadsearch(image_url=image_url, fl=fl)

    Only metadata of type string, int, and float can be retrieved from
    ViSearch. Metadata of type text is not available for retrieval.

7.2 Filtering Results
~~~~~~~~~~~~~~~~~~~~~

To filter search results based on metadata values, provide a dict of
metadata key to filter value in the ``fq`` (filter query) property:

.. code:: python

    fq = {"im_cate": "bags", "price": "10,199"}
    response = api.uploadsearch(image_url=image_url, fq=fq)

Querying syntax for each metadata type is listed in the following table:

=======    ======
Type        FQ
=======    ======
string      Metadata value must be exactly matched with the query value, e.g. "Vintage Wingtips" would not match "vintage wingtips" or "vintage"
text        Metadata value will be indexed using full-text-search engine and supports fuzzy text matching, e.g. "A pair of high quality leather wingtips" would match any word in the phrase
int         Metadata value can be either: (1) exactly matched with the query value; (2) matched with a ranged query minValue,maxValue, e.g. int value 1, 99, and 199 would match ranged query 0,199 but would not match ranged query 200,300
float       Metadata value can be either: (1) exactly matched with the query value; (2) matched with a ranged query minValue,maxValue, e.g. float value 1.0, 99.99, and 199.99 would match ranged query 0.0,199.99 but would not match ranged query 200.0,300.0
=======    ======


7.3 Result Score
~~~~~~~~~~~~~~~~

ViSearch image search results are ranked in descending order i.e. from
the highest scores to the lowest, ranging from 1.0 to 0.0. By default,
the score for each image result is not returned. You can turn on the
**boolean** ``score`` property to retrieve the scores for each image
result:

.. code:: python

    score = True
    response = api.uploadsearch(image_url=image_url, score=score)

If you need to restrict search results from a minimum score to a maximum
score, specify the ``score_min`` and/or ``score_max`` parameters:

+--------------+---------+--------------------------------------------------------+
| Name         | Type    | Description                                            |
+==============+=========+========================================================+
| score\_min   | Float   | Minimum score for the image results. Default is 0.0.   |
+--------------+---------+--------------------------------------------------------+
| score\_max   | Float   | Maximum score for the image results. Default is 1.0.   |
+--------------+---------+--------------------------------------------------------+

.. code:: python

    score_min = 0.5
    score_max = 0.8
    response = api.uploadsearch(image_url=image_url, score_max=score_max, score_min=score_min)

8. Declaration
--------------

-  The image upload.jpg included in the SDK is downloaded from
   http://pixabay.com/en/boots-shoes-pants-folded-fashion-690502/
