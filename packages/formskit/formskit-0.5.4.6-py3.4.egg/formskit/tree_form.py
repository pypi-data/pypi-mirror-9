from base64 import urlsafe_b64decode
from copy import deepcopy
from json import loads
import binascii

from .field import TreeField
from .form import Form, WrongValueName


class TreeForm(Form):

    def _init_before_create(self):
        super()._init_before_create()
        self.parent = None
        self.childs = {}

    def add_field(self, *args, **kwargs):
        field = TreeField(*args, **kwargs)
        self.add_field_object(field)
        return field

    def reset(self):
        super().reset()
        for name in self.childs:
            self.childs[name] = {0: self.childs[name][0]}
            self.childs[name][0].reset()

    def _get_parents(self):
        if self.parent is None:
            return [self._get_form_info()]
        else:
            parents = self.parent._get_parents()
            parents.append(self._get_form_info())
            return parents

    def _get_form_info(self):
        return {
            'name': self.get_name(),
            'index': self.index}

    def add_sub_form(self, form):
        form._set_parent(self, 0)
        self.childs[form.get_name()] = {0: form}

    def _set_parent(self, parent, index):
        self.parent = parent
        self.index = index

    def get_or_create_sub_form(self, name, index):
        try:
            return self.get_sub_form(name, index)
        except KeyError:
            form = self._clone_sub_form(name)
            self.childs[name][index] = form
            form.index = index
            return form

    def get_sub_form(self, name, index):
        return self.childs[name][index]

    def _clone_sub_form(self, name):
        form = self.childs[name][0]
        form = deepcopy(form)
        form.reset()
        return form

    def _validate_sub_forms(self):
        success = True
        for sub_forms in self.childs.values():
            for sub_form in sub_forms.values():
                success &= sub_form._validate()
        return success

    def _parse_sub_form(self, name, data):
        for index, values in enumerate(data):
            sub_form = self.get_or_create_sub_form(name, index)
            sub_form.parse_dict(values)

    def _validate(self):
        # Why this method was implemented in this way?
        # Goal was to run validation on fields and if it succeeded, then form
        # can run form validators.
        # But sub_forms should always run validation.
        super()._validate()
        self.success &= self._validate_sub_forms()
        return self.success

    def _get_field(self, name):
        data = self._decode_name(name)
        name = data['name']

        form = self._get_sub_form(data['parents'][1:])
        return form.fields[name]

    def get_data_dict(self, minified=False):
        tree = super().get_data_dict(minified=minified)
        for name, sub_forms in self.childs.items():
            tree[name] = {}
            for index, sub_form in sub_forms.items():
                tree[name][index] = sub_form.get_data_dict(minified)
        return tree

    def _decode_name(self, name):
        try:
            json = urlsafe_b64decode(name).decode('utf8')
            return loads(json)
        except (binascii.Error, UnicodeDecodeError):
            raise WrongValueName(name)

    def _get_sub_form(self, parents):
        if parents == []:
            return self
        form_name = parents[0]['name']
        index = parents[0]['index']
        sub_form = self.get_or_create_sub_form(form_name, index)
        return sub_form._get_sub_form(parents[1:])

    def get_report(self):
        reports = super().get_report()
        reports['childs'] = {}
        for name, forms in self.childs.items():
            reports['childs'][name] = {}
            for index, form in forms.items():
                reports['childs'][name][index] = form.get_report()
        return reports
