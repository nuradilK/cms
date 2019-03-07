import functools
from .models import Contest


def contest_participation_required(func):
    @functools.wraps(func)
    def wrapper_contest_participation_required(*args, **kwargs):
        for key, val in kwargs.items():
            print(str(key) + '=' + str(val))
        return func(*args, **kwargs)

    return wrapper_contest_participation_required
