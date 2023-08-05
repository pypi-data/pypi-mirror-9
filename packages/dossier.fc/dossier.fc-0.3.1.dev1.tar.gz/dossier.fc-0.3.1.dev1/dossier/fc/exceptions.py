''':mod:`dossier.fc` exceptions.

.. This software is released under an MIT/X11 open source license.
   Copyright 2012-2014 Diffeo, Inc.

.. autoclass:: ReadOnlyException
.. autoclass:: SerializationError

'''

class BaseException(Exception):
    '''Base exception for all things in dossier.fc
    '''
    pass


class ReadOnlyException(BaseException):
    '''Code attempted to modify a read-only feature collection.

    This occurs when adding, deleting, or making other in-place
    modifications to a :class:`~dossier.fc.FeatureCollection` that has
    its :attr:`~dossier.fc.FeatureCollection.read_only` flag set.  It
    also occurs when attempting to make changes to a
    :class:`~dossier.fc.StringCounter` contained in such a collection.

    '''
    pass


class SerializationError(BaseException):
    '''A problem occurred serializing or deserializing.

    This can occur if a :class:`~dossier.fc.FeatureCollection` has an
    unrecognized feature type, or if a CBOR input does not have the
    correct format.

    '''
    pass
