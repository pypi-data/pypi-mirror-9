from wtforms.validators import Optional, ValidationError, StopValidation
import os

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
