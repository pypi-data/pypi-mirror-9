import collections
import itertools
from numbers import Number

from ..._compat import iteritems, OrderedDict, string_types, imap, izip, reduce, xrange
from ...utils.python import getargspec
from .parameters import Parametrization, get_parametrization_fixtures
from .utils import nofixtures

_PRINTABLE_TYPES = (Number,) + string_types


class VariationFactory(object):

    """Helper class to produce variations, while properly naming the needed fixtures to help identifying tests
    """

    def __init__(self, fixture_store):
        super(VariationFactory, self).__init__()
        self._store = fixture_store
        self._needed_fixtures = list(fixture_store.iter_autouse_fixtures_in_namespace())
        self._named_fixture_ids = OrderedDict()
        self._known_value_strings = collections.defaultdict(dict)

    def add_needed_fixture_id(self, fixture_id):
        self._needed_fixtures.append(self._store.get_fixture_by_id(fixture_id))

    def add_needed_fixtures_from_method(self, method):
        self._add_needed_fixtures_from_function(method, is_method=True)

    def add_needed_fixtures_from_function(self, func):
        self._add_needed_fixtures_from_function(func, is_method=False)

    def _add_needed_fixtures_from_function(self, func, is_method):

        if isinstance(func, tuple):
            namespace, func = func
        else:
            namespace = None

        if nofixtures.is_marked(func):
            return

        arg_names = getargspec(func).args[1 if is_method else 0:]

        parametrizations = {}
        for param in get_parametrization_fixtures(func):
            # make sure the parametrization is in the store
            self._store.ensure_known_parametrization(param)
            parametrizations[param.name] = param

        for arg_name in arg_names:
            fixture = parametrizations.get(arg_name, None)
            if fixture is None:
                fixture = self._store.get_fixture_by_name(arg_name)

            self._needed_fixtures.append(fixture)
            if namespace is not None:
                arg_name = '{0}:{1}'.format(namespace, arg_name)
            self._named_fixture_ids[fixture.info.id] = arg_name

    def iter_variations(self):
        param_ids = list(reduce(set.union, imap(self._store.get_all_needed_parametrization_ids, self._needed_fixtures), set()))
        parametrizations = [self._store.get_fixture_by_id(param_id) for param_id in param_ids]
        if not param_ids:
            yield Variation()
            return
        for value_indices in itertools.product(*(xrange(len(p.values)) for p in parametrizations)):
            yield self._build_variation(parametrizations, value_indices)

    def _build_variation(self, parametrizations, value_indices):
        variation_dict = dict((p.info.id, p.values[param_index])
                              for p, param_index in izip(parametrizations, value_indices))
        return Variation(variation_dict, representation=self._build_representation(variation_dict))

    def _build_representation(self, variation_dict):

        if not self._named_fixture_ids:
            return None

        parts = []
        for fixture_id, fixture_name in iteritems(self._named_fixture_ids):
            fixture = self._store.get_fixture_by_id(fixture_id)
            needed_ids = self._store.get_all_needed_parametrization_ids(fixture)
            combination = frozenset((param_id, variation_dict[param_id]) for param_id in needed_ids)
            value_str = self._known_value_strings[fixture_id].get(combination)
            if value_str is None:
                if isinstance(fixture, Parametrization) and self._is_printable(variation_dict[fixture_id]):
                    value_str = str(variation_dict[fixture_id])
                else:
                    value_str = '{0}{1}'.format(fixture_name, len(self._known_value_strings[fixture_id]))
                self._known_value_strings[fixture_id][combination] = value_str
            parts.append('{0}={1}'.format(fixture_name, value_str))
        return ', '.join(parts)

    def _is_printable(self, value):
        return isinstance(value, _PRINTABLE_TYPES)


class Variation(object):

    """Represents a single variation of fixtures. A variation is merely a mapping of fixture ids to their values.
    This mostly applies for parametrization fixtures. The other fixtures follow since they are either constant
    or indirectly depend on parametrization"""

    def __init__(self, variation_dict=None, representation=None):
        super(Variation, self).__init__()
        if variation_dict is None:
            variation_dict = {}
        self.variation_dict = variation_dict
        self.representation = representation

    def has_value_for_fixture_id(self, fixture_id):
        return fixture_id in self.variation_dict

    def get_fixture_value(self, fixture_id):
        return self.variation_dict[fixture_id]

    def __eq__(self, other):
        if isinstance(other, Variation):
            other = other.variation_dict
        if not isinstance(other, dict):
            return NotImplemented
        return self.variation_dict == other

    def __ne__(self, other):
        return not (self == other)  # pylint: disable=superfluous-parens

    def __repr__(self):
        return 'Variation({0})'.format(', '.join('{0}={1}'.format(key, value) for key, value in iteritems(self.variation_dict)))

    def __nonzero__(self):
        return bool(self.variation_dict)

    __bool__ = __nonzero__
