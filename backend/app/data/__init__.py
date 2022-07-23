from __future__ import annotations

from typing import Type, TypeVar, cast

import pickle

from pydantic import BaseModel


T = TypeVar("T")


class PermanentModel(BaseModel):
    _path: str = ""

    @classmethod
    def load(cls: Type[T]) -> T:
        with open(cast(PermanentModel, cls)._path, "rb") as fp:
            return pickle.load(fp)

    def save(self):
        with open(self._path, "wb") as fp:
            pickle.dump(self, fp)
