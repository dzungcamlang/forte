# Copyright 2019 The Forte Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# pylint: disable=attribute-defined-outside-init
from typing import Dict, Any

from texar.torch.hyperparams import HParams

from forte.common.resources import Resources
from forte.processors.base import IndexProcessor
from forte.indexers import ElasticSearchIndexer
from forte import utils

__all__ = [
    "ElasticSearchIndexProcessor"
]


class ElasticSearchIndexProcessor(IndexProcessor):
    r"""This processor indexes the data packs into an Elasticsearch index."""

    # pylint: disable=useless-super-delegation
    def __init__(self) -> None:
        super().__init__()

    def initialize(self, resources: Resources, configs: HParams):
        super().initialize(resources, configs)
        cls = utils.get_class(self.config.indexer.name,
                                  module_paths=["forte.indexers"])
        self.indexer = cls(hparams=self.config.indexer.hparams)

    @staticmethod
    def default_hparams() -> Dict[str, Any]:
        r"""Returns a dictionary of default hyperparameters.

        .. code-block:: python

            {
                "batch_size": 128,
                "field": "content",
                "indexer": {
                    "name": "ElasticSearchIndexer",
                    "hparams": ElasticSearchIndexer.default_hparams(),
                    "kwargs": {
                        "request_timeout": 10,
                        "refresh": False
                    }
                }
            }

        Here:

        `"batch_size"`: int
            Number of examples that will be bulk added to Elasticsearch index

        `"field"`: str
            Field name that will be used as a key while indexing the document

        `"indexer"`: dict

            `"name"`: str
                Name of Indexer to be used.

            `"hparams"`: dict
                Hyperparameters to be used for the index. See
                :meth:`ElasticSearchIndexer.default_hparams` for more details

            `"kwargs"`: dict
                Keyword arguments that will be passed to
                :meth:`ElasticSearchIndexer.add_bulk` API

        """
        return {
            **IndexProcessor.default_hparams(),
            "field": "content",
            "indexer": {
                "name": "ElasticSearchIndexer",
                "hparams": ElasticSearchIndexer.default_hparams(),
                "other_kwargs": {
                    "request_timeout": 10,
                    "refresh": False
                }
            }
        }

    def _bulk_process(self):
        documents = [{self.config.field: document} for document in
                     self.documents]
        self.indexer.add_bulk(documents, **self.config.indexer.other_kwargs)
