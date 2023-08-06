def icon(launchable, src):
    return (launchable['links']['icon'],
            '',
            'image/png',
            open(src, 'rb'))


def launchable(launchable, src):
    return (launchable['links']['content'],
            '',
            'application/vnd.appear.webapp',
            zip_launchable(src))


def zip_launchable(src):
    import os
    import zipfile
    import io
    in_memory_zip = io.BytesIO()
    zf = zipfile.ZipFile(in_memory_zip, 'a', zipfile.ZIP_DEFLATED, False)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            filepath = os.path.join(dirname, filename)
            archname = os.path.relpath(filepath, src)
            print('adding %s' % archname)
            zf.write(filepath, archname)
    zf.close()
    return in_memory_zip.getvalue()
