from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("body",)
        widgets = {
            "body": forms.TextInput(
                attrs={
                    "type": "input",
                    "class": "form-control",
                    "aria-describedby": "basic-addon3",
                    "placeholder": "comment body",
                }
            ),
        }
