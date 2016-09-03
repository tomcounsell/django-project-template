class BehaviorTestCaseMixin(object):
  def get_model(self):
    return getattr(self, 'model')

  def create_instance(self, **kwargs):
    raise NotImplementedError("Implement me")
