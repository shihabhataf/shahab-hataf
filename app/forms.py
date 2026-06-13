from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, TextAreaField, SelectField, BooleanField, URLField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional, URL

class LoginForm(FlaskForm):
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired()])
    remember = BooleanField('تذكرني')

class RegisterForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired(), Length(3, 80)])
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(2, 150)])
    email = StringField('البريد الإلكتروني', validators=[DataRequired(), Email()])
    password = PasswordField('كلمة المرور', validators=[DataRequired(), Length(6, 128)])
    confirm_password = PasswordField('تأكيد كلمة المرور', validators=[DataRequired(), EqualTo('password')])

class ArticleForm(FlaskForm):
    title = StringField('العنوان', validators=[DataRequired(), Length(5, 300)])
    content = TextAreaField('المحتوى', validators=[DataRequired()])
    excerpt = TextAreaField('الملخص', validators=[Optional(), Length(max=500)])
    cover_image = FileField('صورة الغلاف', validators=[FileAllowed(['jpg','jpeg','png','gif','webp'])])
    youtube_url = StringField('رابط يوتيوب', validators=[Optional()])
    category_id = SelectField('التصنيف', coerce=int, validators=[Optional()])
    tags = StringField('الوسوم (مفصولة بفاصلة)', validators=[Optional()])
    status = SelectField('الحالة', choices=[('draft','مسودة'),('published','منشور')])

class CommentForm(FlaskForm):
    content = TextAreaField('تعليقك', validators=[DataRequired(), Length(3, 1000)])

class ProfileForm(FlaskForm):
    full_name = StringField('الاسم الكامل', validators=[DataRequired(), Length(2, 150)])
    bio = TextAreaField('نبذة تعريفية', validators=[Optional(), Length(max=500)])
    avatar = FileField('الصورة الشخصية', validators=[FileAllowed(['jpg','jpeg','png','webp'])])
    current_password = PasswordField('كلمة المرور الحالية', validators=[Optional()])
    new_password = PasswordField('كلمة المرور الجديدة', validators=[Optional(), Length(6, 128)])

class CategoryForm(FlaskForm):
    name = StringField('الاسم', validators=[DataRequired(), Length(2, 100)])
    description = TextAreaField('الوصف', validators=[Optional()])
    color = StringField('اللون', validators=[Optional()])
    icon = StringField('الأيقونة', validators=[Optional()])

class SearchForm(FlaskForm):
    q = StringField('بحث', validators=[DataRequired()])
