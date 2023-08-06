# -*- coding:utf-8 -*-
from django.db.models import CharField, Lookup, Transform


class SoundsLike(Lookup):
    lookup_name = 'sounds_like'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        return '%s SOUNDS LIKE %s' % (lhs, rhs), params


class Soundex(Transform):
    lookup_name = 'soundex'
    output_field = CharField()

    def as_sql(self, compiler, connection):
        lhs, params = compiler.compile(self.lhs)
        return "SOUNDEX(%s)" % lhs, params


# These are mostly used for custom fields


class SetContains(Lookup):
    lookup_name = 'contains'

    def as_sql(self, qn, connection):
        lhs, lhs_params = self.process_lhs(qn, connection)
        rhs, rhs_params = self.process_rhs(qn, connection)
        params = lhs_params + rhs_params
        # Put rhs on the left since that's the order FIND_IN_SET uses
        return 'FIND_IN_SET(%s, %s)' % (rhs, lhs), params


class SetIContains(SetContains):
    lookup_name = 'icontains'
