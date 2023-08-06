'''Utility code for webdiff'''
from collections import defaultdict
import copy
import functools
import hashlib
import mimetypes
import os
import re
import subprocess
import tempfile
import time

from PIL import Image

import github_fetcher


class ImageMagickNotAvailableError(Exception):
    pass


class ImageMagickError(Exception):
    pass


textchars = ''.join(map(chr, [7,8,9,10,12,13,27] + range(0x20, 0x100)))
is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))


# via https://wiki.python.org/moin/PythonDecoratorLibrary#Memoize
def memoize(obj):
    """Decorator to memoize a function."""
    cache = obj.cache = {}

    @functools.wraps(obj)
    def memoizer(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key not in cache:
            cache[key] = obj(*args, **kwargs)
        return cache[key]
    return memoizer


def is_binary_file(filename):
  return is_binary_string(open(filename, 'rb').read(1024))


def find_diff(a, b):
    '''Walk directories a and b and pair off files.'''
    a_files = []
    b_files = []
    def accum(arg, dirname, fnames):
        for fname in fnames:
            path = os.path.join(dirname, fname)
            if not os.path.isdir(path):
                arg.append(path)

    assert os.path.isdir(a)
    assert os.path.isdir(b)

    os.path.walk(a, accum, a_files)
    os.path.walk(b, accum, b_files)

    a_files = [os.path.relpath(x, start=a) for x in a_files]
    b_files = [os.path.relpath(x, start=b) for x in b_files]

    pairs = _convert_to_pair_objects(pair_files(a_files, b_files))
    diff = annotate_file_pairs(pairs, a, b)

    # this sorts "changes" before "delete" in a move, which is much easier to understand.
    diff.sort(key=lambda x: (x['path'], 0 if x['b'] else 1))
    for i, d in enumerate(diff):
        d['idx'] = i
    return diff


def pair_files(a_files, b_files):
    pairs = []
    for f in a_files[:]:
        if f in b_files:
            i = a_files.index(f)
            j = b_files.index(f)
            pairs.append((f, f))
            del a_files[i]
            del b_files[j]
        else:
            pairs.append((f, None))  # delete

    for f in b_files:
        pairs.append((None, f))  # add

    return pairs


def _convert_to_pair_objects(pairs):
    '''Convert (a, b) pairs to {a, b, path, type} filePair objects.'''
    diffs = []
    for i, (a, b) in enumerate(pairs):
        d = { 'a': a, 'b': b, 'path': b or a, 'type': 'change' }
        if a is None:
            d['type'] = 'add'
        elif b is None:
            d['type'] = 'delete'
        diffs.append(d)
    return diffs


def _annotate_file_pair(d, a_dir, b_dir):
    a_path = os.path.join(a_dir, d['a']) if d['a'] else None
    b_path = os.path.join(b_dir, d['b']) if d['b'] else None
    d['a_path'] = a_path
    d['b_path'] = b_path

    # Attach image metadata if applicable.
    if is_image_diff(d):
        d['is_image_diff'] = True
        if d['a']: d['image_a'] = _image_metadata(a_path)
        if d['b']: d['image_b'] = _image_metadata(b_path)
        if d['a'] and d['b']:
            try:
                d['are_same_pixels'], _ = generate_pdiff_image(a_path, b_path)
            except ImageMagickError:
                d['are_same_pixels'] = False
            except ImageMagickNotAvailableError:
                pass

    if a_path and b_path:
        d['no_changes'] = _are_files_identical(a_path, b_path)
    else:
        d['no_changes'] = False


def annotate_file_pairs(file_pairs, a_dir, b_dir):
    '''Add annotations (e.g. stats, image info, moves) to filePair objects.'''
    file_pairs = find_moves(file_pairs, a_dir, b_dir)

    for d in file_pairs:
        _annotate_file_pair(d, a_dir, b_dir)

    return file_pairs


def find_moves(diff, a_dir, b_dir):
    def hash(d, path):
        return _contentHash(os.path.join(d, path))

    out = copy.deepcopy(diff)
    add_delete_pairs = defaultdict(lambda: [None,None])

    for idx, pair in enumerate(diff):
        if pair['type'] == 'add':
            add_delete_pairs[hash(b_dir, pair['b'])][1] = idx
        elif pair['type'] == 'delete':
            add_delete_pairs[hash(a_dir, pair['a'])][0] = idx

    for _, (aIdx, bIdx) in add_delete_pairs.iteritems():
        if aIdx == None or bIdx == None:
            continue

        a = diff[aIdx]
        b = diff[bIdx]

        # replace the "add" with a "change"
        out[bIdx] = {
            'a': a['a'],
            'b': b['b'],
            'path': a['a'],  # ???
            'type': 'move'
        }

    return out


def is_image_diff(diff):
    def is_image(path):
        if path is None: return False
        mime_type, enc = mimetypes.guess_type(path)
        return (mime_type and mime_type.startswith('image/') and enc is None)

    left_img = is_image(diff['a'])
    right_img = is_image(diff['b'])

    if left_img and right_img:
        return True
    elif left_img and diff['b'] is None:
        return True
    elif right_img and diff['a'] is None:
        return True
    return False


hash_cache = {}
def _contentHash(path):
    global hash_cache
    if path in hash_cache:
        return hash_cache[path]
    sha = hashlib.sha512(open(path).read()).digest()
    hash_cache[path] = sha
    return sha


def _are_files_identical(path1, path2):
    # Check if anything has changed.
    # Compare lengths & then checksums.
    if os.path.getsize(path1) != os.path.getsize(path2):
        return False
    return _contentHash(path1) == _contentHash(path2) 


def _image_metadata(path):
    md = { 'num_bytes': os.path.getsize(path) }
    try:
        im = Image.open(path)
        width, height = im.size
        md.update({'width': width, 'height': height})
    except:
        pass
    return md


def _shim_for_file_diff(a_file, b_file):
    '''Sets A_DIR, B_DIR and DIFF to do a one-file diff.'''
    a_dir = os.path.dirname(a_file)
    a_file = os.path.basename(a_file)
    b_dir = os.path.dirname(b_file)
    b_file = os.path.basename(b_file)
    diff = annotate_file_pairs([{
             'a': a_file,
             'b': b_file,
             'idx': 0,
             'path': a_file,
             'type': 'change'}],  # 'change' is the only likely case.
             a_dir, b_dir)
    return a_dir, b_dir, diff


def diff_for_args(args):
    """Returns A_DIR, B_DIR, find_diff() for parsed command line args.
    
    DIFF looks something like:
    [ {
        'a': '1_normal.jpg',
        'is_image_diff': True,
        'b': '1_normal.jpg',
        'idx': 0,
        'no_changes': False,
        'image_a': {'width': 300, 'num_bytes': 20831, 'height': 300},
        'image_b': {'width': 300, 'num_bytes': 20713, 'height': 300},
        'path': '1_normal.jpg',
        'type': 'change'
      }, ... ]
    """
    if 'dirs' in args:
        return list(args['dirs']) + [find_diff(*args['dirs'])]

    if 'files' in args:
        return _shim_for_file_diff(*args['files'])

    if 'github' in args:
        gh = args['github']
        a_dir, b_dir = github_fetcher.fetch_pull_request(gh['owner'], gh['repo'], gh['num'])
        return [a_dir, b_dir] + [find_diff(a_dir, b_dir)]


@memoize
def is_imagemagick_available():
    try:
        # this swallows stdout/stderr
        subprocess.check_output(['identify', '--version'])
    except (subprocess.CalledProcessError, OSError):
        return False
    return True


@memoize
def generate_pdiff_image(before_path, after_path):
    '''Generate a perceptual diff between the before/after images.

    This runs the ImageMagick compare command.

    Returns: (are_images_identical, path_to_pdiff_png)
    '''
    if not is_imagemagick_available():
        raise ImageMagickNotAvailableError()

    _, diff_path = tempfile.mkstemp(suffix='.png')

    # The compare command returns:
    #   0 on success & similar images
    #   1 on success & dissimilar images
    #   2 on failure
    PIPE = subprocess.PIPE
    p = subprocess.Popen([
            'compare',
            '-metric', 'RMSE',
            '-highlight-color', 'Red',
            '-compose', 'Src',
            before_path, after_path, diff_path
        ], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    output, err = p.communicate()  # `compare` is noisy; this swallows its output
    result = p.returncode

    if result == 2:
        raise ImageMagickError('compare failed. Perhaps image dimensions differ.')
    if result == 0:
        return True, diff_path
    return False, diff_path


@memoize
def generate_dilated_pdiff_image(diff_path):
    '''Given a pdiff image, dilate it to highlight small differences.'''
    if not is_imagemagick_available():
        raise ImageMagickNotAvailableError()

    # Dilate the diff image (to highlight small differences) and make it red.
    _, diff_dilate_path = tempfile.mkstemp(suffix='.png')
    subprocess.check_call([
        'convert',
        diff_path,
        '-monochrome',
        '-negate',
        '-morphology', 'Dilate', 'Disk:5.5',
        '-negate',
        '-fill', 'Red', '-opaque', 'Black',
        diff_dilate_path
    ])
    return diff_dilate_path


@memoize
def get_pdiff_bbox(diff_path):
    '''Returns {top,left,width,height} for the content of a pdiff.'''
    if not is_imagemagick_available():
        raise ImageMagickNotAvailableError()

    out = subprocess.check_output(['identify', '-format', '%@', diff_path])
    # This looks like "26x94+0+830"
    m = re.match(r'^(\d+)x(\d+)\+(\d+)\+(\d+)', out)
    if not m:
        raise ImageMagickError('Unexpected identify output: %s' % out)
    width, height, left, top = [int(x) for x in m.groups()]
    return {
        'width': width,
        'height': height,
        'left': left,
        'top': top,
        'bottom': top + height,
        'right': left + width
    }
