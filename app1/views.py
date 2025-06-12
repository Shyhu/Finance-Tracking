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



from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


@csrf_exempt
def project_update_ajax(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        project.name = request.POST.get('name')
        project.location = request.POST.get('location')
        project.total_budget = request.POST.get('total_budget')
        project.start_date = request.POST.get('start_date')
        project.end_date = request.POST.get('end_date')
        project.notes = request.POST.get('notes')
        project.save()
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request'}, status=400)




from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TransactionForm, FileUploadForm
from .models import BillProof, PaymentProof

def add_transaction(request):
    if request.method == 'POST':
        t_form = TransactionForm(request.POST)
        f_form = FileUploadForm(request.POST, request.FILES)

        if t_form.is_valid() and f_form.is_valid():
            transaction = t_form.save()

            for file in request.FILES.getlist('bill_proofs'):
                BillProof.objects.create(transaction=transaction, file=file)

            for file in request.FILES.getlist('payment_proofs'):
                PaymentProof.objects.create(transaction=transaction, file=file)

            messages.success(request, 'Transaction added successfully!')
            return redirect('transaction')
    else:
        t_form = TransactionForm()
        f_form = FileUploadForm()

    return render(request, 'transaction.html', {'t_form': t_form, 'f_form': f_form})




from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Transaction, BillProof, PaymentProof
from .forms import TransactionForm, FileUploadForm

def transaction_list(request):
    transactions = Transaction.objects.select_related('project').all()
    return render(request, 'transaction.html', {'transactions': transactions})

def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        file_form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid() and file_form.is_valid():
            transaction = form.save()

            # Bill Proofs
            for f in request.FILES.getlist('bill_proofs'):
                BillProof.objects.create(transaction=transaction, file=f)

            # Payment Proofs
            for f in request.FILES.getlist('payment_proofs'):
                PaymentProof.objects.create(transaction=transaction, file=f)

            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'})
