import os
def set_env_temporarily(vars_dict):
    """Context manager to set env vars for the duration of a block."""

    class _Ctx:
        def __enter__(self_nonlocal):
            self_nonlocal.old = {}
            for k, v in vars_dict.items():
                self_nonlocal.old[k] = os.environ.get(k)
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

        def __exit__(self_nonlocal, exc_type, exc, tb):
            for k, oldv in self_nonlocal.old.items():
                if oldv is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = oldv
    return _Ctx()


