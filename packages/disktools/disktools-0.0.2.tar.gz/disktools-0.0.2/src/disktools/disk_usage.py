from __future__ import unicode_literals, print_function
import sys
import os
import bson
import stat
import shutil

# Fix utf-8 bugs.
reload(sys)
sys.setdefaultencoding('utf-8')


HIDDEN = u'.duc'  # stands for 'disk usage cache'


def _get_size(path):
    '''Recursively get size of the path. No caching, so this is rather slow.'''
    total_size = os.path.getsize(path)
    for item in os.listdir(path):
        itempath = os.path.join(path, item)
        if os.path.isfile(itempath):
            total_size += os.path.getsize(itempath)
        elif os.path.isdir(itempath):
            total_size += _get_size(itempath)
    return total_size


def get_cache_path(folder_path):
    return os.path.join(folder_path, HIDDEN, 'du.cache')


def get_cache_mtime(folder_path):
    cache_path = get_cache_path(folder_path)
    return os.path.getmtime(cache_path)


def load_cache(folder_path):
    # Start with empty cache.
    cache = {'folder_sizes': dict()}
    cache_path = get_cache_path(folder_path)
    # Check if any previous values have been kept.
    if not os.path.exists(cache_path):
        return cache
    cache['folder_sizes'] = bson.loads(open(cache_path).read())
    cache['last_modified'] = os.path.getmtime(cache_path)
    return cache


def save_cache(folder_path, folder_sizes):
    '''
    Cache is written into .duc folder. The size of the folder is filled
    using a file called blob. The size of the file pads folder disk size
    in bytes to be dividable by a dev block size. This allows for `duc` to
    report the same size as `du`.

    Returns the size of the created/updated cache folder.
    '''
    cache_path = get_cache_path(folder_path)
    cache_dir_path = os.path.dirname(cache_path)
    if not os.path.exists(cache_dir_path):
        os.makedirs(cache_dir_path)
    with open(cache_path, 'w+') as output:
        output.write(bson.dumps(folder_sizes))
    # Return size of the cache.
    return _get_size(cache_dir_path)


def purge_cache(path):
    cache_folder_path = os.path.join(path, HIDDEN)
    if os.path.exists(cache_folder_path):
        shutil.rmtree(cache_folder_path)


def purge_rec_cache(path):
    sub_folders = [folder for folder in os.listdir(path)
                   if os.path.isdir(os.path.join(path, folder))
                   and folder != HIDDEN]
    for sub_folder in sub_folders:
        sub_path = os.path.join(path, sub_folder)
        purge_rec_cache(sub_path)
    purge_cache(path)


def get_size(path, cached=True, seen_hardlinks=None):
    assert os.path.isdir(path)
    size = os.path.getsize(path)
    if seen_hardlinks is None:
        seen_hardlinks = list()
    entries = [unicode(entry_name) for entry_name in os.listdir(path)]
    folder_sizes = dict()
    cache = load_cache(path)
    for entry_name in entries:
        entry_path = os.path.join(path, entry_name)
        attributes = os.stat(entry_path)
        # Sum if os.path.isdir(size of linked files only once.
        if attributes.st_nlink > 0:
            if attributes.st_ino not in seen_hardlinks:
                seen_hardlinks.append(attributes.st_ino)
            else:
                continue
        # Sum size on entries.
        if stat.S_ISDIR(attributes.st_mode):
            if entry_name == HIDDEN:
                # We add cache size separately.
                continue
            # Deep first get_size recursion for folders.
            if cached \
                    and (entry_name not in cache['folder_sizes']
                         or attributes.st_ctime > cache['last_modified']):
                # Learn size recursively.
                folder_size = get_size(entry_path,
                                       seen_hardlinks=seen_hardlinks)
            else:
                folder_size = cache['folder_sizes'][entry_name]
            # Never cache the cache.
            if entry_name != HIDDEN:
                folder_sizes[entry_name] = folder_size
            size += folder_size
            # print('Adding folder size: %d (%s)' % (size, entry_path))
        else:
            # Simply sum the file size.
            size += attributes.st_size
            # print('Adding file size: %d (%s)' % (size, entry_path))
    # Cache learned result on disk.
    # purge_cache(path)
    if not path.endswith(HIDDEN) and len(folder_sizes) > 0:
        # Don't cache the cache of the cache.
        # Don't forget the size of just produced cache folder, otherwise
        # reported results deviate from the `du -sb` output.
        size += save_cache(path, folder_sizes)
        # print('Adding cache size: %d' % size)
    return size
