import string
import mimetypes
import random


def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'


def generate_random_init_pwd(length=6, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(length))


def generate_random_num_code(length=6):
    result = ""
    for i in range(length):
        ch = chr(random.randrange(ord('0'), ord('9') + 1))
        result += ch
    return result


def encode_multipart_formdata(arguments, files):
    """
    arguments is a dict of {name: value} elements for regular form arguments.
    files is a sequence of (name, filename, value) elements for data to be
    uploaded as files.
    Return (content_type, body) ready for httplib.HTTP instance
    """
    boundary = b'----------ThIs_Is_tHe_bouNdaRY_$'
    crlf = b'\r\n'
    l = []
    if arguments is not None:
        for (key, value) in arguments.items():
            l.append(b'--' + boundary)
            l.append(b'Content-Disposition: form-data; name="%s"' % key.encode())
            l.append(b'')
            l.append(value.encode())
    if files is not None:
        for (key, filename, value) in files:
            l.append(b'--' + boundary)
            l.append(
                b'Content-Disposition: form-data; name="%s"; filename="%s"' % (key.encode(), filename.encode())
            )
            l.append(b'Content-Type: %s' % get_content_type(filename).encode())
            l.append(b'')
            l.append(value)
    l.append(b'--' + boundary + b'--')
    l.append(b'')
    body = crlf.join(l)
    content_type = b'multipart/form-data; boundary=%s' % boundary
    return content_type, body
