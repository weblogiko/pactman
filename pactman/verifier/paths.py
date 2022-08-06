def format_path(path):
    s = path[0]
    for elem in path[1:]:
        s += f"[{elem}]" if isinstance(elem, int) else f".{elem}"
    return s
