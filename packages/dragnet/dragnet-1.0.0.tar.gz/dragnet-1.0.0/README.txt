
Dragnet
=======

Dragnet isn’t interested in the shiny chrome or boilerplate dressing of
a web page. It’s interested in… ‘just the facts.’ The machine learning
models in Dragnet extract the main article content and optionally user
generated comments from a web page. They provide state of the art
performance on variety of test benchmarks.

For more information on our approach check out:

-  The `Dragnet homepage`_
-  Our paper `Content Extraction Using Diverse Feature Sets`_, published
   at WWW in 2013, gives an overview of the machine learning approach.
-  `A comparison`_ of Dragnet and alternate content extraction packages.
-  `This blog post`_ explains the intuition behind the algorithms.

GETTING STARTED
===============

Depending on your use case, we provide two separate models to extract
just the main article content or the content and any user generated
comments. Each model implements the ``analyze`` method that takes an
HTML string and returns the content string.

.. code:: python

    import requests
    from dragnet import content_extractor, content_comments_extractor

    # fetch HTML
    url = 'https://moz.com/devblog/dragnet-content-extraction-from-diverse-feature-sets/'
    r = requests.get(url)

    # get main article without comments
    content = content_extractor.analyze(r.content)

    # get article and comments
    content_comments = content_comments_extractor.analyze(r.content)

.. _Dragnet homepage: https://github.com/seomoz/dragnet
.. _Content Extraction Using Diverse Feature Sets: https://github.com/seomoz/dragnet/blob/master/dragnet_www2013.pdf?raw=true
.. _A comparison: https://moz.com/devblog/benchmarking-python-content-extraction-algorithms-dragnet-readability-goose-and-eatiht/
.. _This blog post: https://moz.com/devblog/dragnet-content-extraction-from-diverse-feature-sets/
