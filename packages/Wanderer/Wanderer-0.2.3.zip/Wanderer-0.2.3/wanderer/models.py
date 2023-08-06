'''
models
======

Models for working with a wanderer project.
'''

import os
from .filepath import FilePath


class BaseModel(object):
    '''Basic model class to manage an aspect of a project.'''

    typ = 'base'

    def __init__(self, app, path, parent=None):

        if not isinstance(path, FilePath):
            path = FilePath(path).expand()

        self.app = app
        self.path = path
        self.name = path.name
        self.parent = parent

    @classmethod
    def new(cls, app, path, parent=None, template=None):
        model = cls(app=app, path=path, parent=None)

        template = app.get_template_dir(template or cls.typ)
        if model.path.exists:
            raise NameError('{0} already exists...'.format(model.name))
        else:
            template.copy(model.path)

        return model


class Project(BaseModel):
    '''Project Model'''

    typ = 'project'

    @classmethod
    def new(cls, *args, **kwargs):
        raise NotImplemented('Use Wanderer().bootstrap to create projects')


class Asset(BaseModel):
    '''Asset Model'''

    typ='asset'

    def __init__(self, app, path, parent=None):
        super(Asset, self).__init__(app, path, parent)
        self.cat = self.path.parent.name
        self.component_names = []
        for k, v in self.app.config.components.iteritems():
            if 'asset' in v['parent_types']:
                self.component_names.append(k)

    def new_component(self, name, template=None):
        '''Create a new component for this asset.'''

        if not name in self.component_names:
            err = '{0} is not a valid asset component...use these: {1}'
            raise TypeError(err.format(name, self.component_names))

        return Component.new(
            app=self.app,
            path=self.path.join(name),
            parent=self,
            template=template)

    def find_component(self, name='*'):
        '''Find asset components of a specific name.'''

        if not name in self.component_names + ['*']:
            err = '{0} is not a valid asset component...use these: {1}'
            raise TypeError(err.format(name, self.component_names))

        for c in self.path.glob(name):
            if c.name in self.component_names:
                yield Component(app=self.app, path=c, parent=self)


class Sequence(BaseModel):
    '''Sequence Model'''

    typ = 'sequence'

    def new_shot(self, name, template=None):
        '''Create a new shot in the sequence'''

        return Shot.new(app=self.app, path=self.path.join(name),
                        parent=self, template=template)

    def find_shot(self, name='*'):
        '''Find a shot in the sequence'''

        for s in self.path.glob(name):
            yield Shot(app=self.app, path=s, parent=self)

    @classmethod
    def new(cls, app, path, parent=None, template=None):
        model = cls(app=app, path=path, parent=None)

        template = app.get_template_dir(template or cls.typ)
        if model.path.exists:
            raise NameError('{0} already exists...'.format(model.name))
        else:
            os.makedirs(model.path)

        return model

class Shot(BaseModel):
    '''Shot Model'''

    typ = 'shot'

    def __init__(self, app, path, parent=None):
        super(Shot, self).__init__(app, path, parent)
        self.component_names = []
        for k, v in self.app.config.components.iteritems():
            if 'shot' in v['parent_types']:
                self.component_names.append(k)

    def new_component(self, name, template=None):
        '''Create a new component for this shot.'''

        if not name in self.component_names + ['*']:
            err = '{0} is not a valid shot component...use these: {1}'
            raise TypeError(err.format(name, self.component_names))

        return Component.new(
            app=self.app,
            path=self.path.join(name),
            parent=self,
            template=template)

    def find_component(self, name='*'):
        '''Find shot components

        :param name: Name of component to find (default: *)'''

        if not name in self.component_names + ['*']:
            err = '{0} is not a valid shot component...use these: {1}'
            raise TypeError(err.format(name, self.component_names))

        for c in self.path.glob(name):
            if c.name in self.component_names:
                yield Component(app=self.app, path=c, parent=self)


class Component(BaseModel):

    typ = 'component'

    def __init__(self, app, path, parent=None):
        super(Component, self).__init__(app, path, parent)
        self.short = self.app.config.components[self.name]['short']

    def archive(self):

        apath = FilePath('$WA_PROJECT/archive/{0}/{1}').expand()
        if parent.typ == 'asset':
            apath = apath.format(self.parent.cat, self.parent.name)
        else:
            apath = apath.format(self.parent.parent.name, self.parent.name)

        c.move(apath)

    @classmethod
    def new(cls, app, path, parent=None, template=None):

        c = cls(app=app, path=path, parent=None)

        template = app.get_template_dir(template or c.name)
        if c.path.exists:
            raise NameError('{0} already exists...'.format(c.name))
        else:
            template.copy(c.path)

        return c
