from flask_wtf import Form
from wtforms import StringField, DateField, FileField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Regexp, Email

from application.models.group import Group


class EditUserForm(Form):
    full_name = StringField('ФИО', validators=[DataRequired(), Length(0, 64)])
    mobile_phone = StringField('Мобильный номер', validators=[DataRequired()])
    inner_phone = StringField('Внутренний номер', validators=[DataRequired()])
    birth_date = DateField('Дата рождения', validators=[DataRequired()])
    avatar = FileField('Фото', validators=[DataRequired(), Regexp(r'\.(jpg|png|jpeg|gif)$')])
    skype = StringField('Skype', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class AddUserForm(Form):
    name = StringField("Имя", validators=[DataRequired(), Length(0, 32)])
    surname = StringField("Фамилия", validators=[DataRequired(), Length(0, 32)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    login = StringField("Логин", validators=[DataRequired()])
    groups = SelectMultipleField("Группы",
                                 validators=[DataRequired()],
                                 choices=[(group.id, group.name) for group in Group.query.order_by('name')])  # TODO Add choices from DB
    mobile_phone = StringField("Моб. тел.", validators=[DataRequired()])
    save = SubmitField("Сохранить")
    cancel = SubmitField("Отмена")
