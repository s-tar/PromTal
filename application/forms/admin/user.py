from flask_wtf import Form
from wtforms import StringField, DateField, FileField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp



class EditUserForm(Form):

    full_name = StringField('ФИО', validators=[DataRequired(), Length(0, 64)])
    mobile_phone = StringField('Мобильный номер', validators=[DataRequired()])
    inner_phone = StringField('Внутренний номер', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[DataRequired()])
    avatar = FileField('Фото', validators=[DataRequired(), Regexp('\.(jpg|png|jpeg|gif)$')])
    skype = StringField('Skype', validators=[DataRequired()])
    submit = SubmitField('Сохранить')