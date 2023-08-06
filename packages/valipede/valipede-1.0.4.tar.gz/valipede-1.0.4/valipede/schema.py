import simpleobserver
from .fields import Compound

__all__ = [
    'Schema'
]


class Schema(object):

    def __init__(self, *mixins, **fields):
        self.mixins = mixins
        self.fields = {}

        for m in self.mixins:
            self.fields.update(m.fields)
        self.fields.update(fields)

        self.validator = Compound(**self.fields)
        
        events = ['validate']
        self.before = simpleobserver.Subject(*events)
        self.after = simpleobserver.Subject(*events)


    def validate(self, fields):
        for m in self.mixins:
            m.before.fire('validate', fields)
        self.before.fire('validate', fields)

        validated_fields = self.validator.validate(fields)

        for m in self.mixins:
            m.after.fire('validate', validated_fields)
        self.after.fire('validate', validated_fields)

        return validated_fields
        