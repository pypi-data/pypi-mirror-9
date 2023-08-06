from wtforms.validators import Optional, ValidationError, StopValidation
from wtforms import DateTimeField
import os
import datetime

class RequireItemAsMember(object):
    """
    Ignores validation if a file is not provided.
    :param item: The item to check if that form data contains.
    :param message: The message to show upon error
    :throws ValidationError: ValidationError if the current user
                             is not in the data
    """
    def __init__(self, item, 
        message='A required item did not exist in your selection'):
        self.message = message
        self.item = item

    def __call__(self, form, field):
        if not self.item in field.data:
            raise ValidationError(self.message)



class ValidFileFormat(Optional):
    """
    Determines whether or not a file is valid for uploading
    by checking with flask-uploads.

    :throws ValidationError: ValidationError if the uploaded data is not valid.

    :param fileupload:  a FileUpload object from flask-uploads
    :param message: message to display upon validation error.
    """

    def __init__(self, fileupload, *args, **kwargs):
        self.fileupload = fileupload
        self.message = 'The selected file cannot be uploaded. Only %s are allowed.' % (
                ', '.join([t.lower() for t in fileupload._config.allow])
            )
        if 'message' in kwargs:
            self.message = kwargs['message']

    def __call__(self, form, field):
        filename, extension = os.path.splitext(field.data.filename)
        if not self.fileupload.extension_allowed(extension[1:].lower()):
            raise ValidationError(self.message)

class StopIfEqualTo(object):
    """
    A validator for WTForms which will stop validating 
    if the field data is equal to the getter function passed
    as a parameter.

    :throws StopValidation: StopValidation if the field value is equal 
                            to the getter's returned value.
    
    :param getter: A function pointer which will be used to get
                   the value to compare.

    """
    def __init__(self, getter, *args, **kwargs):
        self.getter = getter

    def __call__(self, form, field):
        if field.data == self.getter():
            raise StopValidation()



class Unique(object):
    """
    Database Unique Validator for WTForms / SQLAlchemy.

    :throws ValidationError: ValidationError if the data already 
                             exists in the database for the specified field.

    :param model: SQL Alchemy ORM Model to target
    :param field: SQL Alchemy ORM Field to compare
                  ie, Model.field
    :param message: message to display upon validation error.
    """
    def __init__(self, model, field, *args, **kwargs):
        self.model = model
        self.field = field
        self.message = 'A record with this information already exists.'
        if 'message' in kwargs:
            self.message = kwargs['message']

    def __call__(self, form, field):
        if self.model.query.filter(self.field == field.data).count() > 0:
            raise ValidationError(self.message)


class OptionalFileField(Optional):
    """
    Ignores validation if a file is not provided.
    :throws StopValidation: StopValidation if a file is not provided.
    """

    def __call__(self, form, field):
        if field.data.filename == '':
            raise StopValidation()

class RequireAny(object):
    """
    Raise a Validation Error on the active field if none of the passed
    fields have data.

    :param fields: A list of (string) fields on the Form class to be 
                   included. 
    :param message: The message to show to the user upon failure
    :param errors_on_all: Show the error message on all the specified fields
    """
    def __init__(self, fields, message, errors_on_all=True):

        self.fields = fields
        self.message = message
        self.errors_on_all = errors_on_all

    def __call__(self, form, field):
        if field.data:
            return True

        for fieldname in self.fields:
            field = getattr(form, fieldname)
            print(field.data)
            if field.data:
                return True
            elif self.errors_on_all:
                field.errors.append(self.message)

        raise ValidationError(self.message)


def empty_string_none(string):
    """
    A Wtforms filter which will turn an empty string into a Nonetype.
    """
    return string or None



class TimezoneDateTimeField(DateTimeField):
    """
    A Timezone aware field for WTForms. 
    Define a field in your form and declare it with tzfield='variable_name'
    The timezone field on the client should have the value of:
        new Date().getTimezoneOffset();

    This is a offset in minutes from UTC. (-ve means ahead of UTC, 
    +ve means behind UTC)

    :param tzfield: The name (as a string) of the variable which containes the 
                    getTimezoneOffset() value.
    """

    def __init__(self, label=None, validators=None, tzfield=None, format='%Y-%m-%d %H:%M:%S' ,**kwargs):
        self.format = format
        self.tzfield = tzfield
        self._form = kwargs.get('_form')

        super(TimezoneDateTimeField, self).__init__(label, validators, format, **kwargs)

    def process_formdata(self, valuelist):
        print("PROCESSING FORM DATA")
        
        if valuelist:
            format = self.format
            date_str = ' '.join(valuelist)

            if self.tzfield:
                format = self.format + ' %z'
                tzoffset = int(getattr(self._form, self.tzfield).data) * -1
                tz = "{0:+02d}{1:02d}".format(int(tzoffset/60), tzoffset % 60)
                date_str = date_str + ' {}'.format(tz)

                print(format)
                print(date_str)

            try:
                self.data = datetime.datetime.strptime(date_str, format)
            except ValueError:
                self.data = None
                raise ValueError(self.gettext('Not a valid datetime value'))


