from fastapi import Request


def get_raw_path(request: Request):
    path = f'{request.url.path}?{request.query_params}'
    return path
