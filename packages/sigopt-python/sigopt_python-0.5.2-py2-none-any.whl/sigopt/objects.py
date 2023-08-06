import copy

class ApiObject(object):
  def __init__(self, body):
    self._body = body

  def __repr__(self):
    return repr(self._body)

  def to_json(self):
    return copy.deepcopy(self._body)


class Assignments(ApiObject):
  def get(self, key):
    return self._body.get(key)

  def __getitem__(self, key):
    return self._body[key]


class Bounds(ApiObject):
  @property
  def max(self):
    return self._body.get('max')

  @property
  def min(self):
    return self._body.get('min')


class CategoricalValue(ApiObject):
  @property
  def name(self):
    return self._body.get('name')


class Client(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def name(self):
    return self._body.get('name')


class Cohort(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def name(self):
    return self._body.get('name')

  @property
  def allocation(self):
    return self._body.get('allocation')

  @property
  def successes(self):
    return self._body.get('successes')

  @property
  def attempts(self):
    return self._body.get('attempts')

  @property
  def state(self):
    return self._body.get('state')

  @property
  def suggestion(self):
    _suggestion = self._body.get('suggestion')
    return Suggestion(_suggestion) if _suggestion else None


class Experiment(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def name(self):
    return self._body.get('name')

  @property
  def parameters(self):
    _parameters = self._body.get('parameters', [])
    return [Parameter(p) for p in _parameters]

  @property
  def metric(self):
    _metric = self._body.get('metric')
    return Metric(_metric) if _metric is not None else None


class Metric(ApiObject):
  @property
  def name(self):
    return self._body.get('name')


class Observation(ApiObject):
  @property
  def assignments(self):
    _assignments = self._body.get('assignments')
    return Assignments(_assignments) if _assignments is not None else None

  @property
  def value(self):
    return self._body.get('value')

  @property
  def value_stddev(self):
    return self._body.get('value_stddev')


class Parameter(ApiObject):
  @property
  def name(self):
    return self._body.get('name')

  @property
  def type(self):
    return self._body.get('type')

  @property
  def bounds(self):
    _bounds = self._body.get('bounds')
    return Bounds(_bounds) if _bounds is not None else None

  @property
  def categorical_values(self):
    _categorical_values = self._body.get('categorical_values', [])
    return [CategoricalValue(cv) for cv in _categorical_values]

  @property
  def transformation(self):
    return self._body.get('transformation')


class Suggestion(ApiObject):
  @property
  def assignments(self):
    _assignments = self._body.get('assignments')
    return Assignments(_assignments) if _assignments is not None else None

  @property
  def expected_improvement(self):
    return self._body.get('expected_improvement')


class Worker(ApiObject):
  @property
  def id(self):
    return self._body.get('id')

  @property
  def suggestion(self):
    _suggestion = self._body.get('suggestion')
    return Suggestion(_suggestion) if _suggestion else None

  @property
  def claimed_time(self):
    return self._body.get('claimed_time')
