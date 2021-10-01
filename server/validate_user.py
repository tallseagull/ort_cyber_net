from hashlib import sha1

def _validate_user(db, user_id, user_token):
    """
    Validate the user credentials. The path is "/{user_type}/{token}/{path}". We take the token (which has 2 elements
    separated by /) and validate it. The first element in the token is the ID of the user. The second is the secret generated
    in the login phase by self._get_user_secret
    :param user_id: The user_id in our DB
    :param user_token: The token for validation
    :return: True/False
    """
    user = db.get_user_by_id(user_id)
    if user:
        if user_token == _get_user_secret(user):
            return True
    return False


def _get_user_secret(user):
    """
    The user secret token. it is a cryptographic hash of the user_id in the our DB and the user name.
    :param user: A dict of the DB record. Should have 'id' and 'name' as keys.
    :return:
    """
    user_secret = sha1(f"{user['id']}/{user['name']}".encode("utf8")).hexdigest()
    return user_secret


def validate_user(db, user_id, user_token, admin_requested=False):
    """
    Validate the user. If the user is valid, returns a dict with 'valid': True. Otherwise 'valid': False and 'status':
    [the error code - 401 or 403].
    :param user_id: The user_id in our DB
    :param user_token: The token for validation
    :param admin_requested: if True, we also validate the user is an admin
    :return: A dict with 'valid', 'status', and if successful in validation also 'user' and 'base_path'
    """
    # Need to validate the user
    if not _validate_user(db, user_id, user_token):
        return {'valid': False,
                'status': 401}

    # The user ID is the second part of the path, and the user secret is the third:
    if admin_requested:
        user_or_admin = 'admin'
    else:
        user_or_admin = 'user'
    base_path = f"/{user_or_admin}/{user_id}/{user_token}"

    # Check that the user is an admin:
    user = db.get_user_by_id(user_id)
    if admin_requested and not user['is_admin']:
        return {'valid': False,
                'status': 403}

    return {'valid': True,
            'status': 200,
            'user': user,  # The User table object from the DB for this user
            'base_path': base_path}  # The base path for future requests - includes the user_id and secret token

