"""
Record.

Returning a asyncdb Record row Format.
"""
from .base import OutputFormat
from asyncdb.meta import Record


class recordFormat(OutputFormat):
    """
    Returns a List of Records from a Resultset
    """
    async def serialize(self, result, error, *args, **kwargs):
        self._result = None
        try:
            if isinstance(result, list):
                set = [Record.from_dict(row) for row in result]
            else:
                set = Record.from_dict(result)
            self._result = set
        except Exception as err:
            error = Exception(f"recordFormat: Error on Data: error: {err}")
        finally:
            return (self._result, error)
