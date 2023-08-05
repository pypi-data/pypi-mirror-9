"""
Celery Backend for MongoDB that does not convert task results into a binary
format before storing them in Mongo database.
"""

__copyright__ = "Copyright 2014 Regents of the University of Michigan"
__author__ = "Zakir Durumeric"
__license__ = "Apache License, Version 2.0"
__email__ = "zakird@gmail.com"

from celery.backends.mongodb import MongoBackend, Binary

__all__ = ['MongoNonBinaryBackend']


class MongoNonBinaryBackend(MongoBackend):

    EXTRACTED_FIELDS = [
        "name",
        "series",
        "hostname",
        "start",
        "end",
        "warnings",
        "schedule"
    ]

    def _store_result(self, task_id, result, status,
                      traceback, log, metadata, name,
                      request=None, **kwargs):
        """Store return value and status of an executed task."""
        meta = {'task_id': task_id,
                'status': status,
                'result': result,
                'log': log,
                'metadata': metadata,
                'traceback': Binary(self.encode(traceback)),
                'children': Binary(self.encode(
                    self.current_task_children(request),
                ))}
        for field in self.EXTRACTED_FIELDS:
            if field in metadata:
                meta[field] = metadata[field]
                continue
            if "__%s" % field in metadata:
                meta[field] = metadata["__%s" % field]
        self.collection.save(meta)
        return result


    def store_result(self, task_id, result, status,
                         traceback=None, request=None, **kwargs):
        """Update task state and result."""
        # custom handling of data we embed in metadata
        if result:
            if "log" in result:
                log = result["log"]
                del result["log"]
            elif hasattr(result, "log"):
                log = getattr(result, "log")
                delattr(result, "log")
            else:
                 log = []
            if "metadata" in result:
                metadata = result["metadata"]
                del result["metadata"]
            elif hasattr(result, "metadata"):
                metadata = getattr(result, "metadata")
                delattr(result, "metadata")
            else:
                metadata = {}
        else:
            log = []
            metadata = {}

        if "pretty_name" in metadata:
            name = metadata["pretty_name"]
            del metadata["pretty_name"]
        else:
            name = "unknown"

        result = self.encode_result(result, status)
        self._store_result(task_id, result, status, traceback,
                           log, metadata, name,
                           request=request, **kwargs)
        return result

