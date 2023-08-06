import flask.signals


_signals = flask.signals.Namespace()
signal = _signals.signal


def listens_to(name, sender=None):
    """Listens to a named signal
    """
    def decorator(f):
        if sender:
            return signal(name).connect(f, sender=sender)
        return signal(name).connect(f)
    return decorator
