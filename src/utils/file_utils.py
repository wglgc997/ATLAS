def read_file(path):
    """ "Config the read mode"""
    with open(path, "r", encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]
