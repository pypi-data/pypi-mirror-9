from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.views import generic
from django.core.urlresolvers import reverse

from datetime import datetime, timedelta, time
from tasksoftheday.models import Task

# Create your views here.
#def index(request):
#    latest_tasks_list = Task.objects.order_by('due_date')[:5]
#    context = {'latest_tasks_list': latest_tasks_list}    
#    
#    return render(request, 'tasksoftheday/index.html', context)
#
#def task(request, task_id):
#    task = get_object_or_404(Task, pk=task_id)
#    context = {'task' : task}
#    return render(request, 'tasksoftheday/task.html', context)

class TaskView(generic.DetailView):
    model = Task
    template_name = 'tasksoftheday/task.html'
    

class IndexView(generic.ListView):
    model = Task
    template_name = 'tasksoftheday/index.html'
    context_object_name = 'task_lists'

    def get_queryset(self):
        # TODO: cleanup!
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        tomorrow_start = datetime.combine(tomorrow, time())
        #aktuell: 2015-03-27 18:48
        #2015-03-27
        #2015-03-28
        #2015-03-27 00:00:00
        #2015-03-28 00:00:00
        aftertomorrow_start = datetime.combine(tomorrow + timedelta(1), time())
        yesterday_start = datetime.combine(today - timedelta(1), time())

        tasks_yeste = Task.objects.filter(due_date__gte=yesterday_start, due_date__lte=today_start).order_by("-due_date")    
        tasks_today = Task.objects.filter(due_date__gte=today_start, due_date__lte=tomorrow_start).order_by("-due_date")
        tasks_tomor = Task.objects.filter(due_date__gte=tomorrow_start, due_date__lte=aftertomorrow_start).order_by("-due_date")
        # TODO: named tuple?
        return [tasks_yeste, tasks_today, tasks_tomor]
        #return Task.objects.order_by('due_date')[:50]

class TaskListView(generic.ListView):
    """used for past and future tasks list"""

    model = Task
    template_name = 'tasksoftheday/tasklist.html'
    context_object_name = 'task_list'
    

    def get_queryset(self):
        past_or_future = self.kwargs['past_or_future']
        today = datetime.now().date()        

        if past_or_future == 'past':
            today_start = datetime.combine(today, time())
            return Task.objects.filter(due_date__lte=today_start).order_by("-due_date")
        elif past_or_future == 'future':
            today_end = datetime.combine(today + timedelta(1), time())
            return Task.objects.filter(due_date__gte=today_end).order_by("-due_date")
        else:
            raise Http404(self.past_or_future)
        
def createTask(request):
    task_text = request.POST["newtask_text"]
    is_done = False
    created_date = datetime.now()
    duedate_from_request = request.POST["newtask_duedate"]
    duedate_from_request += " 16:00"  # am anfang erstmal alle um 16 uhr später vllt erweitern auf uhrzeiten
    newTask = Task(task_text=task_text, is_done=is_done, created_date=created_date, due_date=duedate_from_request)
    
    #save new task to db
    newTask.save()

    return HttpResponseRedirect(reverse('tasksoftheday:index', args=()))

def flip_task_done_status(request, task_id):
    task = Task.objects.get(pk=task_id)
    task.is_done = not(task.is_done)
    task.save()
    return HttpResponseRedirect(reverse('tasksoftheday:index', args=()))
