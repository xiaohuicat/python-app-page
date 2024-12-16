def replace_illegal_chars(path):
    illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_chars:
        path = path.replace(char, '_')
    return path