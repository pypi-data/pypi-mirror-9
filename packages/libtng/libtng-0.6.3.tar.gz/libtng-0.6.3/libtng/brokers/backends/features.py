

class BaseBrokerFeatures(object):
    """Specifies the features supported by a distributed message broker."""

    #: Indicates if the backend supports the ``QUEUE`` publication method.
    has_queues = False

    #: Indicates if the backend supports the ``TOPIC`` publishing method.
    has_topics = False

    #: Indicates if transactions are supported (e.g. as with the STOMP
    #: protocol).
    has_transactions = False

    #: Indicates if the backend supports returning a message id on publishing.
    can_return_id = False
