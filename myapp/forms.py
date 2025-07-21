from django import forms

class CSVFileUploadForm1(forms.Form):
    files = forms.FileField(widget=forms.ClearableFileInput(), required=False)
    files.widget.attrs.update({'multiple': True})

    def clean_files(self):
        files = self.cleaned_data.get('files')
        if not files:
            raise forms.ValidationError('Please upload at least one file.')
        return files   
    

class ExcelUploadForm(forms.Form):
    mapping_file = forms.FileField(
        label='Upload Mapping Excel File',
        widget=forms.FileInput(attrs={'accept': '.xlsx'}),
        help_text='Only Excel files are accepted.'
    )

class CSVFileUploadForm(forms.Form):
    premium_file = forms.FileField(
        label='Upload Premium CSV File',
        widget=forms.FileInput(attrs={'accept': '.csv'}),
        help_text='Only CSV files are accepted.'
    )
