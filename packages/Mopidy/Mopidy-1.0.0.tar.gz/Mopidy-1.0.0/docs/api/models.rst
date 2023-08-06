***********
Data models
***********

These immutable data models are used for all data transfer within the Mopidy
backends and between the backends and the MPD frontend. All fields are optional
and immutable. In other words, they can only be set through the class
constructor during instance creation.

If you want to modify a model, use the
:meth:`~mopidy.models.ImmutableObject.copy` method. It accepts keyword
arguments for the parts of the model you want to change, and copies the rest of
the data from the model you call it on. Example::

    >>> from mopidy.models import Track
    >>> track1 = Track(name='Christmas Carol', length=171)
    >>> track1
    Track(artists=[], length=171, name='Christmas Carol')
    >>> track2 = track1.copy(length=37)
    >>> track2
    Track(artists=[], length=37, name='Christmas Carol')
    >>> track1
    Track(artists=[], length=171, name='Christmas Carol')


Data model relations
====================

.. digraph:: model_relations

    Ref -> Album [ style="dotted", weight=1 ]
    Ref -> Artist [ style="dotted", weight=1 ]
    Ref -> Directory [ style="dotted", weight=1 ]
    Ref -> Playlist [ style="dotted", weight=1 ]
    Ref -> Track [ style="dotted", weight=1 ]

    Playlist -> Track [ label="has 0..n", weight=2 ]
    Track -> Album [ label="has 0..1", weight=10 ]
    Track -> Artist [ label="has 0..n", weight=10 ]
    Album -> Artist [ label="has 0..n", weight=10 ]

    Image

    SearchResult -> Artist [ label="has 0..n", weight=1 ]
    SearchResult -> Album [ label="has 0..n", weight=1 ]
    SearchResult -> Track [ label="has 0..n", weight=1 ]

    TlTrack -> Track [ label="has 1", weight=20 ]


Data model API
==============

.. module:: mopidy.models
    :synopsis: Data model API

.. autoclass:: mopidy.models.Ref

.. autoclass:: mopidy.models.Track

.. autoclass:: mopidy.models.Album

.. autoclass:: mopidy.models.Artist

.. autoclass:: mopidy.models.Playlist

.. autoclass:: mopidy.models.Image

.. autoclass:: mopidy.models.TlTrack

.. autoclass:: mopidy.models.SearchResult


Data model helpers
==================

.. autoclass:: mopidy.models.ImmutableObject

.. autoclass:: mopidy.models.ModelJSONEncoder

.. autofunction:: mopidy.models.model_json_decoder
