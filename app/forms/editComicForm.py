from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, IntegerField, DateField, DecimalField, SelectField, HiddenField,
                     FieldList, FormField, Form, SubmitField)
from wtforms.validators import InputRequired, Length, NumberRange, Optional


class TextObjectForm(Form):
    description = StringField('Description', render_kw={'readonly': True})

    text = TextAreaField(
        'Text',
        validators=[Optional()],
        render_kw={'rows': 10, 'cols': 75}
    )

    language = StringField(
        'Language',
        validators=[Optional()]
    )


class EditComicForm(FlaskForm):
    """ Form class for editing comic details """
    id = IntegerField(
        'Comic ID',
        validators=[NumberRange(min=0, max=9999999999),
                    InputRequired()],
        render_kw={'readonly': True},
    )

    digitalId = IntegerField(
        'Comic Digital ID',
        validators=[NumberRange(min=0, max=9999999999),
                    Optional(strip_whitespace=True)]
    )

    title = StringField(
        'Comic Title',
        validators=[Length(max=1000),
                    Optional(strip_whitespace=True)]
    )

    issueNumber = IntegerField(
        'Comic Issue Number',
        validators=[NumberRange(min=0),
                    Optional(strip_whitespace=True)]
    )

    variantDescription = TextAreaField(
        'Comic Variant Description',
        validators=[Length(max=2147483647),
                    Optional(strip_whitespace=True)],
        render_kw={'rows': 10, 'cols': 75}
    )

    description = TextAreaField(
        'Comic Description',
        validators=[Length(max=2147483647),
                    Optional(strip_whitespace=True)],
        render_kw={'rows': 10, 'cols': 75}
    )

    modified = DateField(
        'Modified',
        validators=[Optional()]
    )

    isbn = StringField(
        'ISBN',
        validators=[Length(max=45),
                    Optional()]
    )

    upc = StringField(
        'UPC',
        validators=[Length(max=45),
                    Optional()]
    )

    diamondCode = StringField(
        'Diamond Code',
        validators=[Length(max=45),
                    Optional()]
    )

    ean = StringField(
        'EAN',
        validators=[Length(max=45),
                    Optional()]
    )

    issn = StringField(
        'ISSN',
        validators=[Length(max=45),
                    Optional()]
    )

    format = StringField(
        'Format',
        validators=[Length(max=45),
                    Optional()]
    )

    pageCount = IntegerField(
        'Page Count',
        validators=[NumberRange(min=0, max=10000),
                    Optional()]
    )

    textObjects = FieldList(
        FormField(TextObjectForm),
        'Text Object',
        validators=[Optional()],
        min_entries=0,
        max_entries=5
    )

    resourceURI = StringField(
        'Resource URI',
        validators=[Length(max=255),
                    Optional()]
    )

    onSaleDate = DateField(
        'On Sale Date',
        validators=[Optional()]
    )

    focDate = DateField(
        'Foc Date',
        validators=[Optional()]
    )

    unlimitedDate = DateField(
        'Unlimited Date',
        validators=[Optional()]
    )

    digitalPurchaseDate = DateField(
        'Digital Purchase Date',
        validators=[Optional()]
    )

    printPrice = DecimalField(
        'Print Price',
        places=2,
        validators=[NumberRange(min=0), Optional()]
    )

    digitalPurchasePrice = DecimalField(
        'Digital Purchase Price',
        places=2,
        validators=[NumberRange(min=0), Optional()]
    )

    seriesId = IntegerField('Series ID', render_kw={'readonly': True})
    thumbnail = StringField('Thumbnail', render_kw={'readonly': True})
    originalIssue = IntegerField('Original Issue ID', render_kw={'readonly': True})

    isVariant = SelectField(
        'Is this comic a variant?',
        choices=[("Yes", "Yes"), ("No", "No")],
        validators=[Optional()]
    )

    isPurchased = SelectField(
        'Do you own this comic?',
        choices=[('Yes', "Yes"), ('No', "No")],
        validators=[Optional()],
        render_kw={'onchange': "isPurchasedChanged()"}
    )

    comicId = HiddenField()

    purchaseDate = DateField(
        'Purchased Date',
        validators=[InputRequired()]
    )

    purchasePrice = DecimalField(
        'Purchased Price',
        places=2,
        validators=[NumberRange(min=0), InputRequired()]
    )

    purchaseType = SelectField(
        'Purchase Format',
        choices=[('Comic', "Comic"), ('Digital', "Digital")],
        validators=[InputRequired()]
    )

    submitBtn = SubmitField('Submit')
