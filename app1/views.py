from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Project
from .forms import ProjectForm

def base(request):
    return render(request,'base.html')

from django.shortcuts import render, redirect, get_object_or_404
from .models import Project
from .forms import ProjectForm
from django.shortcuts import render, redirect
from .models import Project
from .forms import ProjectForm

from django.http import JsonResponse

def project_list(request):
    projects = Project.objects.order_by('-id')
    form = ProjectForm()

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save()
            # Send new row data as JSON
            return JsonResponse({
                'id': project.id,
                'code': project.code,
                'name': project.name,
                'location': project.location,
                'budget': f"${project.total_budget:,.0f}",
                'start_date': project.start_date.strftime("%Y-%m-%d"),
                'end_date': project.end_date.strftime("%Y-%m-%d"),
                'notes': project.notes or ""
            })

        return JsonResponse({'errors': form.errors}, status=400)

    return render(request, 'project.html', {'projects': projects, 'form': form})




from django.shortcuts import render, get_object_or_404
from .models import Project

def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'project_detail.html', {'project': project})

