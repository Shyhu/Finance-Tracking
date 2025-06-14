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



# app1/views.py

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Staff, Project
from .forms import StaffForm

def staff_list(request):
    staff_list = Staff.objects.all()
    project_list = Project.objects.all()
    form = StaffForm()

    if request.method == 'POST':
        if 'add_staff' in request.POST:
            form = StaffForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Staff added successfully.")
                return redirect('staff_list')
            else:
                messages.error(request, "Error adding staff.")

        elif 'edit_staff' in request.POST:
            staff_pk = request.POST.get('staff_pk')
            staff_obj = get_object_or_404(Staff, id=staff_pk)
            form = StaffForm(request.POST, request.FILES, instance=staff_obj)
            if form.is_valid():
                form.save()
                messages.success(request, "Staff updated successfully.")
                return redirect('staff_list')
            else:
                messages.error(request, "Error updating staff.")

    return render(request, 'staff_list.html', {
        'staff_list': staff_list,
        'project_list': project_list,
        'form': form,
    })





# def view_staff(request, pk):
#     staff = get_object_or_404(Staff, pk=pk)
#     files = staff.files.all()
#     return render(request, 'staff_detail.html', {'staff': staff, 'files': files})




def delete_staff(request, staff_id):
    staff = get_object_or_404(Staff, id=staff_id)
    staff.delete()
    messages.success(request, "Staff member deleted.")
    return redirect('staff_list')






from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Loan
from .forms import LoanForm
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from decimal import Decimal
#from django.db.models import Sum
from decimal import Decimal
from .models import Loan, Repayment
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal
from django.db.models import Sum
from .models import Loan, Repayment
from .forms import LoanForm
from django.shortcuts import render, get_object_or_404, redirect
from decimal import Decimal
from .models import Loan, Repayment
from .forms import LoanForm
from django.db.models import Sum
from django.http import JsonResponse
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import render
from .models import Loan, Repayment
from .forms import LoanForm

def loan_list(request): 
    loans = Loan.objects.select_related('project').all()
    form = LoanForm()

    total_loaned_amount = loans.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_principal_repaid = Repayment.objects.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
    total_interest_collected = Repayment.objects.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
    total_outstanding = total_loaned_amount - total_principal_repaid

    for loan in loans:
        # Attach edit form to each loan
        loan.get_form = LoanForm(instance=loan)

        # Calculate totals per loan
        loan.total_interest_paid = loan.repayments.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
        total_principal = loan.repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
        loan.remaining_balance = loan.amount - total_principal

    context = {
        'loans': loans,
        'form': form,
        'total_loaned_amount': total_loaned_amount,
        'total_principal_repaid': total_principal_repaid,
        'total_interest_collected': total_interest_collected,
        'total_outstanding': total_outstanding,
    }
    return render(request, 'loan.html', context)


def create_loan(request):
    if request.method == 'POST':
        form = LoanForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('loan_list')

def update_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        form = LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
    return redirect('loan_list')

def delete_loan(request):
    if request.method == 'POST':
        loan_id = request.POST.get('loan_id')
        try:
            loan = Loan.objects.get(id=loan_id)
            loan.delete()
            return JsonResponse({'success': True})
        except Loan.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Loan not found'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})



# views.py
from django.shortcuts import render, get_object_or_404
from .models import Loan,Repayment  # Assuming Repayment model exists
# views.py
from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from .models import Loan, Repayment
from .forms import RepaymentForm
from django.db.models import Sum
from django.db.models import Sum, Q
from django.utils.dateparse import parse_date
from django.http import HttpResponse
from .utils import generate_loan_pdf  # PDF generator utility



def loan_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    repayments = loan.repayments.all().order_by('date')
    repayment_form = RepaymentForm()

    repayments_data = []
    remaining_balance = loan.amount

    for repayment in repayments:
        remaining_balance -= repayment.principal_paid or Decimal('0.00')
        repayments_data.append({
            'repayment': repayment,
            'balance_after': remaining_balance
        })

    # 🟦 Set default values for GET requests
    interest_paid = Decimal('0.00')
    principal_paid = Decimal('0.00')

    if request.method == 'POST':
        repayment_form = RepaymentForm(request.POST)
        if repayment_form.is_valid():
            repayment = repayment_form.save(commit=False)
            repayment.loan = loan

            total_interest_paid = loan.repayments.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
            total_principal_paid = loan.repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
            current_balance = loan.amount - total_principal_paid

            interest_calculated = (loan.interest_rate / Decimal('100.00')) * current_balance
            repayment.interest_calculated = interest_calculated

            amt = repayment.amount_paid
            if amt <= interest_calculated:
                repayment.interest_paid = amt
                repayment.principal_paid = Decimal('0.00')
            else:
                repayment.interest_paid = interest_calculated
                repayment.principal_paid = amt - interest_calculated

            repayment.balance_after_repayment = current_balance - repayment.principal_paid

            # 🟦 Set values for context after saving
            interest_paid = repayment.interest_paid
            principal_paid = repayment.principal_paid

            repayment.save()
            return redirect('loan_detail', loan_id=loan.id)

    # Totals
    total_interest_paid = repayments.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
    total_principal_paid = repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
    remaining_balance = loan.amount - total_principal_paid

    return render(request, 'loan_detail.html', {
        'loan': loan,
        'repayments': repayments,
        'repayment_form': repayment_form,
        'total_interest_paid': total_interest_paid,
        'total_principal_paid': total_principal_paid,
        'remaining_balance': remaining_balance,
        'interest_paid': interest_paid,  # 🟦 These two are now always defined
        'principal_paid': principal_paid,
    })



# from django.http import HttpResponse
# from .utils import generate_loan_pdf

# def loan_pdf(request, loan_id):
#     loan = get_object_or_404(Loan, pk=loan_id)
#     repayments = loan.repayments.all().order_by('date')
#     # Recalculate totals as in your view:
#     total_interest_paid = repayments.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
#     total_principal_paid = repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
#     remaining_balance = loan.amount - total_principal_paid

#     pdf_content = generate_loan_pdf(loan, repayments, total_interest_paid, total_principal_paid, remaining_balance)
#     if not pdf_content:
#         return HttpResponse("Error generating PDF", status=500)

#     response = HttpResponse(pdf_content, content_type='application/pdf')
#     fname = f"Loan_{loan_id}_summary.pdf"
#     response['Content-Disposition'] = f'attachment; filename="{fname}"'
#     return response


from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, TaskFile
from .forms import TaskForm
from django.forms.models import model_to_dict
def task_list(request):
    tasks = Task.objects.all().order_by('-date')

    if request.method == 'POST':
        # Add Task
        if 'add_task' in request.POST:
            form = TaskForm(request.POST)
            files = request.FILES.getlist('file')
            if form.is_valid():
                task = form.save()
                for f in files:
                    TaskFile.objects.create(task=task, file=f)
                return redirect('task_list')

        # Edit Task
        elif 'edit_task' in request.POST:
            task_id = request.POST.get('task_id_hidden')
            task = get_object_or_404(Task, id=task_id)
            prefix = f"task_{task.id}"
            form = TaskForm(request.POST, instance=task, prefix=prefix)
            if form.is_valid():
                form.save()
                return redirect('task_list')

    # Prepare form for Add Task
    form = TaskForm()

    # Create prefixed forms for edit modals
    for task in tasks:
        task.get_form = TaskForm(instance=task, prefix=f"task_{task.id}")

    return render(request, 'task.html', {'tasks': tasks, 'form': form})

def delete_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect('task_list')

def view_task(request, pk):
    task = get_object_or_404(Task, pk=pk)
    files = task.files.all()
    return render(request, 'task_detail.html', {'task': task, 'files': files})




from django.shortcuts import render
from .models import Project, Transaction, Staff, Loan, Repayment
from django.db.models import Sum

from django.shortcuts import render
from .models import Project, Transaction, Staff, Loan, Repayment
from django.db.models import Sum

def dashboard_view(request):
    total_projects = Project.objects.count()
    total_income = Transaction.objects.filter(type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_staff = Staff.objects.count()
    total_loan_amount = Loan.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_loan_repaid = Repayment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_outstanding_loan = total_loan_amount - total_loan_repaid

    # Bar chart data
    chart_labels = []
    chart_data = []
    projects = Project.objects.all()
    for project in projects:
        income = Transaction.objects.filter(project=project, type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = Transaction.objects.filter(project=project, type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
        profit = income - expense
        chart_labels.append(project.name)
        chart_data.append(profit)

    # Zip the labels and data to avoid using `zip` in template
    project_chart_data = list(zip(chart_labels, chart_data))

    context = {
        'total_projects': total_projects,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_staff': total_staff,
        'total_loan_amount': total_loan_amount,
        'total_loan_repaid': total_loan_repaid,
        'total_outstanding_loan': total_outstanding_loan,
        'project_chart_data': project_chart_data,
    }
    return render(request, 'dashboard_view.html', context)



from django.shortcuts import redirect
from .models import Category

def add_category(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            Category.objects.get_or_create(name=name)
    return redirect(request.META.get('HTTP_REFERER', '/'))
