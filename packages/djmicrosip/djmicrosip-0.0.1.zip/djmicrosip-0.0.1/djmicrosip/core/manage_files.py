import compileall, os, shutil, errno

def compile_and_copy(src, dest, *patterns):
    ''' Para compilar archivos y copiarlos al repositorio de compilado. '''

    base_name = os.path.dirname(dest)
    dest_dir = os.path.abspath(dest)
    compileall.compile_dir(src, force=True)

    if os.path.isdir(base_name):
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        try:
            shutil.copytree(src, dest_dir, ignore=shutil.ignore_patterns(*patterns))
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                shutil.copy(src, dest_dir)
            else:
                print('Directory not copied. Error: %s' % e)