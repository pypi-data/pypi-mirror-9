# Author: Christian Brodbeck <christianbrodbeck@nyu.edu>

from collections import defaultdict
from glob import glob
import inspect
from itertools import chain, product
import os
import re
import shutil
import subprocess
from warnings import warn

import numpy as np

from .. import fmtxt
from .._utils import LazyProperty, ui
from .._utils.com import send_email, Notifier


def _etree_expand(node, state):
    for tk, tv in node.iteritems():
        if tk == '.':
            continue

        for k, v in state.iteritems():
            name = '{%s}' % tk
            if str(v).startswith(name):
                tv[k] = {'.': v.replace(name, '')}
        if len(tv) > 1:
            _etree_expand(tv, state)


def _etree_node_repr(node, name, indent=0):
    head = ' ' * indent
    out = [(name, head + node['.'])]
    for k, v in node.iteritems():
        if k == '.':
            continue

        out.extend(_etree_node_repr(v, k, indent=indent + 3))
    return out


class LayeredDict(dict):
    """Dictionary which can store and restore states
    """
    def __init__(self):
        self._states = []
        dict.__init__(self)

    def __repr__(self):
        rep = ("<LayeredDict with %i stored states:\n"
               "%r>" % (len(self._states), dict.__repr__(self)))
        return rep

    def _get_state(self, index):
        "Retrieve a state (raise an appropriate error if not present)."
        if index >= len(self._states) or index < -len(self._states):
            err = ("Dict has only %i stored states, requested "
                   "%i" % (len(self._states), index))
            raise IndexError(err)
        return self._states[index]

    def get_stored(self, key, level, *args):
        """Retrieve a field value from any level

        Parameters
        ----------
        key : str
            the field name (dictionary key).
        level : int
            The level from which to retrieve the value. -1 = the current level.
        """
        state = self._get_state(level)
        return state.get(key, *args)

    def restore_state(self, index=-1, discard_tip=True):
        """Restore a previously stored state

        Parameters
        ----------
        index : int
            Index of the state which to restore (specified as index into a
            list of stored states, i.e., negative values access recently
            stored states).
        discard_tip : bool
            Discard the relevant state after restoring it. All states stored
            later are discarded either way.

        See Also
        --------
        .get_stored(): Retrieve a stored value without losing stored states
        """
        state = self._get_state(index)
        if discard_tip:
            del self._states[index:]
        elif index != -1:
            del self._states[index + 1:]

        self.clear()
        self.update(state)

    def store_state(self):
        "Store the current state"
        self._states.append(self.copy())


class _TempStateController(object):
    def __init__(self, experiment):
        self.experiment = experiment

    def __enter__(self):
        self.experiment.store_state()

    def __exit__(self, exc_type, exc_value, traceback):
        self.experiment.restore_state()


class TreeModel(object):
    """
    A hierarchical collection of format strings and field values

    Notes
    -----
    Any subclass should make sure to call the ``.store_state()` method at the
    end of initialization.
    """
    owner = None  # email address as string (for notification)
    _auto_debug = False  # in notification block

    _fmt_pattern = re.compile('\{([\w-]+)\}')

    # a dictionary of static templates (i.e., templates that do not have any hooks)
    _templates = {}
    _defaults = {}
    defaults = {}

    exclude = {}  # field_values to exclude (e.g. subjects)

    _repr_args = ()
    _repr_kwargs = ()

    def __init__(self, **state):
        self.exclude = self.exclude.copy()

        # scaffold for state
        self._fields = LayeredDict()
        self._field_values = LayeredDict()
        self._params = LayeredDict()

        # scaffold for hooks
        self._compound_members = {}
        self._compounds = defaultdict(list)
        self._eval_handlers = defaultdict(list)
        self._post_set_handlers = defaultdict(list)
        self._set_handlers = {}

        # construct initial state: make all defaults available, then set as
        # many values as we can
        defaults = dict(self._defaults)
        if defaults:
            warn("The MneExperiment._defaults attributed is deprecated. Use "
                 "MneExperiment.defaults instead.", DeprecationWarning)
        defaults.update(self.defaults)
        defaults.update(state)
        self.defaults = defaults
        for k, v in self._templates.iteritems():
            if v is None:  # field that needs a default value
                self._register_field(k)
            elif isinstance(v, basestring):
                self._register_field(k, None, v)
            elif isinstance(v, tuple):
                self._register_field(k, v, v[0])
            else:
                err = ("Invalid templates field value: %r. Need None, tuple "
                       "or string" % v)
                raise TypeError(err)

        if self.owner:
            task = self.__class__.__name__
            self.notification = Notifier(self.owner, task, self._crash_report,
                                         self._auto_debug)

    def __repr__(self):
        args = [repr(self._fields[arg]) for arg in self._repr_args]
        kwargs = [(arg, repr(self._fields[arg])) for arg in self._repr_kwargs]

        no_initial_state = len(self._fields._states) == 0
        for k in sorted(self._fields):
            if k in self._repr_args or k in self._repr_kwargs:
                continue
            elif k in self._compound_members:
                continue
            elif '{' in self._fields[k]:
                continue

            v = self._fields[k]
            if no_initial_state or v != self._fields.get_stored(k, level=0):
                kwargs.append((k, repr(v)))

        args.extend('='.join(pair) for pair in kwargs)
        args = ', '.join(args)
        return "%s(%s)" % (self.__class__.__name__, args)

    def _bind_eval(self, key, handler):
        self._eval_handlers[key].append(handler)

    def _bind_post_set(self, key, handler):
        handlers = self._post_set_handlers[key]
        if handler not in handlers:
            handlers.append(handler)

    def _bind_set(self, key, handler):
        if key in self._set_handlers:
            raise KeyError("set-handler for %r already set" % key)
        self._set_handlers[key] = handler

    def _crash_report(self):
        source = inspect.getsource(self.__class__)
        tree = str(self.show_state())

        # package versions
        from .. import __version__
        import mne
        versions = '\n'.join(("Eelbrain %s" % __version__,
                              "mne-python %s" % mne.__version__))

        return source, tree, versions

    def _find_missing_fields(self):
        """Check that all field names occurring in templates are valid entries

        Raises
        ------
        KeyError
            If any field names occurring in templates are not registered fields.
        """
        # find field names occurring in field values but not as fields
        missing = set()
        for temp in self._fields.values():
            for field in self._fmt_pattern.findall(temp):
                if field not in self._fields:
                    missing.add(field)
        if missing:
            raise KeyError("The following fields occur in templates but "
                               "are undefined: %s" % ', '.join(sorted(missing)))

    def _register_compound(self, key, elements):
        """Register a field that is composed out of other fields

        The compound always reflects ``' '.join(elements)`` including only
        elements that are not empty.

        Parameters
        ----------
        key : str
            The name of the compound field.
        elements : tuple of str
            The field names of the elements.
        """
        self._compound_members[key] = elements
        for e in elements:
            self._compounds[e].append(key)
            self._bind_post_set(e, self._update_compounds)
        self._fields[key] = None
        self._update_compound(key)

    def _register_field(self, key, values=None, default=None, set_handler=None,
                        eval_handler=None, post_set_handler=None):
        """Register an iterable field

        Parameters
        ----------
        key : str
            Name of the field.
        values : None | sequence of str
            Possible values for this field, if known.
        default : None | str
            Set the default value (if None, the first element in values).
        set_handler : None | callable
            Function to call instead of updating the state value,
        eval_handler : None | callable
            Function to use for evaluating a value before setting. Can be
            called without actually setting the value; any parameter changes
            need to be evaluated in post_set_handlers.
        post_set_handler : None | callable
            Function to call after the value is changed.
        """
        if key in self._fields:
            raise KeyError("Field already exists: %r" % key)

        if set_handler is not None:
            self._bind_set(key, set_handler)
        if eval_handler is not None:
            self._bind_eval(key, eval_handler)
        if post_set_handler is not None:
            self._bind_post_set(key, post_set_handler)

        default = self.defaults.get(key, default)

        if values is not None:
            if default is None:
                if len(values):
                    default = values[0]
                else:
                    msg = "Values for %r empty, can`t set default" % key
                    raise RuntimeError(msg)
            elif default not in values:
                err = ("Default %r for %r not in values "
                       "%s" % (default, key, str(values)))
                raise ValueError(err)

            self._field_values[key] = tuple(values)

        self._fields[key] = ''
        if default is not None:
            self.set(**{key: default})

    def expand_template(self, temp, keep=()):
        """Expand all constant variables in a template

        Parameters
        ----------
        temp : str
            Template or name of the template which should be expanded.
        keep : container (implements __contains__)
            Names of the variables which should not be expanded.

        Returns
        -------
        formatted_temp : str
            Template with all variables replaced by their values, except
            variables which have entries in field_values or in ``keep``.
        """
        temp = self._fields.get(temp, temp)

        while True:
            stop = True
            for name in self._fmt_pattern.findall(temp):
                if (name in keep) or (self._field_values.get(name, False)):
                    pass
                else:
                    temp = temp.replace('{%s}' % name, self._fields[name])
                    stop = False

            if stop:
                break

        return temp

    def find_keys(self, temp):
        """
        Find all terminal keys that are relevant for a template.

        Returns
        -------
        keys : set
            All terminal keys that are relevant for foormatting temp.
        """
        keys = set()
        temp = self._fields.get(temp, temp)

        for key in self._fmt_pattern.findall(temp):
            value = self._fields[key]
            if self._fmt_pattern.findall(value):
                keys = keys.union(self.find_keys(value))
            else:
                keys.add(key)

        return keys

    def format(self, string, vmatch=True, **kwargs):
        """Format a string (i.e., replace any '{xxx}' fields with their values)

        Parameters
        ----------
        string : str
            Template string.
        vmatch : bool
            For fields with known names, only allow existing field names.
        others :
            State parameters.

        Returns
        -------
        formatted_string : str
            The template temp formatted with current state values.
        """
        self.set(match=vmatch, **kwargs)

        while True:
            variables = self._fmt_pattern.findall(string)
            if variables:
                string = string.format(**self._fields)
            else:
                break

        return string

    def get(self, temp, **state):
        path = self.format('{%s}' % temp, **state)
        return path

    def get_field_values(self, field, exclude=True):
        """Find values for a field taking into account exclusion

        Parameters
        ----------
        field : str
            Field for which to find values.
        exclude : bool | list of str | str
            Exclude values. If True, exclude values based on ``self.exclude``.
        """
        values = self._field_values[field]
        if exclude is True:
            exclude = self.exclude.get(field, None)
        elif isinstance(exclude, basestring):
            exclude = (exclude,)

        if exclude:
            values = [v for v in values if v not in exclude]
        else:
            values = list(values)

        return values

    def iter(self, fields, exclude=True, values={}, mail=False, prog=False,
             **constants):
        """
        Cycle the experiment's state through all values on the given fields

        Parameters
        ----------
        fields : list | str
            Field(s) over which should be iterated.
        exclude : bool | dict  {str: bool, str: str, str: iterator over str}
            Exclude values from iteration. Boolean specifies whether to apply
            standard exclusion (``self.exclude``). A ``dict`` can be used to
            customize the exclusion per field with one of {field: bool,
            field: value, field: (sequence of values, )}. If only some fields
            are specified in a dict, True is assumed for absent fields.
        values : dict  {str: iterator over str}
            Fields with custom values to iterate over (instead of the
            corresponding field values) with {name: (sequence of values)}
            entries.
        group : None | str
            If iterating over subjects, use this group ('all' or a name defined
            in experiment.groups).
        prog : bool | str
            Show a progress dialog; str for dialog title.
        mail : bool | str
            Send an email when iteration is finished. Can be True or an email
            address. If True, the notification is sent to :attr:`.owner`.
        others :
            Fields with constant values throughout the iteration.
        """
        if mail is True:
            mail = self.owner

        # set constants
        self.set(**constants)
        self.store_state()

        if isinstance(fields, basestring):
            fields = [fields]
            yield_str = True
        else:
            yield_str = False
        fields = list(set(fields).difference(constants).union(values))

        # gather possible values to iterate over
        field_values = {}
        for field in fields:
            if field in values:
                field_values[field] = values[field]
            else:
                if isinstance(exclude, bool):
                    exclude_ = exclude
                elif field in exclude:
                    exclude_ = exclude[field]
                else:
                    exclude_ = True
                field_values[field] = self.get_field_values(field, exclude_)

        # pick out the fields to iterate, but drop excluded cases:
        v_lists = []
        for field in fields:
            v_lists.append(field_values[field])

        if len(v_lists):
            if prog:
                i_max = np.prod(map(len, v_lists))
                if not isinstance(prog, str):
                    prog = "MNE Experiment Iterator"
                progm = ui.progress_monitor(i_max, prog, "")
                prog = True

            for v_list in product(*v_lists):
                if prog:
                    progm.message(' | '.join(map(str, v_list)))
                self.restore_state(discard_tip=False)
                values = dict(zip(fields, v_list))
                self.set(**values)

                if yield_str:
                    yield v_list[0]
                else:
                    yield v_list

                if prog:
                    progm.advance()
        else:
            yield ()

        self.restore_state()
        if mail:
            send_email(mail, "Eelbrain Task Done", "I did as you desired, "
                       "my master.")

    def iter_temp(self, temp, exclude=True, values={}, mail=False, prog=False,
                  **constants):
        """
        Iterate through all paths conforming to a template given in ``temp``.

        Parameters
        ----------
        temp : str
            Name of a template in the MneExperiment.templates dictionary, or
            a path template with variables indicated as in ``'{var_name}'``
        """
        # if the name is an existing template, retrieve it
        temp = self.expand_template(temp, values.keys())

        # find variables for iteration
        variables = set(self._fmt_pattern.findall(temp))
        variables.difference_update(constants)

        for _ in self.iter(variables, exclude=exclude, values=values,
                           mail=mail, prog=prog, **constants):
            path = temp.format(**self._fields)
            yield path

    def restore_state(self, index=-1, discard_tip=True):
        """Restore a previously stored state

        Parameters
        ----------
        index : int
            Index of the state which to restore (specified as index into a
            list of stored states, i.e., negative values access recently
            stored states).
        discard_tip : bool
            Discard the relevant state after restoring it. All states stored
            later are discarded either way.
        """
        self._fields.restore_state(index, discard_tip)
        self._field_values.restore_state(index, discard_tip)
        self._params.restore_state(index, discard_tip)

    def set(self, match=True, allow_asterisk=False, **state):
        """Set the value of one or more fields.

        Parameters
        ----------
        match : bool
            For fields with stored values, only allow valid values.
        allow_asterisk : bool
            If a value contains '*', set the value without the normal value
            evaluation and checking mechanism.
        kwargs :
            Fields and values to set. Invalid fields raise a KeyError. Unless
            match == False, Invalid values raise a ValueError.
        """
        if not state:
            return

        # fields with special set handlers
        handled_state = {}
        for k in state.keys():
            if k in self._set_handlers:
                v = state.pop(k)
                self._set_handlers[k](v)
                handled_state[k] = ''

        # make sure only valid fields are set
        for k in state:
            if k not in self._fields:
                raise KeyError("No template named %r" % k)

        # eval all values
        for k in state.keys():
            eval_handlers = self._eval_handlers[k]
            v = state[k]
            if not isinstance(v, basestring):
                msg = "Values have to be strings, got %s=%r" % (k, v)
                raise TypeError(msg)
            elif '*' in v and allow_asterisk:
                pass
            elif eval_handlers:
                for handler in eval_handlers:
                    v = handler(v)
                    if not isinstance(v, basestring):
                        err = "Invalid conversion: %s=%r" % (k, v)
                        raise RuntimeError(err)
                    state[k] = v
            elif not match:
                pass
            elif k not in self._field_values:
                pass
            elif v not in self.get_field_values(k, False):
                err = ("Variable {k!r} has no value {v!r}. In order to "
                       "see valid values use e.list_values(); In order to "
                       "set a non-existent value, use e.set({k!s}={v!r}, "
                       "match=False).".format(k=k, v=v))
                raise ValueError(err)

        self._fields.update(state)

        # call post_set handlers
        for k, v in chain(state.iteritems(), handled_state.iteritems()):
            for handler in self._post_set_handlers[k]:
                handler(k, v)

    def show_fields(self, str_out=False):
        """
        Generate a table for all iterable fields and ther values.

        Parameters
        ----------
        str_out : bool
            Return the table as a string (instead of printing it).
        """
        lines = []
        for key in self._field_values:
            values = list(self.get_field_values(key))
            line = '%s:' % key
            head_len = len(line) + 1
            while values:
                v = repr(values.pop(0))
                if values:
                    v += ','
                if len(v) < 80 - head_len:
                    line += ' ' + v
                else:
                    lines.append(line)
                    line = ' ' * head_len + v

                if not values:
                    lines.append(line)

        table = os.linesep.join(lines)
        if str_out:
            return table
        else:
            print table

    def show_state(self, temp=None, empty=False, hide=[]):
        """
        List all top-level fields and their values (i.e., fields whose values
        do not contain templates).

        Parameters
        ----------
        temp : None | str
            Only show variables relevant to this template.
        empty : bool
            Show empty variables (items whose value is the empty string '').
        hide : list of str
            State variables to hide.

        Returns
        -------
        state : Table
            Table of (relevant) variables and their values.
        """
        table = fmtxt.Table('lll')
        table.cells('Key', '*', 'Value')
        table.caption('*: Value is modified from initialization state.')
        table.midrule()

        if temp is None:
            keys = (k for k, v in self._fields.iteritems()
                    if ('{' not in v) and len(v) < 60)
        else:
            keys = self.find_keys(temp)

        for k in sorted(keys):
            if k in hide:
                continue

            v = self._fields[k]
            if v != self._fields.get_stored(k, level=0):
                mod = '*'
            else:
                mod = ''

            if empty or mod or v:
                table.cells(k, mod, repr(v))

        return table

    def show_tree(self, root='root', fields=None):
        """
        Print a tree of the filehierarchy implicit in the templates

        Parameters
        ----------
        root : str
            Name of the root template (e.g., 'besa-root').
        fields : list of str
            Which fields to include in the tree (default is all).
        """
        if fields is None:
            fields = self._fields
        else:
            # find all implied fields
            new_fields = set(fields)
            fields = {}
            while new_fields:
                k = new_fields.pop()
                fields[k] = v = self._fields[k]
                new_fields.update([f for f in self._fmt_pattern.findall(v) if
                                   f not in fields])

        tree = {'.': self.get(root)}
        root_temp = '{%s}' % root
        for k, v in fields.iteritems():
            if str(v).startswith(root_temp):
                tree[k] = {'.': v.replace(root_temp, '')}
        _etree_expand(tree, fields)
        nodes = _etree_node_repr(tree, root)
        name_len = max(len(n) for n, _ in nodes)
        path_len = max(len(p) for _, p in nodes)
        pad = ' ' * (80 - name_len - path_len)
        print os.linesep.join(n.ljust(name_len) + pad + p.ljust(path_len)
                              for n, p in nodes)

    def store_state(self):
        """Store the current state

        See also
        --------
        .restore_state() : restore a previously stored state
        """
        self._fields.store_state()
        self._field_values.store_state()
        self._params.store_state()

    @LazyProperty
    def _temporary_state(self):
        return _TempStateController(self)

    def _update_compound(self, key):
        items = []
        for item_key in self._compound_members[key]:
            value = self.get(item_key)
            if value:
                items.append(value)
        self.set(**{key: ' '.join(items)})

    def _update_compounds(self, key, _):
        for compound in self._compounds[key]:
            self._update_compound(compound)


class FileTree(TreeModel):
    """
    :class:`TreeModel` subclass for representing a file system hierarchy
    """
    _repr_args = ('root',)

    def __init__(self, **state):
        TreeModel.__init__(self, **state)
        self._make_handlers = {}
        self._cache_handlers = {}
        self._register_field('root', eval_handler=self._eval_root)

    def _bind_cache(self, key, handler):
        """
        The cache function is called every time the file name is retrieved and
        should recreate the file if it is outdated.
        """
        if key in self._cache_handlers:
            raise RuntimeError("Cache handler for %r already defined." % key)
        elif key in self._make_handlers:
            raise RuntimeError("Make handler for %r already defined." % key)
        self._cache_handlers[key] = handler

    def _bind_make(self, key, handler):
        """
        The make function is called only when the file name is retrieved and
        the file does not exist.
        """
        if key in self._cache_handlers:
            raise RuntimeError("Cache handler for %r already defined." % key)
        elif key in self._make_handlers:
            raise RuntimeError("Make handler for %r already defined." % key)
        self._make_handlers[key] = handler

    @staticmethod
    def _eval_root(root):
        root = os.path.expanduser(root)
        if root != '':
            root = os.path.normpath(root)
        return root

    def get(self, temp, fmatch=False, vmatch=True, match=True, mkdir=False,
            make=False, **kwargs):
        """
        Retrieve a formatted template

        With match=True, '*' are expanded to match a file,
        and if there is not a unique match, an error is raised. With
        mkdir=True, the directory containing the file is created if it does not
        exist.

        Parameters
        ----------
        temp : str
            Name of the requested template.
        fmatch : bool
            "File-match": If the template contains asterisk ('*'), use glob to
            fill it in. An IOError is raised if the pattern does not match
            exactly one file.
        vmatch : bool
            "Value match": Require existence of the assigned value (only
            applies for fields with stored values).
        match : bool
            Do any matching (i.e., match=False sets fmatch as well as vmatch
            to False).
        mkdir : bool
            If the directory containing the file does not exist, create it.
        make : bool
            If a requested file does not exists, make it if possible.
        kwargs :
            Set any state values.
        """
        if not match:
            fmatch = vmatch = False

        path = TreeModel.get(self, temp, vmatch=vmatch, **kwargs)
        path = os.path.expanduser(path)

        # assert the presence of the file
        if fmatch and ('*' in path):
            paths = glob(path)
            if len(paths) == 1:
                path = paths[0]
            elif len(paths) > 1:
                err = "More than one files match %r: %r" % (path, paths)
                raise IOError(err)
            else:
                raise IOError("No file found for %r" % path)

        # create the directory
        if mkdir:
            dirname = os.path.dirname(path)
            if not os.path.exists(dirname):
                root = self.get('root')
                if root == '':
                    raise IOError("Prevented from creating directories because "
                                  "root is not set. Use root='.' for a "
                                  "relative root.")
                elif os.path.exists(root):
                    os.makedirs(dirname)
                else:
                    raise IOError("Prevented from creating directories because "
                                  "Root does not exist: %r" % root)

        # make the file
        if make:
            if temp in self._cache_handlers:
                self._cache_handlers[temp]()
            elif not os.path.exists(path):
                if temp in self._make_handlers:
                    with self._temporary_state:
                        self._make_handlers[temp]()
                elif temp.endswith('-dir'):
                    os.makedirs(path)
                else:
                    raise RuntimeError("No make handler for %r." % temp)

        return path

    def glob(self, temp, **state):
        """Find all files matching a certain pattern

        Parameters
        ----------
        temp : str
            Name of the path template for which to find files.

        Notes
        -----
        State parameters can include an asterisk ('*') to match multiple files.
        Uses :func:`glob.glob`.
        """
        with self._temporary_state:
            pattern = self.get(temp, allow_asterisk=True, **state)
        file_paths = glob(pattern)
        return file_paths

    def show_file_status(self, temp, row, col=None, count=True, present='X',
                         absent='-', **kwargs):
        """Compile a table about the existence of files

        Parameters
        ----------
        temp : str
            The name of the path template for the files to examine.
        row : str
            Field over which to alternate rows.
        col : None | str
            Field over which to alternate columns (default is a single column).
        count : bool
            Add a column with a number for each line (default True).
        present : str
            String to display when a given file is present (default 'X').
        absent : str
            String to display when a given file is absent (default '-').
        others :
            ``self.iter()`` kwargs.
        """
        if col is None:
            ncol = 1
        else:
            col_v = self.get_field_values(col)
            ncol = len(col_v)

        # table header
        table = fmtxt.Table('r' * bool(count) + 'l' * (ncol + 1))
        if count:
            table.cell()
        table.cell(row.capitalize())
        if col is None:
            table.cell(temp.capitalize())
        else:
            for name in col_v:
                table.cell(name.capitalize())
        table.midrule()

        # body
        for i, row_v in enumerate(self.iter(row, **kwargs)):
            if count:
                table.cell(i)
            table.cell(row_v)
            exist = []
            if col is None:
                path = self.get(temp)
                exist.append(os.path.exists(path))
            else:
                for v in col_v:
                    path = self.get(temp, **{col: v})
                    exist.append(os.path.exists(path))

            for exists in exist:
                if exists:
                    table.cell(present)
                else:
                    table.cell(absent)

        return table

    def show_file_status_mult(self, files, fields, count=True, present='X',
                              absent='-', **kwargs):
        """
        Compile a table about the existence of multiple files

        Parameters
        ----------
        files : str | list of str
            The names of the path templates whose existence to list.
        fields : str | list of str
            The names of the variables for which to list files (i.e., for each
            unique combination of ``fields``, list ``files``).
        count : bool
            Add a column with a number for each subject.
        present : str
            String to display when a given file is present.
        absent : str
            String to display when a given file is absent.

        Examples
        --------
        >>> e.show_file_status_mult(['raw-file', 'trans-file', 'fwd-file'],
        ... 'subject')
             Subject   Raw-file   Trans-file   Fwd-file
        -----------------------------------------------
         0   AD001     X          X            X
         1   AD002     X          X            X
         2   AD003     X          X            X
        ...
        """
        if not isinstance(files, (list, tuple)):
            files = [files]
        if not isinstance(fields, (list, tuple)):
            fields = [fields]

        ncol = (len(fields) + len(files))
        table = fmtxt.Table('r' * bool(count) + 'l' * ncol)
        if count:
            table.cell()
        for name in fields + files:
            table.cell(name.capitalize())
        table.midrule()

        for i, _ in enumerate(self.iter(fields, **kwargs)):
            if count:
                table.cell(i)

            for field in fields:
                table.cell(self.get(field))

            for temp in files:
                path = self.get(temp)
                if os.path.exists(path):
                    table.cell(present)
                else:
                    table.cell(absent)

        return table

    def show_in_finder(self, temp, **kwargs):
        "Reveals the file corresponding to the ``temp`` template in the Finder."
        fname = self.get(temp, **kwargs)
        subprocess.call(["open", "-R", fname])

    def push(self, dst_root, names, overwrite=False, exclude=False, **kwargs):
        """Copy files to another experiment root folder.

        Before copying any files the user is asked for confirmation.

        Parameters
        ----------
        dst_root : str
            Path to the root to which the files should be copied.
        names : str | sequence of str
            Name(s) of the template(s) of the files that should be copied.
        overwrite : bool
            What to do if the target file already exists.
        others :
            Update experiment state.

        Notes
        -----
        Use ``e.show_tree()`` to find out which element(s) to copy.
        """
        if isinstance(names, basestring):
            names = [names]

        # find files
        files = []
        for name in names:
            for src in self.iter_temp(name, exclude=exclude, **kwargs):
                if '*' in src:
                    raise NotImplementedError("Can't fnmatch here yet")

                if os.path.exists(src):
                    dst = self.get(name, root=dst_root)
                    if src == dst:
                        raise ValueError("Source == destination (%r)" % src)

                    if os.path.exists(dst):
                        flag = 'o' if overwrite else 'e'
                    else:
                        flag = ' '
                else:
                    dst = None
                    flag = 'm'
                files.append((src, dst, flag))

        # prompt for confirmation
        root = self.get('root')
        n_root = len(root)
        for src, dst, flag in files:
            if src.startswith(root):
                src = src[n_root:]
            print(' '.join((flag, src[-78:])))
        print("Flags: o=overwrite, e=skip, it exists, m=skip, source is "
              "missing")
        msg = "Proceed? (confirm with 'yes'): "
        if raw_input(msg) != 'yes':
            return

        # copy the files
        for src, dst, flag in files:
            if flag in ('e', 'm'):
                continue

            dirpath = os.path.dirname(dst)
            if not os.path.exists(dirpath):
                os.makedirs(dirpath)

            if os.path.isdir(src):
                if flag == 'o':
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)

    def rename(self, old, new, exclude=False):
        """
        Rename files corresponding to a pattern (or template)

        Parameters
        ----------
        old : str
            Template for the files to be renamed. Can interpret '*', but will
            raise an error in cases where more than one file fit the pattern.
        new : str
            Template for the new names.

        Examples
        --------
        The following command will collect a specific file for each subject and
        place it in a common folder:

        >>> e.rename('{root}/{subject}/info.txt',
                     '/some_other_place/{subject}s_info.txt'
        """
        new = self.expand_template(new)
        files = []
        for old_name in self.iter_temp(old, exclude):
            if '*' in old_name:
                matches = glob(old_name)
                if len(matches) == 1:
                    old_name = matches[0]
                elif len(matches) > 1:
                    err = ("Several files fit the pattern %r" % old_name)
                    raise ValueError(err)

            if os.path.exists(old_name):
                new_name = self.format(new)
                files.append((old_name, new_name))

        if not files:
            print "No files found for %r" % old
            return

        old_pf = os.path.commonprefix([pair[0] for pair in files])
        new_pf = os.path.commonprefix([pair[1] for pair in files])
        n_pf_old = len(old_pf)
        n_pf_new = len(new_pf)

        table = fmtxt.Table('lll')
        table.cells('Old', '', 'New')
        table.midrule()
        table.caption("%s -> %s" % (old_pf, new_pf))
        for old, new in files:
            table.cells(old[n_pf_old:], '->', new[n_pf_new:])

        print table

        msg = "Rename %s files (confirm with 'yes')? " % len(files)
        if raw_input(msg) == 'yes':
            for old, new in files:
                dirname = os.path.dirname(new)
                if not os.path.exists(dirname):
                    os.makedirs(dirname)
                os.rename(old, new)

    def rename_field(self, temp, field, old, new, exclude=False, **kwargs):
        """Change the value of one field in paths corresponding to a template

        Parameters
        ----------
        temp : str
            Template name.
        field : str
            Field to change.
        old : str
            Old value.
        new : str
            New value.
        kwargs :
            ``self.iter_temp`` arguments.
        """
        items = []  # (tag, src, dst)
        kwargs[field] = old
        dst_kwa = {field: new}
        for src in self.iter_temp(temp, exclude, ** kwargs):
            dst = self.get(temp, **dst_kwa)
            if os.path.exists(src):
                if os.path.exists(dst):
                    tag = 'o'
                else:
                    tag = ' '
            else:
                tag = 'm'
            items.append((tag, src, dst))

        src_prefix = os.path.commonprefix(tuple(item[1] for item in items))
        dst_prefix = os.path.commonprefix(tuple(item[2] for item in items))
        src_crop = len(src_prefix)
        dst_crop = len(dst_prefix)

        # print info
        if src_prefix == dst_prefix:
            lines = ['in ' + src_prefix, '']
        else:
            lines = [src_prefix, '->' + dst_prefix, '']

        for tag, src, dst in items:
            lines.append('%s %s -> %s' % (tag, src[src_crop:], dst[dst_crop:]))
        lines.append('')
        msg = 'Legend  m: source is missing;  o: will overwite a file'
        lines.append(msg)
        print os.linesep.join(lines)
        rename = tuple(item for item in items if item[0] == ' ')
        if not rename:
            return

        msg = "Rename %i files (confirm with 'yes')? " % len(rename)
        if raw_input(msg) != 'yes':
            return

        for _, src, dst in rename:
            os.rename(src, dst)
        print "Done"

    def rm(self, temp, confirm=False, **constants):
        """
        Remove all files corresponding to a template

        Asks for confirmation before deleting anything. Uses glob, so
        individual templates can be set to '*'.

        Parameters
        ----------
        temp : str
            Name of the path template for which to find and delete files.
        confirm : bool
            Confirm removal of the selected files. If False (default) the user
            is prompted for confirmation with a list of files; if True, the
            files are removed immediately.
        **others** :
            Set field values (values can be '*' to match all).
        """
        files = self.glob(temp, **constants)
        if files:
            root = self.get('root')
            print "root: %s\n" % root
            root_len = len(root)
            for name in files:
                if name.startswith(root):
                    print name[root_len:]
                else:
                    print name
            msg = ("Delete %i files or directories (confirm with 'yes')? "
                   % len(files))
            if confirm or raw_input(msg) == 'yes':
                print 'deleting...'
                for path in files:
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)
            else:
                print 'aborting...'
        else:
            print "No files found for %r" % temp
