import os
import shutil
from plumber import (
    plumbing,
    default,
    finalize,
)
from node.base import BaseNode
from node.behaviors import (
    Adopt,
    DefaultInit,
    Reference,
    Nodify,
    DictStorage,
)
from node.locking import (
    TreeLock,
    locktree,
)
from node.interfaces import IRoot
from zope.interface import (
    implementer,
    alsoProvides,
)
from zope.component.event import objectEventNotify
from node.ext.directory.interfaces import (
    IDirectory,
    IFile,
)
from node.ext.directory.events import FileAddedEvent


MODE_TEXT = 0
MODE_BINARY = 1


@implementer(IFile)
class FileStorage(DictStorage):
    fs_mode = default(None)

    def _get_mode(self):
        if not hasattr(self, '_mode'):
            self._mode = MODE_TEXT
        return self._mode

    def _set_mode(self, mode):
        self._mode = mode

    mode = default(property(_get_mode, _set_mode))

    def _get_data(self):
        if not hasattr(self, '_data'):
            if self.mode == MODE_BINARY:
                self._data = None
            else:
                self._data = ''
            if os.path.exists(os.path.sep.join(self.fs_path)):
                mode = self.mode == MODE_BINARY and 'rb' or 'r'
                with open(os.path.sep.join(self.fs_path), mode) as file:
                    self._data = file.read()
        return self._data

    def _set_data(self, data):
        setattr(self, '_changed', True)
        self._data = data

    data = default(property(_get_data, _set_data))

    def _get_lines(self):
        if self.mode == MODE_BINARY:
            raise RuntimeError(u"Cannot read lines from binary file.")
        if not self.data:
            return []
        return self.data.split('\n')

    def _set_lines(self, lines):
        if self.mode == MODE_BINARY:
            raise RuntimeError(u"Cannot write lines to binary file.")
        self.data = '\n'.join(lines)

    lines = default(property(_get_lines, _set_lines))

    @default
    @property
    def fs_path(self):
        # seems more appropriate here:
        #     return self.parent.fs_path + [self.name]
        return self.path

    @finalize
    @locktree
    def __call__(self):
        file_path = os.path.join(*self.fs_path)
        exists = os.path.exists(file_path)
        # Only write file if it's data has changed or not exists yet
        if hasattr(self, '_changed') or not exists:
            write_mode = self.mode == MODE_BINARY and 'wb' or 'w'
            with open(file_path, write_mode) as file:
                file.write(self.data)
        # Change file system mode if set
        if self.fs_mode is not None:
            os.chmod(file_path, self.fs_mode)


@plumbing(
    Adopt,
    DefaultInit,
    Reference,
    Nodify,
    FileStorage)
class File(object):
    pass


# global file factories
file_factories = dict()


@implementer(IDirectory)
class DirectoryStorage(DictStorage):
    fs_encoding = default('utf-8')
    fs_mode = default(None)
    backup = default(True)
    ignores = default(list())
    default_file_factory = default(File)

    # XXX: rename later to file_factories, keep now as is for b/c reasons
    factories = default(dict())

    @default
    @property
    def file_factories(self):
        # temporary, see above
        return self.factories

    @default
    @property
    def child_directory_factory(self):
        return Directory

    @default
    @property
    def fs_path(self):
        return self.path

    @finalize
    def __init__(self, name=None, parent=None, backup=False, factories=dict()):
        self.__name__ = name
        self.__parent__ = parent
        self.backup = backup
        # override file factories if given
        if factories:
            self.factories = factories
        self._deleted = list()

    @finalize
    @locktree
    def __call__(self):
        if IDirectory.providedBy(self):
            dir_path = os.path.join(*self.fs_path)
            try:
                os.mkdir(dir_path)
            except OSError, e:
                # Ignore ``already exists``.
                if e.errno != 17:
                    raise e
            # Change file system mode if set
            if self.fs_mode is not None:
                os.chmod(dir_path, self.fs_mode)
        for name in self._deleted:
            abspath = os.path.join(*self.fs_path + [name])
            if os.path.exists(abspath):
                if os.path.isdir(abspath):
                    shutil.rmtree(abspath)
                else:
                    os.remove(abspath)
                    bakpath = os.path.join(*self.fs_path + ['.%s.bak' % name])
                    if os.path.exists(bakpath):
                        os.remove(bakpath)
                continue
        for name, target in self.items():
            if IDirectory.providedBy(target):
                target()
            elif IFile.providedBy(target):
                target()
                # Use fs_path if provided by child, otherwise fallback to path
                # XXX: deprecate the fallback use of path
                if hasattr(target, 'fs_path'):
                    fs_path = target.fs_path
                else:
                    fs_path = target.path
                abspath = os.path.join(*fs_path)
                if self.backup and os.path.exists(abspath):
                    bakpath = os.path.join(
                        *target.fs_path[:-1] + ['.%s.bak' % target.name])
                    shutil.copyfile(abspath, bakpath)

    @finalize
    def __setitem__(self, name, value):
        if not name:
            raise KeyError('Empty key not allowed in directories')
        name = self._encode_name(name)
        if IFile.providedBy(value) or IDirectory.providedBy(value):
            if IDirectory.providedBy(value):
                value.backup = self.backup
            self.storage[name] = value
            objectEventNotify(FileAddedEvent(value))
            return
        raise ValueError('Unknown child node.')

    @finalize
    def __getitem__(self, name):
        name = self._encode_name(name)
        if name in self.storage:
            return self.storage[name]
        with TreeLock(self):
            filepath = os.path.join(*self.fs_path + [name])
            if os.path.exists(filepath):
                if os.path.isdir(filepath):
                    self[name] = self.child_directory_factory()
                else:
                    factory = self._factory_for_ending(name)
                    if factory:
                        try:
                            self[name] = factory()
                        except TypeError:
                            # happens if the factory cannot be called without 
                            # args (e.g. .pt)
                            # in this case we treat it as a flat file
                            # XXX: remove try/except and fallback, for
                            #      described case child factories are supposed
                            #      to be used
                            self[name] = File()
                    else:
                        # default
                        self[name] = self.default_file_factory()
        return self.storage[name]

    @finalize
    def __delitem__(self, name):
        name = self._encode_name(name)
        if os.path.exists(os.path.join(*self.fs_path + [name])):
            self._deleted.append(name)
        del self.storage[name]

    @finalize
    def __iter__(self):
        try:
            existing = set(os.listdir(os.path.join(*self.fs_path)))
        except OSError:
            existing = set()
        for key in self.storage:
            existing.add(key)
        for key in existing:
            if self.backup and key.endswith('.bak'):
                continue
            if key in self._deleted:
                continue
            if key in self.ignores:
                continue
            yield key

    @default
    def _encode_name(self, name):
        if isinstance(name, unicode):
            name = name.encode(self.fs_encoding)
        return name

    @default
    def _factory_for_ending(self, name):
        def match(keys, key):
            keys = sorted(keys)
            keys = sorted(keys,
                          cmp=lambda x, y: len(x) > len(y) and 1 or -1,
                          reverse=True)
            for possible in keys:
                if key.endswith(possible):
                    return possible
        factory_keys = [
            match(self.file_factories.keys(), name),
            match(file_factories.keys(), name),
        ]
        if factory_keys[0]:
            if factory_keys[1] and len(factory_keys[1]) > len(factory_keys[0]):
                return file_factories[factory_keys[1]]
            return self.file_factories[factory_keys[0]]
        if factory_keys[1]:
            return file_factories[factory_keys[1]]


@plumbing(
    Adopt,
    Reference,
    Nodify,
    DirectoryStorage)
class Directory(object):
    """Object mapping a file system directory.
    """
