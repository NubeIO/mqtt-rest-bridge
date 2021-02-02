def read_file(file) -> str:
    try:
        with open(file, "r") as f:
            return f.read()
    except Exception:
        return ""


def write_file(file, content):
    f = open(file, "w")
    f.write(content)
    f.close()
