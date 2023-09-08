from flask_wtf import FlaskForm
from wtforms import IntegerField,StringField,SubmitField,TextAreaField, URLField, PasswordField
from wtforms.validators import InputRequired,NumberRange,Email,Length,EqualTo


class MovieForm(FlaskForm):
    title = StringField("Title",validators=[InputRequired(),])
    director = StringField("Director",validators=[InputRequired()])
    year=IntegerField("Year",validators=[InputRequired(),NumberRange(min=1878,message="Please enter a number bigger than 1878!")])
    submit = SubmitField("Add movie")

class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        # checks valuelist contains at least 1 element, and the first element isn't falsy (i.e. empty string)
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []
 

class ExtendedMovieForm(MovieForm):
    cast = StringListField("Cast")
    series = StringListField("Series")
    tags = StringListField("Tags")
    description = TextAreaField("Description")
    video_link =  URLField("Video link")

    submit = SubmitField("Edit")


class RegisterForm(FlaskForm):
    email = StringField("Email",validators=[InputRequired(),Email()])
    password= PasswordField("Password",validators=[InputRequired(),Length(min=4,max=20,message="Password between 4 and 20 characters!")])
    confirm_password = PasswordField("Confirm password",validators=[
        InputRequired(),
        Length(min=4,max=20,message="Password between 4 and 20 characters!"),
        EqualTo("password",message="This password did not match the one in the password field.")])
    
    submit = SubmitField("Register")


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")




















