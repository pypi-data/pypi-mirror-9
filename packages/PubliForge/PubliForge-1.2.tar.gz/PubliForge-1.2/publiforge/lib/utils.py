# $Id: utils.py 7981fd623a54 2015/02/21 08:15:22 Patrick $
# -*- coding: utf-8 -*-
"""Some various utilities."""

from sys import version_info
from os import sep, listdir, makedirs
from os.path import exists, join, isdir, dirname, basename, getmtime
from shutil import copy2
import re
import zipfile
import mimetypes
from datetime import datetime
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
from cStringIO import StringIO
from beaker.crypto.util import sha1
from lxml import etree
from subprocess import Popen, PIPE, STDOUT
from docutils.core import publish_parts
from unicodedata import normalize, combining
from textwrap import fill
from webhelpers2.html import literal

from pyramid.i18n import TranslationStringFactory, make_localizer


_ = TranslationStringFactory('publiforge')
EXCLUDED_FILES = ('.hg', '.svn', '.git', 'Thumbs.db', '.DS_Store')
MIME_TYPES = (
    'css', 'csv', 'epub+zip', 'folder', 'font-woff', 'gif', 'html',
    'indesign-iddd', 'indesign-idml', 'javascript', 'jpeg', 'mp4', 'mpeg',
    'msword', 'ogg', 'pdf', 'plain', 'png', 'postscript', 'relaxng', 'svg+xml',
    'tiff', 'vnd.ms-excel', 'vnd.ms-opentype',
    'vnd.oasis.opendocument.spreadsheet', 'vnd.oasis.opendocument.text',
    'x-msdos-program', 'x-msvideo', 'x-python', 'x-shockwave-flash', 'x-tar',
    'x-wav', 'xml', 'xml-dtd', 'zip')


# =============================================================================
def localizer(locale_name, directories=None):
    """Create a :class:`pyramid.i18n.Localizer` object corresponding to the
    provided locale name from the translations found in the list of translation
    directories.

    :param locale_name: (string)
        Current language.
    :param directories: (list, optional)
        Translation directories.
    :return: (:class:`pyramid.i18n.Localizer` instance)
    """
    return make_localizer(
        locale_name, directories or [join(dirname(__file__), '..', 'Locale')])


# =============================================================================
def has_permission(request, *perms):
    """Check if the user has at least one of the specified permissions.

    :param request: (:class:`pyramid.request.Request` instance)
        Current request.
    :param perms: (list)
        List of permission groups.
    :return: (boolean)

    See :ref:`frontreference_permissions`.
    """
    if 'perms' not in request.session:
        return False
    if 'admin' in request.session['perms']:
        return True
    for perm in perms:
        if perm in request.session['perms'] or \
                '%s_manager' % perm[0:3] in request.session['perms'] or \
                ('%s_editor' % perm[0:3] in request.session['perms'] and
                 perm[4:] == 'user'):
            return True
    return False


# =============================================================================
def config_get(config, section, option, default=None):
    """Retrieve a value from a configuration object.

    :param config: (:class:`ConfigParser.ConfigParser` instance)
        Configuration object.
    :param section: (string)
        Section name.
    :param option: (string)
        Option name.
    :param default: (string, optional)
        Default value
    :return: (string)
        Read value or default value.
    """
    if not config.has_option(section, option):
        return default
    value = config.get(section, option)
    return (isinstance(value, str) and value.decode('utf8')) or value


# =============================================================================
def config_get_list(config, section, option, default=None):
    """Retrieve a list of values from a configuration object.

    :param config: (:class:`ConfigParser.ConfigParser` instance)
        Configuration object.
    :param section: (string)
        Section name.
    :param option: (string)
        Option name.
    :param default: (list, optional)
        Default values.
    :return: (list)
    """
    if not config.has_option(section, option):
        return default or []
    values = config_get(config, section, option)
    return values and [k.strip() for k in values.split(',')] or []


# =============================================================================
def settings_get_list(settings, option, default=None):
    """Retrieve a list of values from a settings object.

    :param settings: (:class:`pyramid.registry.Registry.settings` instance)
        Configuration object.
    :param option: (string)
        Option name.
    :param default: (list, optional)
        Default values.
    :return: (list)
    """
    if option not in settings:
        return default or []
    return [k.strip() for k in settings.get(option, '').split(',')]


# =============================================================================
def copy_content(src_dir, dst_dir, exclude=(), force=False):
    """Copy the content of a ``src_dir`` directory into a ``dst_dir``
    directory.

    :param src_dir: (string)
        Source directory path.
    :param dst_dir: (string)
        Destination directory path.
    :param exclude: (list, optional)
        List of files to exclude.
    :param force: (booelan, optional)
        Force copy even if the target file has the same date.
    """
    if not exists(dst_dir):
        makedirs(dst_dir)
    for name in listdir(src_dir):
        if name in exclude or name in EXCLUDED_FILES:
            continue
        source = join(src_dir, name)
        if not isinstance(source, unicode):
            source = source.decode('utf8')
            name = name.decode('utf8')
        target = join(dst_dir, name)
        if isdir(source):
            if listdir(source):
                copy_content(source, target, exclude, force)
        elif force or not exists(target) \
                or getmtime(target) != getmtime(source):
            copy2(source, target)


# =============================================================================
def camel_case(text):
    """Convert ``text`` in Camel Case."""
    if version_info[:3] >= (2, 7, 0):
        # pylint: disable = locally-disabled, E1123
        return re.sub(
            r'(^\w|[-_ 0-9]+\w)',
            lambda m: m.group(0).replace('_', '').replace(' ', '').upper(),
            text, flags=re.UNICODE)
    else:
        return re.sub(
            r'(^\w|[-_ 0-9]+\w)',
            lambda m: m.group(0).replace('_', '').replace(' ', '').upper(),
            text)


# =============================================================================
def normalize_name(name):
    """Normalize name."""
    return re.sub('_+', '_', re.sub(r'[  *?!,;:"\'/]', '_', name))\
        .lower().encode('utf8')


# =============================================================================
def normalize_spaces(text, truncate=None):
    """Normalize spaces and, eventually, truncate result.

    :param text: (string)
        Text to normalize.
    :param truncate: (integer, optional)
        If not ``None``, maximum lenght of the returned string.
    :return: (string or ``None``)
    """
    if text is None:
        return None
    text = u' '.join(text.strip().replace(u' ', ':~:').split())\
           .replace(':~:', u' ')
    return truncate and text[0:truncate] or text


# =============================================================================
def make_id(name, mode=None, truncate=None):
    """Make an ID with name.

    :param name: (string)
        Name to use.
    :param mode: ('standard', 'token' or 'class', optional)
        Strategy to make ID.
    :param truncate: (integer, optional)
        If not ``None``, maximum lenght of the returned string.
    :return: (string)
    """
    token = name.strip()
    if mode != 'class':
        token = token.lower()
    if mode in ('standard', 'token', 'class'):
        token = re.sub('_+', '_', re.sub(u'[  *?!.,;:"\'/«»()–]', '_', token))
    if mode in ('token', 'class'):
        token = normalize('NFKD', unicode(token))
        token = u''.join([k for k in token if not combining(k)])
    return truncate and token[0:truncate] or token


# =============================================================================
def hash_sha(value, key):
    """Cryptographic hash function with SHA1 algorithm.

    :param value: (string)
        String to hash.
    :param key: (string)
        Encryption key.
    """
    return sha1('%s%s' % (value.encode('utf8'), key)).hexdigest()


# =============================================================================
def wrap(text, width=70, indent=0):
    """Transform a reStructuredText into XHTML.

    :param text: (string)
        Text to wrap.
    :param width: (integer, default 70)
        The maximum length of wrapped lines.
    :param indent: (integer, default 0)
        Initial and subsequent indentation.
    :return: (string)
        Wrapped text.
    """
    text = text.strip().replace(u' ', ':~:')
    if indent:
        text = fill(
            text, initial_indent='\n' + ' ' * indent,
            subsequent_indent=' ' * indent) + '\n' + ' ' * (indent - 2)
    else:
        text = fill(text, width=width)
    return text.replace(':~:', u' ')


# =============================================================================
def encrypt(value, key):
    """Encryption function.

    :param value: (string)
        String to encrypt.
    :param key: (string)
        Encryption key.
    :return: (string)
        Encrypted value or ``None``.
    """
    if value:
        cipher = AES.new((str(key) * 16)[:32])
        value = value.encode('utf8')
        return b64encode(cipher.encrypt(value + ' ' * (16 - len(value) % 16)))


# =============================================================================
def decrypt(value, key):
    """Decryption function.

    :param value: (string)
        String to decrypt.
    :param key: (string)
        Encryption key.
    :return: (string)
        Clear value or ``None``.
    """
    if value:
        cipher = AES.new((str(key) * 16)[:32])
        return cipher.decrypt(b64decode(str(value))).strip()


# =============================================================================
def zipize(data_list, are_files):
    """Return a ZIP archive containing all data of ``data_list``.

    :param data_list: (list)
        A list of tuples such as ``(<filename_in_zip>, <string_or_filename>)``.
    :param are_files: (boolean)
        ``True`` if strings represent file name.
    :return: (ZIP)
    """
    output = StringIO()
    zip_file = zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED)
    for data in data_list:
        if not are_files:
            zip_file.writestr(data[0], data[1])
    zip_file.close()
    zip_file = output.getvalue()
    output.close()

    return zip_file


# =============================================================================
def unzip(archive, outpath):
    """Extract an archive ignoring forbidden files.

    :param archive: (string or file)
        Name of the ZIP file.
    :param outpath: (string)
        Full path where extract the archive.
    """
    try:
        zip_file = zipfile.ZipFile(archive, 'r')
    except zipfile.BadZipfile:
        return
    for zipinfo in zip_file.infolist():
        if not [k for k in EXCLUDED_FILES
                if '%s%s' % (sep, k) in zipinfo.filename]:
            zip_file.extract(zipinfo, outpath.encode('utf8'))
    zip_file.close()


# =============================================================================
def get_mime_type(filename):
    """Return the mime type of ``filename``.

    :param filename: (string)
        File name.
    :return: (tuple)
        A tuple such as ``(mime_type, subtype)``. For instance:
        ``('text/plain', 'plain')``.
    """
    if isdir(filename):
        return 'folder', 'folder'
    mimetype = mimetypes.guess_type(filename, False)[0]
    if mimetype is None:
        return 'unknown', 'unknown'
    subtype = mimetype.partition('/')[2]
    return mimetype, subtype or mimetype


# =============================================================================
def size_label(size, is_dir):
    """Return a size in o, Kio, Mio or Gio.

    :param size: (integer)
        Size in figures.
    :param is_dir: (boolean)
        ``True`` if it is about a directory.
    :return: (string or :class:`pyramid.i18n.TranslationString`)
    """
    # For a directory
    if is_dir:
        return _('${n} items', {'n': size}) if size > 1 else \
            _('${n} item', {'n': size})

    # For a file
    if size >= 1073741824:
        return '%.1f Gio' % round(size / 1073741824.0, 1)
    elif size >= 1048576:
        return '%.1f Mio' % round(size / 1048576.0, 1)
    elif size >= 1024:
        return '%.1f Kio' % round(size / 1024.0, 1)
    return '%d o' % size


# =============================================================================
def age(mtime):
    """Return an age in minutes, hours, days or date.

    :param mtime: (datetime)
        Modification time.
    :return: (:class:`pyramid.i18n.TranslationString` or string)
        Return an age or a date if ``mtime`` is older than a year.
    """
    # pylint: disable = locally-disabled, R0911
    if not mtime:
        return ''
    delta = datetime.now() - mtime
    if delta.days == 0 and delta.seconds < 60:
        return _('1 second') if delta.seconds <= 1 \
            else _('${s} seconds', {'s': delta.seconds})
    elif delta.days == 0 and delta.seconds < 3600:
        minutes = delta.seconds / 60
        return _('1 minute') if minutes == 1 \
            else _('${m} minutes', {'m': minutes})
    elif delta.days == 0:
        hours = delta.seconds / 3600
        return _('1 hour') if hours == 1 \
            else _('${h} hours', {'h': hours})
    elif delta.days < 7:
        return _('1 day') if delta.days == 1 \
            else _('${d} days', {'d': delta.days})
    elif delta.days < 30:
        weeks = delta.days / 7
        return _('1 week') if weeks == 1 \
            else _('${w} weeks', {'w': weeks})
    elif delta.days < 365:
        months = delta.days / 30
        return _('1 month') if months == 1 else \
            _('${m} months', {'m': months})
    return str(mtime.replace(microsecond=0))[0:-9]


# =============================================================================
def cache_key(cache, method_name, *args):
    """Compute a cache key.

    :param cache: (:class:`beaker.cache.Cache` instance)
    :param method_name: (string)
    :param args: (positional arguments)
    :return: (string)
    """
    # pylint: disable = locally-disabled, W0141
    try:
        key = ','.join(map(str, args))
    except UnicodeEncodeError:
        key = ','.join(map(unicode, args))
    key = '%s(%s)' % (method_name, key)
    if len(key) + len(cache.namespace_name) > 250:
        key = sha1(key).hexdigest()
    return key


# =============================================================================
def cache_decorator():
    """Decorator to cache a method of a class with ``self.cache`` attribute.

    ``self.cache`` is a :class:`beaker.cache.Cache` instance.

    The method being decorated must only be called with positional arguments,
    and the arguments must support being stringified with ``str()``.
    """
    def _wrapper(create_method):
        """Wrapper function."""

        def _cached(self, *args):
            """Cache function."""
            if not hasattr(self, 'cache'):
                raise Exception('Class must have a "cache" attribute!')
            key = cache_key(self.cache, create_method.__name__, *args)

            def _createfunc():
                """Creation function."""
                # pylint: disable = locally-disabled, W0142
                return create_method(self, *args)

            return self.cache.get_value(key, createfunc=_createfunc)

        return _cached

    return _wrapper


# =============================================================================
def export_file_set(root_elt, record, file_type):
    """Save set of files in a XML object.

    :param root_elt: (:class:`lxml.etree.Element` instance)
        Element that linked the result.
    :param record: (:class:`~.models.processings.Processing`
        or :class:`~.models.packs.Pack` instance).
    :param file_type: ('file', 'resource' or 'template')
        File type.
     """
    items = [k for k in record.files if k.file_type == file_type]
    if len(items) == 0:
        return
    group_elt = etree.SubElement(root_elt, '%ss' % file_type)
    for item in sorted(items, key=lambda k: k.sort):
        elt = etree.SubElement(group_elt, file_type)
        if hasattr(item, 'target') and item.target:
            elt.set('to', item.target)
        if hasattr(item, 'visible') \
                and not (file_type == 'file' and item.visible) \
                and not (file_type != 'file' and not item.visible):
            elt.set('visible', item.visible and 'true' or 'false')
        elt.text = item.path


# =============================================================================
def swap_files(direction, index, record, files, form):
    """Swap two files in the list of files of a record (pack or processing).

    :param direction: ('mup' or 'dwn')
        Direction of the move.
    :param index: (string)
        Item to move in ``files``.
    :param record: (:class:`~.models.processings.Processing` or
        :class:`~.models.packs.Pack` instance)
        Current pack object.
    :param files: (dictionary)
        See :func:`~.lib.viewutils.file_details` function.
    :param form: (:class:`~.lib.form.Form` instance)
        Current form
    """
    file_type, index = index.partition('_')[0::2]
    index = int(index)

    # Something to do?
    direction = direction == 'dwn' and 1 or -1
    if (direction == -1 and index == 0) \
       or (direction == 1 and index + 1 == len(files[file_type])):
        return

    # Swap in database
    item1 = '%s/%s' % files[file_type][index][1:3]
    item1 = [k for k in record.files
             if k.file_type == file_type and k.path == item1][0]
    item2 = '%s/%s' % files[file_type][index + direction][1:3]
    item2 = [k for k in record.files
             if k.file_type == file_type and k.path == item2][0]
    item1.sort, item2.sort = item2.sort, item1.sort

    # Swap in dictionary
    files[file_type][index], files[file_type][index + direction] = \
        files[file_type][index + direction], files[file_type][index]

    # Modify form
    if form is not None and hasattr(item1, 'visible'):
        form.values['%s_%d_see' % (file_type, index)] = item2.visible
        form.values['%s_%d_see' % (file_type, index + direction)] = \
            item1.visible
        form.static('%s_%d_see' % (file_type, index))
        form.static('%s_%d_see' % (file_type, index + direction))


# =============================================================================
def execute(command, cwd=None, no_exit_code=False):
    """Run the command described by command. Wait for command to complete.
    If the return code is not zero, return output and an error message.

    :param command: (list)
        Splitted command to execute.
    :param cwd: (string, optional)
        If it is not ``None``, the current directory will be changed to ``cwd``
        before it is executed.
    :param no_exit_code: (boolean, default=False)
        If the command is known to exit with code 0 even if there is an error,
        assign this argument to ``True``.
    :return: (tuple)
        An error message such as ``(output, error)`` where ``output`` is a
        string and ``error`` a :class:`pyramid.i18n.TranslationString`.
    """
    try:
        process = Popen(command, cwd=cwd, stderr=STDOUT, stdout=PIPE)
    except OSError as error:
        return '', _('"${c}" failed: ${e}', {'c': command, 'e': error})
    if command[0] == 'nice':
        command = command[1:]
    command = basename(command[0])
    try:
        output = process.communicate()[0]
        if process.poll() or (no_exit_code and output):
            try:
                return output[0:102400].decode('utf8').strip(), \
                    _('"${c}" failed', {'c': command})
            except UnicodeDecodeError:
                return output[0:102400].decode('latin1').strip(), \
                    _('"${c}" failed', {'c': command})
    except OSError as error:
        return '', _('"${c}" failed: ${e}', {'c': command, 'e': error})
    output = output[0:102400]
    try:
        output = output.decode('utf8')
    except UnicodeDecodeError:
        pass
    return output.strip(), ''


# =============================================================================
def rst2xhtml(rst):
    """Transform a reStructuredText into XHTML.

    :param rst: (string)
        reStructuredText.
    :return: (string)
        XHTML.
    """
    return rst and literal(publish_parts(
        rst, writer_name='html')['body'].replace('blockquote', 'div')) or None


# =============================================================================
def load_regex(filename):
    """Load a list of regular expressions.

    :param filename: (string)
        Name of file to load.
    :return: (list)
        A list of :class:`re.pattern` objects.
    """
    regex = []
    for line in open(filename, 'r'):
        if line and not line[0] == '#' and not line[0:7] == '[Regex]':
            pattern, replace = line.partition(' =')[::2]
            pattern = pattern.strip().decode('utf8')
            if not pattern:
                continue
            if pattern[0] in '\'"' and pattern[-1] in '\'"':
                pattern = pattern[1:-1]
            replace = replace.strip().decode('utf8')
            if replace and replace[0] in '\'"' and replace[-1] in '\'"':
                replace = replace[1:-1]
            # pylint: disable = locally-disabled, eval-used
            if replace.startswith('lambda'):
                replace = eval(replace)
            regex.append((re.compile(
                pattern, re.MULTILINE | re.UNICODE), replace))

    return regex
