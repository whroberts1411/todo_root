
from django.contrib import admin
from .models import Todo

class TodoAdmin(admin.ModelAdmin):
    """ Set up values for a number of properties to alter the default behaviour
        of the standard Django admin screens. """
        
    readonly_fields = ('created', )
    list_display = ('title', 'created', 'user')
    ordering = ('-created', 'user')
    search_fields = ('title', 'memo')

admin.site.register(Todo, TodoAdmin)
