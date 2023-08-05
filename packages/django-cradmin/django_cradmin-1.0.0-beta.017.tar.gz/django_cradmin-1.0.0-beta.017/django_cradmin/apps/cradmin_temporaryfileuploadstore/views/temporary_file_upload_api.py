import json
import mimetypes
from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.views.generic import FormView
from django.utils.translation import ugettext_lazy as _

from django import forms
from multiupload.fields import MultiFileField
from django_cradmin.apps.cradmin_temporaryfileuploadstore.models import TemporaryFileCollection, TemporaryFile, \
    html_input_accept_match, make_unique_filename


class FileUploadForm(forms.Form):
    file = MultiFileField(
        max_file_size=1000000 * getattr(settings, 'CRADMIN_TEMPORARYFILEUPLOADSTORE_MAX_FILE_SIZE_MB', 1000))
    collectionid = forms.IntegerField(
        required=False)
    minutes_to_live = forms.IntegerField(
        min_value=1,
        required=False)
    mode = forms.ChoiceField(
        required=False,
        choices=[
            (None, 'Multifile'),
            ('singlefile', 'Single file')
        ]
    )
    accept = forms.CharField(required=False)
    max_filename_length = forms.IntegerField(min_value=0, required=False)
    unique_filenames = forms.BooleanField(required=False)


class FileDeleteForm(forms.Form):
    collectionid = forms.IntegerField(required=True)
    temporaryfileid = forms.IntegerField(required=True)


class UploadTemporaryFilesView(FormView):
    form_class = FileUploadForm
    http_method_names = ['post', 'delete']

    def create_collection(self, minutes_to_live, accept, max_filename_length, unique_filenames):
        collection = TemporaryFileCollection(
            user=self.request.user)
        if minutes_to_live is not None:
            collection.minutes_to_live = minutes_to_live
        if accept is not None:
            collection.accept = accept
        if max_filename_length:
            collection.max_filename_length = max_filename_length
        if unique_filenames:
            collection.unique_filenames = unique_filenames
        collection.full_clean()
        collection.save()
        return collection

    def get_existing_collection(self, collectionid):
        return TemporaryFileCollection.objects.filter(user=self.request.user).get(id=collectionid)

    def create_or_get_collection_id(self, collectionid, minutes_to_live, accept,
                                    max_filename_length, unique_filenames):
        if collectionid is None:
            return self.create_collection(
                minutes_to_live=minutes_to_live,
                accept=accept,
                max_filename_length=max_filename_length,
                unique_filenames=unique_filenames)
        else:
            return self.get_existing_collection(collectionid)

    def save_uploaded_file(self, collection, formfile, mode, filename_set):
        if mode == 'singlefile':
            collection.clear_files()

        filename = formfile.name
        if collection.unique_filenames:
            filename = make_unique_filename(
                filename_set=filename_set,
                wanted_filename=filename,
                max_filename_length=collection.max_filename_length)
            filename_set.add(filename)
        temporaryfile = TemporaryFile(collection=collection, filename=filename)
        temporaryfile.file.save(formfile.name, formfile, save=False)
        temporaryfile.full_clean()
        temporaryfile.save()
        return temporaryfile

    def form_invalid(self, form):
        return self.__invalid_form_response(form)

    def everything_valid(self, collection, form):
        uploadedfiles_data = []
        filename_set = None
        if collection.unique_filenames:
            filename_set = collection.get_filename_set()
        for formfile in form.cleaned_data['file']:
            temporaryfile = self.save_uploaded_file(
                collection=collection,
                formfile=formfile,
                mode=form.cleaned_data['mode'],
                filename_set=filename_set)
            uploadedfiles_data.append({
                'id': temporaryfile.id,
                'filename': temporaryfile.filename,
                'mimetype': temporaryfile.mimetype
            })
        return self.json_response(json.dumps({
            'collectionid': collection.id,
            'temporaryfiles': uploadedfiles_data
        }))

    def validate_all_files(self, accept, form):
        if not accept:
            return
        for formfile in form.cleaned_data['file']:
            if not html_input_accept_match(
                    accept=accept,
                    mimetype=mimetypes.guess_type(formfile.name)[0],
                    filename=formfile.name):
                raise ValidationError(
                    _('%(filename)s: Unsupported filetype.') % {'filename': formfile.name},
                    code='unsupported_mimetype')

    def form_valid(self, form):
        collectionid = form.cleaned_data['collectionid']
        minutes_to_live = form.cleaned_data['minutes_to_live']
        accept = form.cleaned_data['accept']
        max_filename_length = form.cleaned_data['max_filename_length']
        unique_filenames = form.cleaned_data['unique_filenames']
        try:
            self.validate_all_files(accept=accept, form=form)
        except ValidationError as e:
            return self.json_response(json.dumps({
                'file': [
                    {
                        'message': e.message,
                        'code': e.code
                    }
                ]
            }), status=400)
        else:
            try:
                collection = self.create_or_get_collection_id(
                    collectionid=collectionid,
                    minutes_to_live=minutes_to_live,
                    accept=accept,
                    max_filename_length=max_filename_length,
                    unique_filenames=unique_filenames)
            except TemporaryFileCollection.DoesNotExist:
                return self.__collection_does_not_exist_response(collectionid)
            else:
                return self.everything_valid(collection=collection, form=form)

    def json_response(self, data, status=200):
        return HttpResponse(
            data,
            content_type='application/json',
            status=status)

    def __collection_does_not_exist_response(self, collectionid):
        return self.json_response(json.dumps({
            'collectionid': [
                {
                    'message': 'Collection with id={} does not exist.'.format(collectionid),
                    'code': 'doesnotexist'
                }
            ]
        }), status=404)

    def __temporaryfile_does_not_exist_response(self, temporaryfileid):
        return self.json_response(json.dumps({
            'temporaryfileid': [
                {
                    'message': 'Temporary file with id={} does not exist.'.format(temporaryfileid),
                    'code': 'doesnotexist'
                }
            ]
        }), status=404)

    def __invalid_form_response(self, form):
        return self.json_response(form.errors.as_json(), status=400)

    def delete(self, request, *args, **kwargs):
        try:
            requestdata = json.loads(self.request.body)
        except ValueError:
            return self.json_response(json.dumps({
                'errormessage': 'Invalid JSON data in the request body.'
            }), status=400)

        form = FileDeleteForm(requestdata)
        if form.is_valid():
            collectionid = form.cleaned_data['collectionid']
            temporaryfileid = form.cleaned_data['temporaryfileid']
            try:
                collection = self.get_existing_collection(collectionid)
            except TemporaryFileCollection.DoesNotExist:
                return self.__collection_does_not_exist_response(collectionid)
            else:
                try:
                    temporaryfile = collection.files.get(id=temporaryfileid)
                except TemporaryFile.DoesNotExist:
                    return self.__temporaryfile_does_not_exist_response(temporaryfileid)
                else:
                    return self.perform_temporaryfile_delete(temporaryfile)
        else:
            return self.__invalid_form_response(form)

    def perform_temporaryfile_delete(self, temporaryfile):
        temporaryfileid = temporaryfile.id
        temporaryfile.delete_object_and_file()
        return self.json_response(json.dumps({
            'collectionid': temporaryfile.collection_id,
            'temporaryfileid': temporaryfileid
        }))
