from django import forms


class AnalysisUploadForm(forms.Form):
    title = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'e.g., Senior Full Stack Python Developer'
        }),
        label="Job Title / Role"
    )

    resume_file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-file-input',
            'accept': '.pdf,.docx,.doc'
        }),
        label="Upload Resume (PDF or DOCX)"
    )

    jd_text = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'form-textarea',
            'rows': 8,
            'placeholder': 'Paste the full job description requirements, qualifications, and responsibilities here...'
        }),
        label="Job Description"
    )

    def clean_resume_file(self):
        f = self.cleaned_data.get('resume_file')
        if f:
            ext = f.name.lower().split('.')[-1]
            if ext not in ['pdf', 'docx', 'doc']:
                raise forms.ValidationError("Please upload a valid PDF or Word (.docx) document.")
            if f.size > 10 * 1024 * 1024:
                raise forms.ValidationError("File size exceeds 10MB limit. Please upload a smaller file.")
        return f

    def clean_jd_text(self):
        text = self.cleaned_data.get('jd_text', '').strip()
        if len(text) < 30:
            raise forms.ValidationError("Please provide a detailed job description (minimum 30 characters).")
        return text
