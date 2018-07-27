from wtforms import Form, IntegerField, validators


class MineBlocksForm(Form):
    num_blocks = IntegerField(
        'How many blocks',
        [validators.NumberRange(min=1)],
        default=101,
    )
