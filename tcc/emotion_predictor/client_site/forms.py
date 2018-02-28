from django import forms

class VideoForm(forms.Form):
    video_url = forms.CharField(label='Video URL', max_length=1000)

class FileUploadForm(forms.Form):
    file_source = forms.FileField()
