
from django.db import models
from django.contrib.auth.models import User

class Todo(models.Model):
    """ Database model for the Todo table. This application only uses a single
        table. """

    title = models.CharField(max_length=100)
    memo = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    datecompleted = models.DateTimeField(null=True, blank=True)
    important = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        """ Ensure that something sensible is displayed on the Admin screen. """

        return self.title