from ckan import model


def get_context(user):
    return {
        'model': model,
        'user': user if isinstance(user, str) else user['name']
    }
