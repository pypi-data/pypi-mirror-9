from cubicweb.predicates import Predicate


class match_ws_etype(Predicate):
    def __init__(self, etype):
        self.etype = etype

    def __call__(self, cls, req, **kwargs):
        return 1 if req.form.get('_ws_etype') == self.etype else 0
