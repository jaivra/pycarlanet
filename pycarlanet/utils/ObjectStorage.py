from typing import Any, Dict
import itertools

class ObjectStorage:
    _instance = None
    _queue: Dict[str, Any] = dict()
    
    _id_iter = itertools.count(1000)


    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ObjectStorage, cls).__new__(cls)
        return cls._instance

    @classmethod
    def put(cls, item: Any) -> str:
        key = str(next(cls._id_iter))
        cls._queue[key] = item
        return key

    @classmethod
    def get_and_remove(cls, key: str) -> Any:
        if key in cls._queue:
            item = cls._queue[key]
            del cls._queue[key]  # Delete the item after getting it
            return item
        else:
            raise IndexError(f"cannot find any element in ObjectStorage with key: {key}")
    
    @classmethod
    def get(cls, key: str) -> Any:
        if key in cls._queue:
            item = cls._queue[key]
            return item
        else:
            raise IndexError(f"cannot find any element in ObjectStorage with key: {key}")