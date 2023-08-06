from .utils import get_user_id, get_session, BASE_URL, validate_result
from classification_data import ClassificationData
from classification_model import ClassificationModel

# contains various user operations

def list_datasets():
    """
    Returns identifiers to the users datasets
    """
    user_id = get_user_id()

    # url = BASE_URL + "/api/users/" + str(user_id) + "/datasets"
    url = BASE_URL + "/api/v1.1/users/" + str(user_id) + "/datasets"
    response = get_session().get(url)
    result = validate_result(response)
    datasets =  [ClassificationData(id=d["id"], verbose=False) for d in result["datasets"]]
    return datasets

def list_classifiers():
    """
    Returns identifiers to the users datasets
    """
    user_id = get_user_id()

    url = BASE_URL + "/api/v1.1/users/" + str(user_id) + "/classifiers"
    response = get_session().get(url)
    result = validate_result(response)
    models = [ClassificationModel(id=m["id"]) for m in result["trained_models"]]
    return models

def delete_dataset(dataset):
    """
    Deletes the dataset with the given dataset id
    """
    url = BASE_URL + "/api/datasets/%d"%(dataset.id)
    response = get_session().delete(url)
    if len(response.text) > 0:
        result = validate_result(response)

    dataset.clear_values()

def delete_classifier(classifier):
    """
    Deletes the model with given model id
    """
    url = BASE_URL + "/api/classifiers/%d"%(classifier.id)
    response = get_session().delete(url)
    if len(response.text) > 0:
        result = validate_result(response)

    classifier.clear_values()
