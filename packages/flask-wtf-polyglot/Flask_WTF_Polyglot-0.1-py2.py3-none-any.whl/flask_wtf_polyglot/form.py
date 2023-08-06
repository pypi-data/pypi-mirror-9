from flask_wtf.form import Form

from wtf_polyglot.meta import PolyglotMeta


class PolyglotForm(Form):
    Meta = PolyglotMeta
