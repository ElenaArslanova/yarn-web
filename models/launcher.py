from functools import partial

from models.base import MajorityRowModel, Model
from models.metrics import general_metric, jacard_with_word_influence
from models.processing import remove_stop_words_tokens


def create_majority_row_model() -> Model:
    metric = partial(general_metric, sim_metric=jacard_with_word_influence, processing=remove_stop_words_tokens)
    return MajorityRowModel(0.4, metric)
