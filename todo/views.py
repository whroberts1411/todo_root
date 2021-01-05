
#--------------------------------------------------------------------------------------------------
# Bill Roberts - December 2020 to January 2021
#
# A website to store and manage todo lists for registered users. The site includes a
# comprehensive set of authentication screens to allow users to register, log in and
# log out. The site is styled with Bootstrap, and includes a top navigation bar with
# contents that is responsive to screen size and orientation.
#--------------------------------------------------------------------------------------------------

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TodoForm
from .models import Todo
from django.utils import timezone

#--------------------------------------------------------------------------------------------------

def home(request):
    """ Display the home screen. """

    return render(request, 'todo/home.html')

#--------------------------------------------------------------------------------------------------

def signupuser(request):
    """ For a new user, display a standard Django registration form. """

    # On initial screen display, show the blank registration form.
    if request.method == 'GET':
        return render(request, 'todo/signupuser.html', {'form':UserCreationForm()})
    else:
        # If the passwords match, continue with other checks.
        if request.POST['password1'] == request.POST['password2']:
            try:
                # Attempt to create a new user, using the credentials supplied
                # by the user.
                user = User.objects.create_user(request.POST['username'],
                                    password = request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currenttodos')
            except IntegrityError:
                # Signup failed, as the supplied username already exists.
                return render(request, 'todo/signupuser.html', {'form':UserCreationForm(),
                        'error':'That username already exists - please choose another'})
        else:
            return render(request, 'todo/signupuser.html', {'form':UserCreationForm(),
                                                    'error':'Passwords did not match'})

#--------------------------------------------------------------------------------------------------

def logoutuser(request):
    """ Log the current user out. """

    if request.method == 'POST':
        logout(request)
        return redirect('home')

#--------------------------------------------------------------------------------------------------

def loginuser(request):
    """ Allow a user to log in, using a standard Django authentication form. """

    # On initial display of the screen, display the empty login form.
    if request.method == 'GET':
        return render(request, 'todo/loginuser.html', {'form':AuthenticationForm()})
    else:
        # Authenticate the user with their username and password.
        user = authenticate(request, username=request.POST['username'],
                                    password=request.POST['password'])
        # Either return an error message if credentials don't match, or login
        # the user if they do match.
        if user == None:
            return render(request, 'todo/loginuser.html', {'form':AuthenticationForm(),
                                    'error':'Username and password did not match'})
        else:
            login(request, user)
            return redirect('currenttodos')

#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------

def currenttodos(request):
    """ Display a list of all current Todos for the logged in user. """

    # If not correctly logged in, exit with n error message.
    if not request.user.is_authenticated:
        return render(request, 'todo/home.html', {'error':'You need to log in first!'})

    # only return records for the logged in user that have not been completed.
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=True)
    #request.session['todos'] = todos
    return render(request, 'todo/currenttodos.html', {'todos':todos})

#--------------------------------------------------------------------------------------------------

def createtodo(request):
    """ Create a new Todo record. Check that there is an authenticated user logged
        in before continuing. If so, get the new details and write them to the
        database. """

    # Check if the user is logged in. If not, return an error message.
    if not request.user.is_authenticated:
        return render(request, 'todo/home.html', {'error':'You need to log in first!'})

    # Display the appropriate empty form on first display of the screen.
    if request.method == "GET":
        return render(request, 'todo/createtodo.html', {'form':TodoForm()})
    else:
        # New details have been returned (POST), so write them to the database
        # after adding the user's id to the new record.
        try:
            form = TodoForm(request.POST)
            newtodo = form.save(commit=False)
            newtodo.user = request.user
            newtodo.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/createtodo.html', {'form':TodoForm(),
                            'error':'Invalid values entered - try again'})

#--------------------------------------------------------------------------------------------------

def viewtodo(request, todo_pk):
    """ Retrieve and display the Todo record with primary key of todo_pk  """

    # In case the url has been modified by the user, check that the pk exists
    # and the indexed record belongs to the current user.
    try:
        todo = Todo.objects.get(id=todo_pk, user=request.user)
    except Exception as ex:
       return render(request, 'todo/viewtodo.html', {
            'error':'No records returned - invalid record or user id'})

    # Initial request to display the populated form, with the requested Todo.
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form})
    else:
        # The form has been returned modified (POST) so write the updated
        # details to the database.
        try:
            form = TodoForm(request.POST, instance=todo)
            form.save()
            return redirect('currenttodos')
        except ValueError:
            return render(request, 'todo/viewtodo.html', {'todo':todo, 'form':form,
                                    'error':'Invalid values entered'})

#--------------------------------------------------------------------------------------------------

def completetodo(request, todo_pk):
    """ Complete the selected todo by setting the completion date to the current date
        and time. """

    # In case the url has been modified by the user, check that the pk exists
    # and the indexed record belongs to the current user.
    try:
        todo = Todo.objects.get(id=todo_pk, user=request.user)
    except Exception as ex:
       return render(request, 'todo/viewtodo.html', {
            'error':'No records returned - invalid record or user id'})

    # Still here, so ok to complete the todo.
    if request.method == 'POST':
        todo.datecompleted = timezone.now()
        todo.save()
        return redirect('currenttodos')

#--------------------------------------------------------------------------------------------------

def deletetodo(request, todo_pk):
    """ Delete the selected todo. This will remove it completely from the database. """

    # In case the url has been modified by the user, check that the pk exists
    # and the indexed record belongs to the current user.
    try:
        todo = Todo.objects.get(id=todo_pk, user=request.user)
    except Exception as ex:
       return render(request, 'todo/viewtodo.html', {
            'error':'No records returned - invalid record or user id'})

    # Still here, so ok to delete the todo.
    if request.method == 'POST':
        todo.delete()
        return redirect('currenttodos')

#--------------------------------------------------------------------------------------------------

def completedtodos(request):
    """ Display a list of all completed Todos for the logged in user. """

    # If not correctly logged in, exit with n error message.
    if not request.user.is_authenticated:
        return render(request, 'todo/home.html', {'error':'You need to log in first!'})

    # only return records for the logged in user that have been completed.
    todos = Todo.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'todo/completedtodos.html', {'todos':todos})

#--------------------------------------------------------------------------------------------------

def viewcomplete(request, todo_pk):
    """ Retrieve and display the completed Todo record with primary key of todo_pk  """

    # In case the url has been modified by the user, check that the pk exists
    # and the indexed record belongs to the current user.
    try:
        todo = Todo.objects.get(id=todo_pk, user=request.user)
    except Exception as ex:
       return render(request, 'todo/viewcomplete.html', {
            'error':'No records returned - invalid record or user id'})

    # Initial request to display the populated form, with the requested Todo.
    if request.method == 'GET':
        form = TodoForm(instance=todo)
        return render(request, 'todo/viewcomplete.html', {'todo':todo, 'form':form})
    else:
        # The form has been returned modified (POST) so reset the completed
        # date to NULL and write to the database.
        try:
            todo.datecompleted = None
            todo.save()
            return redirect('completedtodos')
        except ValueError:
            return render(request, 'todo/viewcomplete.html', {'todo':todo, 'form':form,
                                    'error':'Invalid values entered'})

#--------------------------------------------------------------------------------------------------


#--------------------------------------------------------------------------------------------------
