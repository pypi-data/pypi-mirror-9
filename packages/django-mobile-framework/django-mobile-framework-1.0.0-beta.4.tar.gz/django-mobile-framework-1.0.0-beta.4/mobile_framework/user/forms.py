from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.utils.translation import ugettext_lazy as _

User = get_user_model()


class UserCreationForm(forms.ModelForm):
    """ Custom User Creation From for our custom model. """
    password1 = forms.CharField(label=_(u'Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_(u'Password Confirmation'), widget=forms.PasswordInput)

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = ('username', 'email')


class UserChangeForm(forms.ModelForm):
    """ Custom User Change Form for our custom model. """
    password = ReadOnlyPasswordHashField()

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

    class Meta:
        model = User
        fields = '__all__'
