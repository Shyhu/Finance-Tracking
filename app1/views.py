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
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm
from django.shortcuts import render

def project_list(request):
    projects = Project.objects.order_by('-id')
    form = ProjectForm()

    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        form = ProjectForm(request.POST)
        if form.is_valid():
            # Auto-generate the code
            last_project = Project.objects.order_by('-id').first()
            if last_project and last_project.code.startswith('PRJ'):
                last_num = int(last_project.code.replace('PRJ', ''))
            else:
                last_num = 0
            new_code = f"PRJ{last_num + 1:03d}"

            project = form.save(commit=False)
            project.code = new_code
            project.save()

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

from django.db.models import Sum, Count

def transaction_list(request):
    transactions = Transaction.objects.all().select_related('project')
    projects = Project.objects.all()
    categories = Category.objects.all()

    # Filters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project_id = request.GET.get('project')
    txn_type = request.GET.get('type')
    category = request.GET.get('category')

    selected = {
        'start_date': start_date or '',
        'end_date': end_date or '',
        'project': project_id or 'all',
        'type': txn_type or 'all',
        'category': category or '',
    }

    if start_date:
        transactions = transactions.filter(created_at__date__gte=parse_date(start_date))
    if end_date:
        transactions = transactions.filter(created_at__date__lte=parse_date(end_date))
    if project_id and project_id != 'all':
        try:
            transactions = transactions.filter(project__id=int(project_id))
        except ValueError:
            pass
    if txn_type and txn_type != 'all':
        transactions = transactions.filter(type=txn_type)
    if category:
        transactions = transactions.filter(category__icontains=category)

    # Summary stats
    # total_income = transactions.filter(type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    # total_expense = transactions.filter(type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_income = transactions.filter(type__iexact='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = transactions.filter(type__iexact='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_amount = transactions.aggregate(Sum('amount'))['amount__sum'] or 0
    total_transactions = transactions.count()
    total_pending = transactions.filter(status__iexact='Pending').count()     # case-insensitive
    total_approved = transactions.filter(status__iexact='Approved').count()   # case-insensitive


    return render(request, 'transaction.html', {
        'transactions': transactions,
        'projects': projects,
        'categories': categories,
        'selected': selected,
        'summary': {
            'total_income': total_income,
            'total_expense': total_expense,
            'total_transactions': total_transactions,
            'total_pending': total_pending,
            'total_approved': total_approved,
            'total_amount':total_amount,
            # 'income_count': transactions.filter(type__iexact='Income').count(),
    # 'expense_count': transactions.filter(type__iexact='Expense').count(),
        }
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



# def view_transaction(request, pk):
#     txn = get_object_or_404(Transaction.objects.select_related('project'), pk=pk)
#     html = render_to_string('view_transaction_detail.html', {'txn': txn})
#     return JsonResponse({'html': html})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Transaction, BillProof, PaymentProof

def view_transaction(request, pk):
    txn = get_object_or_404(Transaction.objects.select_related('project'), pk=pk)

    # Get related proofs
    bill_proofs = BillProof.objects.filter(transaction=txn)
    payment_proofs = PaymentProof.objects.filter(transaction=txn)

    # Render the modal content
    html = render_to_string('view_transaction_detail.html', {
        'txn': txn,
        'bill_proofs': bill_proofs,
        'payment_proofs': payment_proofs
    })

    return JsonResponse({'html': html})


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Transaction, BillProof, PaymentProof
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Transaction, BillProof, PaymentProof
def edit_transaction(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        txn.project_id = request.POST.get('project')
        txn.type = request.POST.get('type')
        txn.amount = request.POST.get('amount')
        txn.vendor = request.POST.get('vendor')
        txn.status = request.POST.get('status')
        txn.category = request.POST.get('category')
        txn.description = request.POST.get('description')
        txn.save()

        # ✅ Only delete BillProofs if new bill_proofs were uploaded
        if 'bill_proofs' in request.FILES:
            BillProof.objects.filter(transaction=txn).delete()
            for f in request.FILES.getlist('bill_proofs'):
                BillProof.objects.create(transaction=txn, file=f)

        # ✅ Only delete PaymentProofs if new payment_proofs were uploaded
        if 'payment_proofs' in request.FILES:
            PaymentProof.objects.filter(transaction=txn).delete()
            for f in request.FILES.getlist('payment_proofs'):
                PaymentProof.objects.create(transaction=txn, file=f)

        return JsonResponse({'success': True})

    else:
        data = {
            'id': txn.id,
            'transaction_id': txn.transaction_id,
            'project': txn.project_id,
            'type': txn.type,
            'amount': str(txn.amount),
            'vendor': txn.vendor,
            'status': txn.status,
            'category': txn.category,
            'description': txn.description,
        }

        bill_proofs = list(BillProof.objects.filter(transaction=txn).values('id', 'file'))
        payment_proofs = list(PaymentProof.objects.filter(transaction=txn).values('id', 'file'))

        return JsonResponse({
            'txn': data,
            'bill_proofs': bill_proofs,
            'payment_proofs': payment_proofs,
        })


from django.template.loader import render_to_string

from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction

def delete_transaction(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        txn.delete()
        return redirect('transaction_list') 


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


from datetime import date
from decimal import Decimal
from django.db.models import Sum
from django.shortcuts import get_object_or_404, render, redirect
from .models import Loan, Repayment
from .forms import RepaymentForm


def loan_detail(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    repayments = loan.repayments.all().order_by('date')
    repayment_form = RepaymentForm()

    # Set up for loop display with balances
    repayments_data = []
    remaining_balance = loan.amount

    for repayment in repayments:
        remaining_balance -= repayment.principal_paid or Decimal('0.00')
        repayments_data.append({
            'repayment': repayment,
            'balance_after': remaining_balance
        })

    # Default values for GET request context
    interest_paid = Decimal('0.00')
    principal_paid = Decimal('0.00')

    if request.method == 'POST':
        repayment_form = RepaymentForm(request.POST,request.FILES)
        if repayment_form.is_valid():
            repayment = repayment_form.save(commit=False)
            repayment.loan = loan

            # Determine date range for interest calculation
            if repayments.exists():
                last_repayment_date = repayments.last().date
            else:
                last_repayment_date = loan.start_date

            new_payment_date = repayment.date
            days_elapsed = (new_payment_date - last_repayment_date).days or 1

            # Current balance before this repayment
            total_principal_paid = repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
            current_balance = loan.amount - total_principal_paid

            # Interest calculation based on time
            interest_calculated = (
                loan.interest_rate / Decimal('100.00')
            ) * current_balance * Decimal(days_elapsed) / Decimal('365.00')
            interest_calculated = round(interest_calculated, 2)

            repayment.interest_calculated = interest_calculated

            amt = repayment.amount_paid
            if amt <= interest_calculated:
                repayment.interest_paid = amt
                repayment.principal_paid = Decimal('0.00')
            else:
                repayment.interest_paid = interest_calculated
                repayment.principal_paid = amt - interest_calculated

            repayment.balance_after_repayment = current_balance - repayment.principal_paid

            interest_paid = repayment.interest_paid
            principal_paid = repayment.principal_paid

            repayment.save()
            return redirect('loan_detail', loan_id=loan.id)

    # Final Totals
    total_interest_paid = repayments.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
    total_principal_paid = repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
    remaining_balance = loan.amount - total_principal_paid

    return render(request, 'loan_detail.html', {
        'loan': loan,
        'repayments': repayments_data,
        'repayment_form': repayment_form,
        'total_interest_paid': total_interest_paid,
        'total_principal_paid': total_principal_paid,
        'remaining_balance': remaining_balance,
        'interest_paid': interest_paid,
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
from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, TaskFile, Staff, Project
from .forms import TaskForm
from django.db.models import Q

def task_list(request):
    tasks = Task.objects.all().order_by('-date')

    # --- Filtering ---
    task_id = request.GET.get('task_id')
    status = request.GET.get('status')
    staff = request.GET.get('staff')
    project = request.GET.get('project')
    due_date_from = request.GET.get('due_date_from')
    due_date_to = request.GET.get('due_date_to')
    created_from = request.GET.get('created_from')
    created_to = request.GET.get('created_to')

    if task_id:
        tasks = tasks.filter(task_id__icontains=task_id)
    if status and status != 'all':
        tasks = tasks.filter(status=status)
    if staff and staff != 'all':
        tasks = tasks.filter(staff_id=staff)
    if project and project != 'all':
        tasks = tasks.filter(project_id=project)
    if due_date_from:
        tasks = tasks.filter(due_date__gte=due_date_from)
    if due_date_to:
        tasks = tasks.filter(due_date__lte=due_date_to)
    if created_from:
        tasks = tasks.filter(date__gte=created_from)
    if created_to:
        tasks = tasks.filter(date__lte=created_to)

    # --- POST Handling ---
    if request.method == 'POST':
        # Add Task
        if 'add_task' in request.POST:
            form = TaskForm(request.POST, request.FILES)
            files = request.FILES.getlist('file')
            voice_memo = request.FILES.get('voice_memo')

            if form.is_valid():
                task = form.save(commit=False)
                if voice_memo:
                    task.voice_memo = voice_memo
                task.save()

                for f in files:
                    TaskFile.objects.create(task=task, file=f)

                return redirect('task_list')

        # Edit Task
        elif 'edit_task' in request.POST:
            task_id = request.POST.get('task_id_hidden')
            task = get_object_or_404(Task, id=task_id)
            prefix = f"task_{task.id}"
            form = TaskForm(request.POST, request.FILES, instance=task, prefix=prefix)

            if form.is_valid():
                if 'voice_memo' in request.FILES:
                    task.voice_memo = request.FILES['voice_memo']
                form.save()
                return redirect('task_list')

    # Form for Add Task
    form = TaskForm()

    # Forms for Edit Modals
    for task in tasks:
        task.get_form = TaskForm(instance=task, prefix=f"task_{task.id}")

    context = {
        'tasks': tasks,
        'form': form,
        'staffs': Staff.objects.all(),
        'projects': Project.objects.all(),
        # Include current GET values to retain filter state
        'get': request.GET,
    }

    return render(request, 'task.html', context)


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

from django.shortcuts import render
from django.db.models import Sum
from .models import Project, Transaction, Staff, Loan, Repayment

from django.shortcuts import render
from django.db.models import Sum
from .models import Project, Transaction, Staff, Loan, Repayment

def dashboard_view(request):
    total_projects = Project.objects.count()
    total_income = Transaction.objects.filter(type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_staff = Staff.objects.count()
    total_loan_amount = Loan.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_loan_repaid = Repayment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_outstanding_loan = total_loan_amount - total_loan_repaid
    net_profit = total_income - total_expense

    # Calculate bar heights (max 200px)
    max_height = 200
    max_value = max(total_income, total_expense, 1)  # Avoid division by 0
    income_bar_height = int((total_income / max_value) * max_height)
    expense_bar_height = int((total_expense / max_value) * max_height)

    context = {
        'total_projects': total_projects,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_staff': total_staff,
        'total_loan_amount': total_loan_amount,
        'total_loan_repaid': total_loan_repaid,
        'total_outstanding_loan': total_outstanding_loan,
        'net_profit': net_profit,
        'income_bar_height': income_bar_height,
        'expense_bar_height': expense_bar_height,
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




from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from decimal import Decimal
from .models import Loan
from django.shortcuts import get_object_or_404
from django.db.models import Sum

def loan_pdf(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    repayments = loan.repayments.all().order_by('date')

    remaining_balance = loan.amount
    repayments_data = []
    for repayment in repayments:
        remaining_balance -= repayment.principal_paid or Decimal('0.00')
        repayments_data.append({
            'repayment': repayment,
            'balance_after': remaining_balance
        })

    total_interest_paid = repayments.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
    total_principal_paid = repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
    remaining_balance = loan.amount - total_principal_paid

    template = get_template('loan_pdf.html')
    html = template.render({
        'loan': loan,
        'repayments': repayments_data,
        'total_interest_paid': total_interest_paid,
        'total_principal_paid': total_principal_paid,
        'remaining_balance': remaining_balance,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Loan_{loan.id}_Details.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('PDF generation failed')
    return response




from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Transaction
from django.db.models import Q

def transaction_pdf(request):
    # Filters from query parameters
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    project = request.GET.get('project')
    tx_type = request.GET.get('type')
    category = request.GET.get('category')

    transactions = Transaction.objects.all()

    if start_date:
        transactions = transactions.filter(created_at__date__gte=start_date)
    if end_date:
        transactions = transactions.filter(created_at__date__lte=end_date)
    if project and project != 'all':
        transactions = transactions.filter(project__id=project)
    if tx_type and tx_type != 'all':
        transactions = transactions.filter(type=tx_type)
    if category and category != 'all':
        transactions = transactions.filter(category=category)

    # Render template
    template = get_template('transaction_pdf.html')
    html = template.render({'transactions': transactions})
    
    # Generate PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Error generating PDF', status=500)
    return response



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Loan, Repayment
from decimal import Decimal
from django.db.models import Sum

def download_loan_pdf(request):
    loans = Loan.objects.select_related('project').all()

    total_loaned_amount = loans.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    total_principal_repaid = Repayment.objects.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
    total_interest_collected = Repayment.objects.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
    total_outstanding = total_loaned_amount - total_principal_repaid

    # Attach computed fields like in the main view
    for loan in loans:
        loan.total_interest_paid = loan.repayments.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
        total_principal = loan.repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
        loan.remaining_balance = loan.amount - total_principal

    template = get_template('loan_pdf_template.html')
    html = template.render({
        'loans': loans,
        'total_loaned_amount': total_loaned_amount,
        'total_principal_repaid': total_principal_repaid,
        'total_interest_collected': total_interest_collected,
        'total_outstanding': total_outstanding,
    })

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="loan_report.pdf"'
    pisa.CreatePDF(html, dest=response)
    return response




# views.py

from django.shortcuts import render, redirect
from .models import Task, Staff, StaffMessage
from .forms import StaffMessageForm

from datetime import date
from .models import Target  # make sure it's imported

def staff_dashboard(request):
    staff = Staff.objects.get(id=request.user.id)  # Adjust if needed
    tasks = Task.objects.filter(staff=staff)
    targets = Target.objects.filter(staff=staff, date=date.today())  # today's targets

    if request.method == 'POST':
        form = StaffMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.staff = staff
            message.save()
            return redirect('staff_dashboard')
    else:
        form = StaffMessageForm()

    return render(request, 'staff_dashboard.html', {
        'staff': staff,
        'tasks': tasks,
        'form': form,
        'targets': targets,
        'today': date.today(),  # so that {{ today }} in template works
    })


# views.py

def admin_messages(request):
    messages = StaffMessage.objects.select_related('staff').order_by('-timestamp')
    return render(request, 'admin_messages.html', {'messages': messages})



from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from .models import Project

def generate_project_pdf(request):
    projects = Project.objects.all()
    template_path = 'project_pdf_template.html'
    context = {'projects': projects}
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="projects.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed <pre>' + html + '</pre>')
    return response




from django.shortcuts import render, redirect, get_object_or_404
from .models import Target, Project, Staff
from .forms import TargetForm
from django.views.decorators.csrf import csrf_exempt

def target_dashboard(request):
    targets = Target.objects.all().order_by('-date')
    form = TargetForm()
    projects = Project.objects.all()
    staff_list = Staff.objects.all()
    return render(request, 'target_list.html', {
        'targets': targets, 'form': form, 'projects': projects, 'staff_list': staff_list
    })

def add_target(request):
    if request.method == 'POST':
        form = TargetForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect('target_dashboard')

@csrf_exempt
def edit_target(request, pk):
    target = get_object_or_404(Target, pk=pk)
    if request.method == 'POST':
        form = TargetForm(request.POST, instance=target)
        if form.is_valid():
            form.save()
    return redirect('target_dashboard')

def delete_target(request, pk):
    target = get_object_or_404(Target, pk=pk)
    if request.method == 'POST':
        target.delete()
    return redirect('target_dashboard')




from django.http import JsonResponse

def get_next_project_code(request):
    last_project = Project.objects.order_by('-id').first()
    if last_project and last_project.code.startswith("PRJ"):
        last_num = int(last_project.code.replace("PRJ", ""))
    else:
        last_num = 0
    next_code = f"PRJ{last_num + 1:03d}"
    return JsonResponse({'next_code': next_code})


