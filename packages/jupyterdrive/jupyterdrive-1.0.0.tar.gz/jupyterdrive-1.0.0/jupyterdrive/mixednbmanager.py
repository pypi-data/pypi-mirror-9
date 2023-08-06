"""A contents manager that combine multiple content managers."""

# Copyright (c) IPython Development Team.
# Distributed under the terms of the Modified BSD License.

from IPython.html.services.contents.manager import ContentsManager
from IPython.utils.traitlets import List
from IPython.utils.importstring import import_item

class MixedContentsManager(ContentsManager):

    filesystem_scheme = List([
            {
                'root':'local',
                'contents':"IPython.html.services.contents.filemanager.FileContentsManager"
            },
            {
                'root': 'gdrive',
                'contents': 'jupyterdrive.clientsidenbmanager.ClientSideContentsManager'
            }
        ],
    help="""
    List of virtual mount point name and corresponding contents manager
    """, config=True)

    def __init__(self, **kwargs):

        super(MixedContentsManager, self).__init__(**kwargs)
        self.managers = {}

        ## check consistency of scheme.
        if not len(set(map(lambda x:x['root'], self.filesystem_scheme))) == len(self.filesystem_scheme):
            raise ValueError('Scheme should not mount two contents manager on the same mountpoint')

        kwargs.update({'parent':self})
        for scheme in self.filesystem_scheme:
            manager_class = import_item(scheme['contents'])
            self.managers[scheme['root']] = manager_class(**kwargs)


    def path_dispatch1(method):
        def _wrapper_method(self, path, *args, **kwargs):
            path = path.strip('/')
            _path = path.split('/')
            sentinel = _path.pop(0)
            man = self.managers.get(sentinel, None)
            if man is not None:
                meth = getattr(man, method.__name__)
                sub = meth('/'.join(_path), *args, **kwargs)
                return sub
            else :
                return method(self, path, *args, **kwargs)
        return _wrapper_method

    def path_dispatch2(method):
        def _wrapper_method(self, other, path, *args, **kwargs):
            path = path.strip('/')
            _path = path.split('/')
            sentinel = _path.pop(0)
            man = self.managers.get(sentinel, None)
            if man is not None:
                meth = getattr(man, method.__name__)
                sub = meth(other, '/'.join(_path), *args, **kwargs)
                return sub
            else :
                return method(self, other, path, *args, **kwargs)
        return _wrapper_method

    def path_dispatch_kwarg(method):
        def _wrapper_method(self, path=''):
            path = path.strip('/')
            _path = path.split('/')
            sentinel = _path.pop(0)
            man = self.managers.get(sentinel, None)
            if man is not None:
                meth = getattr(man, method.__name__)
                sub = meth(path='/'.join(_path))
                return sub
            else :
                return method(self, path=path)
        return _wrapper_method

    # ContentsManager API part 1: methods that must be
    # implemented in subclasses.

    @path_dispatch1
    def dir_exists(self, path):
        ## root exists
        if len(path) == 0:
            return True
        if path in self.managers.keys():
            return True
        return False

    @path_dispatch1
    def is_hidden(self, path):
        if (len(path) == 0) or path in self.managers.keys():
            return False;
        raise NotImplementedError('....'+path)

    @path_dispatch_kwarg
    def file_exists(self, path=''):
        if len(path) == 0:
            return False
        raise NotImplementedError('NotImplementedError')

    @path_dispatch1
    def exists(self, path):
        if len(path) == 0:
            return True
        raise NotImplementedError('NotImplementedError')

    @path_dispatch1
    def get(self, path, **kwargs):
        if len(path) == 0:
            return [ {'type':'directory'}]
        raise NotImplementedError('NotImplementedError')

    @path_dispatch2
    def save(self, model, path):
        raise NotImplementedError('NotImplementedError')

    @path_dispatch2
    def update(self, model, path):
        raise NotImplementedError('NotImplementedError')

    @path_dispatch1
    def delete(self, path):
        raise NotImplementedError('NotImplementedError')

    @path_dispatch1
    def create_checkpoint(self, path):
        raise NotImplementedError('NotImplementedError')

    @path_dispatch1
    def list_checkpoints(self, path):
        raise NotImplementedError('NotImplementedError')

    @path_dispatch2
    def restore_checkpoint(self, checkpoint_id, path):
        raise NotImplementedError('NotImplementedError')

    @path_dispatch2
    def delete_checkpoint(self, checkpoint_id, path):
        raise NotImplementedError('NotImplementedError')

    # ContentsManager API part 2: methods that have useable default
    # implementations, but can be overridden in subclasses.

    # TODO (route optional methods too)
