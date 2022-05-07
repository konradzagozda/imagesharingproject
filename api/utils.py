import magic


def get_mime(filepath):
    mime = magic.Magic(mime=True)
    return mime.from_file(filepath)


def get_mime_memory_file(file):
    initial_pos = file.tell()
    file.seek(0)
    mime_type = magic.from_buffer(file.read(1024), mime=True)
    file.seek(initial_pos)
    return mime_type