from threading import Lock


class SingletonMeta(type):
    """
    Thread-safe Singleton metaclass with per-class lock.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        # create a lock for this class if it doesn't exist
        if not hasattr(cls, "_lock"):
            cls._lock = Lock()

        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
