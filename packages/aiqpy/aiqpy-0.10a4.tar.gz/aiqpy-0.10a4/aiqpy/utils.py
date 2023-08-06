"""
aiqpy.utils
-----------

This module provides utility functions that can be used together with aiqpy
to provide short hands for cumbersome calls.

"""

import collections
import mimetypes


class MultipartMessage(collections.Mapping):
    def __init__(self):
        self.__wrapped_dict = collections.OrderedDict()

    def items(self):
        return self.__wrapped_dict.items()

    def __iter__(self):
        return self.__wrapped_dict.__iter__()

    def __getitem__(self, item):
        return self.__wrapped_dict.__getitem__(item)

    def __len__(self):
        return len(self.__wrapped_dict)

    def __contains__(self, item):
        return self.__wrapped_dict.__contains__(item)

    def add_part(self, name, payload,
                 content_type=None,
                 content_transfer_encoding=None):
        import six
        if isinstance(payload, dict):
                import json
                payload = json.dumps(payload)
                if not content_type:
                    content_type = 'application/json'

        if not content_transfer_encoding:
            if isinstance(payload, six.string_types):
                content_transfer_encoding = '8bit'
            else:
                content_transfer_encoding = 'binary'

        if not content_type and hasattr(payload, 'name'):
            (content_type, _) = mimetypes.guess_type(payload.name)

        self.__wrapped_dict[name] = ('', payload, content_type,
                                     {'Content-Transfer-Encoding':
                                      content_transfer_encoding})


def icon(metadata, icon_path):
    """Prepare a request to upload a icon."""
    return (metadata['links']['icon'],
            open(icon_path, 'rb'))


def launchable(metadata, launchable_path):
    """Prepare a request to upload a launchable."""
    return (metadata['links']['content'],
            __zip_launchable(launchable_path),
            'application/vnd.appear.webapp')


def __zip_launchable(source_path):
    """Take a folder and compress as zip in memory"""
    import os
    import zipfile
    import io
    in_memory_zip = io.BytesIO()
    zf = zipfile.ZipFile(in_memory_zip, 'a', zipfile.ZIP_DEFLATED, False)
    for dir_name, _, files in os.walk(source_path):
        for filename in files:
            file_path = os.path.join(dir_name, filename)
            arch_name = os.path.relpath(file_path, source_path)
            zf.write(file_path, arch_name)
    zf.close()
    return in_memory_zip.getvalue()
