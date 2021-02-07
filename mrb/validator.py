from mrb.message import Response


def is_valid(response: Response):
    return response.status in range(200, 300) and not response.error
