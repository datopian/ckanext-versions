from ckan.plugins import toolkit


def dataset_version_create(context, data_dict):
    pass


@toolkit.side_effect_free
def dataset_version_list(context, data_dict):
    pass


def dataset_version_current(context, data_dict):
    pass


def dataset_history(context, data_dict):
    # not sure if we need this
    pass


def activity_dataset_show(context, data_dict):
    pass


def get_activity_id_from_dataset_version_name(context, data_dict):
    pass


def dataset_has_versions(context, data_dict):
    pass
