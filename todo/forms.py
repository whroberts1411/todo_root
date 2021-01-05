
from django.forms import ModelForm
from .models import Todo

class TodoForm(ModelForm):
    """ A user-defined form to enter new Todo details. Note that some of the
        Todo fields are not relevent/required for a new record.  """

    class Meta:
        model = Todo
        fields = ['title', 'memo', 'important']
