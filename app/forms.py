from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, SelectField)
from wtforms.validators import DataRequired

class ResetImageForm(FlaskForm):
    submitReset = SubmitField('Reset Image')

class StarSelectForm(FlaskForm):
    select_star = SelectField('Stars')
    select_filters = StringField(default = "B,V,R,I,H")
    submitStar = SubmitField('Update Template')

class ScheduleForm(FlaskForm):
    fileName = StringField(default = "...insert here...",
                            validators=[DataRequired()])
    title = StringField(default = "object",
                            validators=[DataRequired()])
    observer = StringField(default = "Clem",
                            validators=[DataRequired()])
    source = StringField(default = "...insert here...",
                            validators=[DataRequired()])
    ra = StringField(default = "...insert here...",
                            validators=[DataRequired()])
    dec = StringField(default = "...insert here...",
                            validators=[DataRequired()])
    epoch = StringField(default = "2000",
                            validators=[DataRequired()])
    lststart = StringField(default = "14:00:00",
                            validators=[DataRequired()])
    filters = StringField(default = "...insert here...",
                            validators=[DataRequired()])
    duration = StringField(default = "...insert here...",
                            validators=[DataRequired()])
    binning = StringField(default = "1,1",
                            validators=[DataRequired()])
    subimage = StringField(default = "0,0,3056,3056",
                            validators=[DataRequired()])
    priority = StringField(default = "0",
                            validators=[DataRequired()])
    compress = StringField(default = "0",
                            validators=[DataRequired()])
    imagedir = StringField(default = "/usr/local/telescope/user/images",
                            validators=[DataRequired()])
    ccdcalib = StringField(default = "NONE",
                            validators=[DataRequired()])
    shutter = StringField(default = "OPEN",
                            validators=[DataRequired()])
    repeat = StringField(default = "60",
                            validators=[DataRequired()])
    submitSched = SubmitField('Create Schedule File')