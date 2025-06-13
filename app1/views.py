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



from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm

def edit_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = ProjectForm(instance=project)
        return render(request, 'project.html', {'edit_form': form, 'project_id': pk})
    

from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from .models import Project

@require_POST
def delete_project(request, pk):
    try:
        project = Project.objects.get(pk=pk)
        project.delete()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'})




from django.shortcuts import render
from django.http import JsonResponse
from .models import Transaction, BillProof, PaymentProof, Category, Project
from .forms import TransactionForm
from django.shortcuts import render
from .models import Transaction, Project, Category
from django.utils.dateparse import parse_date
from datetime import datetime

def transaction_list(request):
    transactions = Transaction.objects.all().select_related('project')
    projects = Project.objects.all()
    categories = Category.objects.all()

    # Get filter parameters from GET
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project_id = request.GET.get('project')
    txn_type = request.GET.get('type')
    category = request.GET.get('category')

    # Create a dictionary to retain selected filters in the template
    selected = {
        'start_date': start_date or '',
        'end_date': end_date or '',
        'project': project_id or 'all',
        'type': txn_type or 'all',
        'category': category or '',
    }

    # Apply filters
    if start_date:
        transactions = transactions.filter(created_at__date__gte=parse_date(start_date))

    if end_date:
        transactions = transactions.filter(created_at__date__lte=parse_date(end_date))

    if project_id and project_id != 'all':
        try:
            transactions = transactions.filter(project__id=int(project_id))
        except ValueError:
            pass  # Ignore invalid project_id

    if txn_type and txn_type != 'all':
        transactions = transactions.filter(type=txn_type)

    if category:
        transactions = transactions.filter(category__icontains=category)

    return render(request, 'transaction.html', {
        'transactions': transactions,
        'projects': projects,
        'categories': categories,
        'selected': selected,
    })


def add_transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        # file_form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save()

            # Bill Proofs
            for f in request.FILES.getlist('bill_proofs'):
                BillProof.objects.create(transaction=transaction, file=f)

            # Payment Proofs
            for f in request.FILES.getlist('payment_proofs'):
                PaymentProof.objects.create(transaction=transaction, file=f)

            return JsonResponse({'success': True})
        else:
            print(form.errors, request.POST, request.FILES)
            return JsonResponse({'success': False, 'errors': form.errors})
    return JsonResponse({'success': False, 'message': 'Invalid request'})



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Staff, Project,Loan
from .forms import StaffForm,LoanForm

# List & Add Staff View
def staff_list(request):
    staff_list = Staff.objects.all()
    project_list = Project.objects.all()

    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member added successfully.")
            return redirect('staff_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = StaffForm()

    context = {
        'staff_list': staff_list,
        'project_list': project_list,
        'form': form,
    }
    return render(request, 'staff_list.html', context)


# Delete View
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    staff.delete()
    messages.success(request, "Staff member deleted successfully.")
    return redirect('staff_list')


# Optional: Edit View
def staff_edit(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, request.FILES, instance=staff)
        if form.is_valid():
            form.save()
            messages.success(request, "Staff member updated successfully.")
            return redirect('staff_list')
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = StaffForm(instance=staff)

    context = {
        'form': form,
        'staff': staff,
    }
    return render(request, 'staff_edit.html', context)




from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Loan
from .forms import LoanForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from decimal import Decimal
# List view for Loan Management
def loan_list(request):
    loans = Loan.objects.select_related('project').all()
    form = LoanForm()

    # Example calculations (replace with actual fields if available)
    total_loaned_amount = loans.aggregate(total=Sum('amount'))['total'] or 0

    # Placeholder logic: assuming total repaid and interest collected are stored separately
    total_principal_repaid = 921.04  # Replace with actual logic or aggregate field
    total_interest_collected = 78.96
    total_outstanding = total_loaned_amount - Decimal(total_principal_repaid)


    context = {
        'loans': loans,
        'form': form,
        'total_loaned_amount': total_loaned_amount,
        'total_principal_repaid': total_principal_repaid,
        'total_interest_collected': total_interest_collected,
        'total_outstanding': total_outstanding,
    }
    return render(request, 'loan.html', context)

# Create Loan
def create_loan(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('loan_list')
    return redirect('loan_list')

# Update Loan
def update_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            return redirect('loan_list')
    return redirect('loan_list')

# Delete Loan (via AJAX)
@csrf_exempt
def delete_loan(request):
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        loan = get_object_or_404(Loan, id=loan_id)
        loan.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'message': 'Invalid request'}, status=400)
