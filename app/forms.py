from wtforms.form import Form
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField,IntegerField,SelectMultipleField,TextAreaField,SelectField,PasswordField,FloatField,TextField,DateField
from wtforms.validators import DataRequired,NumberRange
from models import get_all_esfs,get_cost_duration,get_next_resource_id,get_all_incidents,get_next_incident_id

esf_list=[]


class LoginForm(Form):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)

class NewResourceForm(FlaskForm):
    esf_list = get_all_esfs()
    rid = get_next_resource_id()

    esf_list.insert(0,(0, u'#0 - select an option -'))
    sec_list = esf_list[1:]
    resource_id = StringField('Resource Id',default=rid)
    owner = StringField('Owner')
    resource_name = StringField('Resource Name', validators=[DataRequired()])
    primary_esf = SelectField('Primary ESF', choices=esf_list,coerce=int,validators=[DataRequired()])
    additional_esfs = SelectMultipleField('Additional Esfs', choices = sec_list,coerce=int)
    model = StringField('Model',default='')
    capabilities = TextAreaField('Capabilities')
    add_capability = StringField()
    latitude = FloatField('Latitude', validators=[DataRequired(),NumberRange(min=-90,max=90)])
    longitude = FloatField('Longitude', validators=[DataRequired(),NumberRange(min=-90,max=90)])
    cost = FloatField('Cost', validators=[DataRequired(),NumberRange(min=0)])
    duration=get_cost_duration()
    print duration
    cost_duration=SelectField('cost_duration', choices=duration,coerce=int, default='1')


class IncidentInfoForm(FlaskForm):

    incident_id = StringField('Incident Id',default=get_next_incident_id())
    date = DateField('Date',format='%Y-%m-%d', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    latitude = FloatField('Latitude', validators=[DataRequired(),NumberRange(min=-90,max=90)])
    longitude = FloatField('Longitude', validators=[DataRequired()])

class SearchResourceForm(FlaskForm):
    def __init__(self,incident_choices):
        super(SearchResourceForm,self).__init__()
        self.incident_list.choices = incident_choices

    esf_list = get_all_esfs()
    esf_list.insert(0,(0, u'#0 - select an option -'))
    uid = StringField('UserId')
    keyword = StringField('Keyword')
    esf = SelectField('ESF', choices=esf_list,coerce=int)
    location = FloatField('Location',default=50000)
    incident_list = SelectField('Incident')
