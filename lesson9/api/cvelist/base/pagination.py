
def convert_pages_to_limits(page: int, page_size: int):
    limit = page_size
    offset = (page - 1) * page_size
    return limit, offset
