def read_file(file) -> str:
    with open(file, "r") as f:
        return f.read()


def write_file(file, content):
    f = open(file, "w")
    f.write(content)
    f.close()
