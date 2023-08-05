

from .utils import set_api_key, get_api_key, get_user_id, match_predictions_with_labels, get_input_from_path

from .classification_data import ClassificationData

from .classification_model import ClassificationModel

from .user import list_datasets, list_classifiers, delete_dataset, delete_classifier

general_image_classifier = ClassificationModel(id="GeneralImageClassifier")
food_image_classifier = ClassificationModel(id="FoodImageClassifier")
twitter_text_classifier = ClassificationModel(id="TwitterTextClassifier")


# TODO: get version from setup.py, or other non-duplicative method
# see https://packaging.python.org/en/latest/single_source_version.html#single-sourcing-the-version
__all__ = ['ClassificationData','ClassificationModel', 
           'set_api_key', 'get_api_key', 'get_user_id', 'match_predictions_with_labels', 'get_input_from_path',
           'list_datasets', 'list_classifiers', 'delete_dataset', 'delete_classifier']
