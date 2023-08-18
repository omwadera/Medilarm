from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, BooleanField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class MedicineForm(FlaskForm):
    name = StringField('Medicine Name', validators=[DataRequired()])
    photo = FileField('Medicine Photo', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Images only!')])
    before_breakfast = BooleanField('Before Breakfast')
    after_breakfast = BooleanField('After Breakfast')
    breakfast = BooleanField('During Breakfast')
    before_lunch = BooleanField('Before Lunch')
    after_lunch = BooleanField('After Lunch')
    lunch = BooleanField('During Lunch')
    before_dinner = BooleanField('Before Dinner')
    after_dinner = BooleanField('After Dinner')
    dinner = BooleanField('During Dinner')
    notes = TextAreaField('Medicine Notes', validators=[Length(max=500)])
    submit = SubmitField('Add Medicine')
    morning = BooleanField('Morning')  # New Checkbox
    afternoon = BooleanField('Afternoon')  # New Checkbox
    evening = BooleanField('Evening')  # New Checkbox