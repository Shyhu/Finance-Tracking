from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from .models import Project
from .forms import ProjectForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Task
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
from django.shortcuts import render, get_object_or_404
from .models import Project

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm

from django.http import JsonResponse, HttpResponseNotAllowed
from django.views.decorators.http import require_POST
from .models import Project

from django.shortcuts import render
from django.http import JsonResponse
from .models import Transaction, BillProof, PaymentProof, Category, Project
from .forms import TransactionForm
from django.shortcuts import render
from .models import Transaction, Project, Category
from django.utils.dateparse import parse_date
from datetime import datetime

from django.db.models import Sum, Count
from django.utils import timezone
from django.http import JsonResponse
from .models import Transaction, BillProof, PaymentProof
from .forms import TransactionForm


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Transaction, BillProof, PaymentProof

from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Transaction, BillProof, PaymentProof
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from .models import Transaction, BillProof, PaymentProof

from django.template.loader import render_to_string

from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Staff, Project
from .forms import StaffForm

def base(request):
    return render(request,'base.html')



def project_list(request):
    projects = Project.objects.order_by('-id')
    total_budget = projects.aggregate(Sum('total_budget'))['total_budget__sum'] or 0
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
                'notes': project.notes or "",
                 'total_budget': total_budget,
            })

        return JsonResponse({'errors': form.errors}, status=400)

    return render(request, 'project.html', {'projects': projects, 'form': form})







def project_detail_view(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'project_detail.html', {'project': project})




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
    


@require_POST
def delete_project(request, pk):
    try:
        project = Project.objects.get(pk=pk)
        project.delete()
        return JsonResponse({'success': True})
    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'})




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
        transactions = transactions.filter(created_at__gte=parse_date(start_date))
    if end_date:
        transactions = transactions.filter(created_at__lte=parse_date(end_date))

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
        
        if form.is_valid():
            transaction = form.save(commit=False)

            # Use user input if provided, else set to now
            if form.cleaned_data.get('created_at'):
                transaction.created_at = form.cleaned_data['created_at']
            else:
                transaction.created_at = timezone.now()

            transaction.save()

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

        bill_proofs = [{'id': bp.id, 'file': bp.file.url} for bp in BillProof.objects.filter(transaction=txn)]
        payment_proofs = [{'id': pp.id, 'file': pp.file.url} for pp in PaymentProof.objects.filter(transaction=txn)]

        return JsonResponse({
            'txn': data,
            'bill_proofs': bill_proofs,
            'payment_proofs': payment_proofs,
        })



def delete_transaction(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)

    if request.method == 'POST':
        txn.delete()
        return redirect('transaction_list') 


# app1/views.py


# def staff_list(request):
#     staff_list = Staff.objects.all()
#     project_list = Project.objects.all()
#     form = StaffForm()

#     if request.method == 'POST':
#         if 'add_staff' in request.POST:
#             form = StaffForm(request.POST, request.FILES)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, "Staff added successfully.")
#                 return redirect('staff_list')
#             else:
#                 messages.error(request, "Error adding staff.")

#         elif 'edit_staff' in request.POST:
#             staff_pk = request.POST.get('staff_pk')
#             staff_obj = get_object_or_404(Staff, id=staff_pk)
#             form = StaffForm(request.POST, request.FILES, instance=staff_obj)
#             if form.is_valid():
#                 form.save()
#                 messages.success(request, "Staff updated successfully.")
#                 return redirect('staff_list')
#             else:
#                 messages.error(request, "Error updating staff.")

#     return render(request, 'staff_list.html', {
#         'staff_list': staff_list,
#         'project_list': project_list,
#         'form': form,
#     })





# # def view_staff(request, pk):
# #     staff = get_object_or_404(Staff, pk=pk)
# #     files = staff.files.all()
# #     return render(request, 'staff_detail.html', {'staff': staff, 'files': files})




# def delete_staff(request, staff_id):
#     staff = get_object_or_404(Staff, id=staff_id)
#     staff.delete()
#     messages.success(request, "Staff member deleted.")
#     return redirect('staff_list')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Staff, Project, Task
from .forms import StaffForm

def staff_list(request):
    staff_list = Staff.objects.all()
    project_list = Project.objects.all()
    form = StaffForm()

    if request.method == 'POST':
        if 'add_staff' in request.POST:
            form = StaffForm(request.POST, request.FILES)
            password = request.POST.get('password')
            if form.is_valid():
                user = User.objects.create_user(
                    username=request.POST.get('staff_id'),
                    password=password
                )
                staff = form.save(commit=False)
                staff.user = user
                staff.save()
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
from django.shortcuts import render
from decimal import Decimal
from django.db.models import Sum
from .models import Loan, Repayment, Project
from .forms import LoanForm

def loan_list(request):
    loans = Loan.objects.select_related('project').all()
    form = LoanForm()  # Required for Add Loan Modal

    # Attach repayment info and compute remaining_balance for each loan
    for loan in loans:
        loan.get_form = LoanForm(instance=loan)
        total_interest = loan.repayments.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
        total_principal = loan.repayments.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
        loan.remaining_balance = loan.amount - total_principal
        loan.total_interest_paid = total_interest

    # Convert queryset to list for filtering on custom field
    loans = list(loans)

    # Filters from GET parameters
    project = request.GET.get('project')
    loan_amount = request.GET.get('loan_amount')
    balance = request.GET.get('balance')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')  # new line
    interest_rate = request.GET.get('interest_rate')

    if project:
        loans = [loan for loan in loans if str(loan.project_id) == project]
    if loan_amount:
        loans = [loan for loan in loans if loan.amount >= Decimal(loan_amount)]
    if balance:
        loans = [loan for loan in loans if loan.remaining_balance <= Decimal(balance)]
    if start_date:
        loans = [loan for loan in loans if str(loan.start_date) >= start_date]
    if end_date:
        loans = [loan for loan in loans if str(loan.start_date) <= end_date]

    if interest_rate:
        loans = [loan for loan in loans if loan.interest_rate >= Decimal(interest_rate)]

    # Summary totals (not filtered, but you can change that if needed)
    total_loaned_amount = sum([loan.amount for loan in loans], Decimal('0.00'))
    total_principal_repaid = Repayment.objects.aggregate(total=Sum('principal_paid'))['total'] or Decimal('0.00')
    total_interest_collected = Repayment.objects.aggregate(total=Sum('interest_paid'))['total'] or Decimal('0.00')
    total_outstanding = total_loaned_amount - total_principal_repaid

    context = {
        'form': form,  # Add Loan Modal
        'loans': loans,
        'projects': Project.objects.all(),
        'total_loaned_amount': total_loaned_amount,
        'total_principal_repaid': total_principal_repaid,
        'total_interest_collected': total_interest_collected,
        'total_outstanding': total_outstanding,
    }
    return render(request, 'loan.html', context)


def create_loan(request):
    if request.method == 'POST':
        form = LoanForm(request.POST,request.FILES)
        if form.is_valid():
            form.save()
    return redirect('loan_list')

def update_loan(request, pk):
    loan = get_object_or_404(Loan, pk=pk)
    if request.method == 'POST':
        form = LoanForm(request.POST,request.FILES,instance=loan)
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


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from django.shortcuts import get_object_or_404

def get_repayment_data(repayment, request=None):
    photo_url = ''
    if repayment.photo_proof and hasattr(repayment.photo_proof, 'url'):
        try:
            photo_url = request.build_absolute_uri(repayment.photo_proof.url) if request else repayment.photo_proof.url
        except ValueError:
            photo_url = ''
    return {
        'id': repayment.id,
        'date': repayment.date.strftime('%Y-%m-%d'),
        'amount_paid': float(repayment.amount_paid),
        'interest_paid': float(repayment.interest_paid),
        'principal_paid': float(repayment.principal_paid),
        'interest_calculated': float(repayment.interest_calculated),
        'photo_proof_url': photo_url,
    }

# def repayment_detail(request, repayment_id):
#     repayment = get_object_or_404(Repayment, id=repayment_id)
#     return JsonResponse(get_repayment_data(repayment))

def repayment_detail(request, repayment_id):
    repayment = get_object_or_404(Repayment, id=repayment_id)
    return JsonResponse(get_repayment_data(repayment, request=request))


@require_POST
def edit_repayment(request, repayment_id):
    repayment = get_object_or_404(Repayment, id=repayment_id)
    form = RepaymentForm(request.POST, request.FILES, instance=repayment)
    if form.is_valid():
        form.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})

@require_POST
@csrf_exempt
def delete_repayment(request, repayment_id):
    repayment = get_object_or_404(Repayment, id=repayment_id)
    repayment.delete()
    return JsonResponse({'success': True})




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
from django.db.models import Sum
from collections import defaultdict

from django.shortcuts import render
from django.db.models import Sum
from .models import Project, Transaction, Staff, Loan, Repayment
from django.shortcuts import render
from .models import Project, Transaction, Staff, Loan, Repayment
from django.db.models import Sum
from django.contrib.auth.decorators import login_required

@login_required
@login_required
def dashboard_view(request):
    from decimal import Decimal
    from django.db.models import Sum

    total_projects = Project.objects.count()
    total_income = Transaction.objects.filter(type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
    total_expense = Transaction.objects.filter(type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0
    total_staff = Staff.objects.count()
    total_loan_amount = Loan.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    total_loan_repaid = Repayment.objects.aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    total_outstanding_loan = total_loan_amount - total_loan_repaid
    net_profit = total_income - total_expense - total_outstanding_loan  # ✅ updated to subtract outstanding loan
    total_principal_repaid = Repayment.objects.aggregate(Sum('principal_paid'))['principal_paid__sum'] or 0
    total_outstanding_principal = total_loan_amount - total_principal_repaid


    projects = Project.objects.all()
    project_bars = []
    for project in projects:
        income = Transaction.objects.filter(project=project, type='Income').aggregate(Sum('amount'))['amount__sum'] or 0
        expense = Transaction.objects.filter(project=project, type='Expense').aggregate(Sum('amount'))['amount__sum'] or 0

        # Calculate outstanding loan for each project
        project_loans = Loan.objects.filter(project=project)
        project_loan_total = project_loans.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
        repaid_total = Repayment.objects.filter(loan__project=project).aggregate(Sum('principal_paid'))['principal_paid__sum'] or Decimal('0.00')
        remaining_loan = project_loan_total - repaid_total

        project_bars.append({
            'name': project.name,
            'income': float(income),
            'expense': float(expense),
            'remaining': float(remaining_loan),  # ✅ add to bar chart data
        })

    context = {
        'total_projects': total_projects,
        'total_income': total_income,
        'total_expense': total_expense,
        'total_staff': total_staff,
        'total_loan_amount': total_loan_amount,
        'total_loan_repaid': total_loan_repaid,
        'total_outstanding_loan': total_outstanding_loan,
        'net_profit': net_profit,
        'project_bars': project_bars,
        'total_outstanding_principal': total_outstanding_principal,
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




from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm

# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')  # Replace with your home/dashboard view

#     form = LoginForm(request.POST or None)
#     if request.method == 'POST' and form.is_valid():
#         username = form.cleaned_data['username']
#         password = form.cleaned_data['password']
#         user = authenticate(request, username=username, password=password)

#         if user:
#             login(request, user)
#             return redirect('dashboard')  # or wherever you want to redirect
#         else:
#             form.add_error(None, "Invalid username or password.")

#     return render(request, 'login.html', {'form': form})
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect

from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard')
            else:
                return redirect('staff_dashboard')
    return render(request, 'login.html', {'form': form})





from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to login page after logout





import openpyxl
import requests
from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.dateparse import parse_datetime
from .models import Transaction, Project, Category

def import_transactions(request):
    if request.method == "POST":
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, "No file uploaded.")
            return redirect('transaction_list')

        try:
            wb = openpyxl.load_workbook(excel_file)
            sheet = wb.active

            for idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                try:
                    (
                        project_name, txn_id, txn_type, amount, vendor,
                        created_at, status, category_name, description,
                        bill_url, payment_url
                    ) = row
                    print(project_name,payment_url)

                    # Validate Project
                    project = Project.objects.filter(name=project_name).first()
                    if not project:
                        messages.warning(request, f"Row {idx}: Project '{project_name}' not found.")
                        continue

                    # Skip duplicates
                    if Transaction.objects.filter(transaction_id=txn_id).exists():
                        messages.warning(request, f"Row {idx}: Transaction ID '{txn_id}' already exists. Skipped.")
                        continue

                    # Validate datetime
                    parsed_date = parse_datetime(str(created_at))
                    if not parsed_date:
                        messages.warning(request, f"Row {idx}: Invalid date '{created_at}'. Skipped.")
                        continue

                    # Get/Create Category
                    category, _ = Category.objects.get_or_create(name=category_name)

                    # Create Transaction
                    txn = Transaction(
                        transaction_id=txn_id,
                        project=project,
                        type=txn_type,
                        amount=amount,
                        vendor=vendor,
                        created_at=parsed_date,
                        status=status,
                        category=category,
                        description=description
                    )
                    txn.save()

                    # Bill Proof from URL
                    if bill_url:
                        response = requests.get(bill_url)
                        if response.status_code == 200:
                            file_name = f"{txn_id}_bill.{bill_url.split('.')[-1]}"
                            BillProof.objects.create( transaction =txn,file=file_name)
                            # txn.bill_proof.save(file_name, ContentFile(response.content), save=False)

                    # Payment Proof from URL
                    if payment_url:
                        response = requests.get(payment_url)
                        print(response)
                        if response.status_code == 200:
                            file_name = f"{txn_id}_payment.{payment_url.split('.')[-1]}"
                            PaymentProof.objects.create( transaction=txn,file=file_name)
                            # txn.payment_proof.save(file_name, ContentFile(response.content), save=False)

                    # txn.save()

                except Exception as e:
                    print(e,'ssssss,sxmxmnncxbncbcmbvnchfdffgd')
                    messages.error(request, f"Row {idx} error: {str(e)}")

            messages.success(request, "Transactions imported successfully.")
            return redirect('transaction_list')

        except Exception as e:
            messages.error(request, f"Import failed: {str(e)}")
            return redirect('transaction_list')

    return redirect('transaction_list')



from django.contrib.auth.decorators import login_required
from .models import Staff, Task

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from app1.models import Staff, Task
from .models import Target  # Assuming Target is in the same app


from app1.models import LeaveRequest
from .forms import LeaveRequestForm

from app1.models import LeaveRequest, Target, Task, Staff
from .forms import LeaveRequestForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db import models  
# @login_required
# def staff_dashboard(request):
#     staff = get_object_or_404(Staff, user=request.user)

#     tasks = Task.objects.filter(staff=staff).prefetch_related('files')
#     targets = Target.objects.filter(staff=staff)
#     leaves = LeaveRequest.objects.filter(staff=staff).order_by('-requested_at')

#     # ✅ Calculate counts
#     total_targets = targets.count()
#     total_target_amount = targets.aggregate(total=models.Sum('target_amount'))['total'] or 0

#     if request.method == 'POST':
#         leave_form = LeaveRequestForm(request.POST)
#         if leave_form.is_valid():
#             leave = leave_form.save(commit=False)
#             leave.staff = staff
#             leave.save()
#             messages.success(request, "Leave request submitted.")
#             return redirect('staff_dashboard')
#     else:
#         leave_form = LeaveRequestForm()

#     return render(request, 'staff_dashboard.html', {
#         'staff': staff,
#         'tasks': tasks,
#         'targets': targets,
#         'leaves': leaves,
#         'leave_form': leave_form,
#         'total_targets': total_targets,                # ✅ Pass total targets
#         'total_target_amount': total_target_amount     # ✅ Pass total target amount
#     })

# NEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.db.models import Sum
# from datetime import datetime
# from .forms import LeaveRequestForm
# from app1.models import Staff, Task, Target, LeaveRequest

# @login_required
# def staff_dashboard(request):
#     staff = get_object_or_404(Staff, user=request.user)

#     # Handle month filter
#     selected_month = request.GET.get('month')
#     if selected_month and selected_month.lower() != 'none':
#         try:
#             selected_date = datetime.strptime(selected_month, '%Y-%m')
#         except ValueError:
#             selected_date = datetime.today()
#     else:
#         selected_date = datetime.today()

#     # Get targets for the month
#     targets = Target.objects.filter(
#         staff=staff,
#         date__year=selected_date.year,
#         date__month=selected_date.month
#     )

#     # ✅ Handle achieved amount update (NO impact on leave form)
#     if request.method == 'POST' and 'target_id' in request.POST:
#         target_id = request.POST.get('target_id')
#         achieved_amount = request.POST.get('achieved_amount')
#         try:
#             target = Target.objects.get(id=target_id, staff=staff)
#             target.achieved_amount = achieved_amount
#             target.save()
#             messages.success(request, "Achieved amount updated.")
#             return redirect(f'{request.path}?month={selected_month or selected_date.strftime("%Y-%m")}')
#         except Target.DoesNotExist:
#             messages.error(request, "Target not found.")

#     # Leave form logic untouched ✅
#     if request.method == 'POST' and 'start_date' in request.POST:
#         leave_form = LeaveRequestForm(request.POST)
#         if leave_form.is_valid():
#             leave = leave_form.save(commit=False)
#             leave.staff = staff
#             leave.save()
#             messages.success(request, "Leave request submitted.")
#             return redirect('staff_dashboard')
#     else:
#         leave_form = LeaveRequestForm()

#     # Other dashboard data
#     tasks = Task.objects.filter(staff=staff).prefetch_related('files')
#     leaves = LeaveRequest.objects.filter(staff=staff).order_by('-requested_at')
#     total_targets = targets.count()
#     total_target_amount = targets.aggregate(total=Sum('target_amount'))['total'] or 0

#     return render(request, 'staff_dashboard.html', {
#         'staff': staff,
#         'tasks': tasks,
#         'targets': targets,
#         'leaves': leaves,
#         'leave_form': leave_form,
#         'total_targets': total_targets,
#         'total_target_amount': total_target_amount,
#         'selected_month': selected_month,
#         'today': datetime.today()
#    
@login_required
def staff_dashboard(request):
    staff = get_object_or_404(Staff, user=request.user)

    # Month filtering (existing)
    selected_month = request.GET.get('month')
    if selected_month and selected_month.lower() != 'none':
        try:
            selected_date = datetime.strptime(selected_month, '%Y-%m')
        except ValueError:
            selected_date = datetime.today()
    else:
        selected_date = datetime.today()

    # Targets for the selected month (existing)
    targets = Target.objects.filter(
        staff=staff,
        date__year=selected_date.year,
        date__month=selected_date.month
    )

    # ✅ Target achieved amount update (existing)
    if request.method == 'POST' and 'target_id' in request.POST:
        target_id = request.POST.get('target_id')
        achieved_amount = request.POST.get('achieved_amount')
        try:
            target = Target.objects.get(id=target_id, staff=staff)
            target.achieved_amount = achieved_amount
            target.save()
            messages.success(request, "Achieved amount updated.")
            return redirect(f'{request.path}?month={selected_month or selected_date.strftime("%Y-%m")}')
        except Target.DoesNotExist:
            messages.error(request, "Target not found.")

    # ✅ Leave request form submission (existing)
    if request.method == 'POST' and 'start_date' in request.POST:
        leave_form = LeaveRequestForm(request.POST)
        if leave_form.is_valid():
            leave = leave_form.save(commit=False)
            leave.staff = staff
            leave.save()
            messages.success(request, "Leave request submitted.")
            return redirect('staff_dashboard')
    else:
        leave_form = LeaveRequestForm()

    # ✅ New: Filtering leaves by purpose and status (added safely)
    purpose_filter = request.GET.get('purpose', '')
    status_filter = request.GET.get('status', '')
    leaves = LeaveRequest.objects.filter(staff=staff)
    if purpose_filter:
        leaves = leaves.filter(purpose=purpose_filter)
    if status_filter:
        leaves = leaves.filter(status=status_filter)

    # ✅ All other data (untouched)
    tasks = Task.objects.filter(staff=staff).prefetch_related('files')
    approved_count = leaves.filter(status='Approved').count()
    pending_count = leaves.filter(status='Pending').count()
    rejected_count = leaves.filter(status='Rejected').count()
    total_targets = targets.count()
    total_target_amount = targets.aggregate(total=Sum('target_amount'))['total'] or 0

    return render(request, 'staff_dashboard.html', {
        'staff': staff,
        'tasks': tasks,
        'targets': targets,
        'leaves': leaves.order_by('-requested_at'),
        'leave_form': leave_form,
        'total_targets': total_targets,
        'total_target_amount': total_target_amount,
        'approved_count': approved_count,
        'pending_count': pending_count,
        'rejected_count': rejected_count,
        'selected_month': selected_month,
        'today': datetime.today(),
        'purpose_filter': purpose_filter,
        'status_filter': status_filter,
    })





@login_required
def mark_task_complete(request, task_id):
    task = get_object_or_404(Task, id=task_id, staff=request.user.staff)
    if request.method == 'POST' and task.status != 'Completed':
        task.status = 'Completed'
        task.save()
        messages.success(request, "Task marked as completed.")
    return redirect('staff_dashboard')
from .models import MessageToAdmin

# def admin_task_report(request):
#     staff_members = Staff.objects.all()
#     task_data = []

#     for staff in staff_members:
#         tasks = Task.objects.filter(staff=staff)
#         total = tasks.count()
#         completed = tasks.filter(status='Completed').count()
#         pending = tasks.exclude(status='Completed').count()
#         progress = int((completed / total) * 100) if total else 0

#         task_data.append({
#             'staff': staff,
#             'total': total,
#             'completed': completed,
#             'pending': pending,
#             'progress': progress,
#         })

#     leaves = LeaveRequest.objects.select_related('staff').order_by('-requested_at')
#     staff_messages = MessageToAdmin.objects.select_related('staff').order_by('-sent_at')

#     return render(request, 'admin_task_report.html', {
#         'task_data': task_data,
#         'leaves': leaves,
#         'staff_messages': staff_messages
#     })


from django.shortcuts import render
from django.db.models import Sum
from app1.models import Staff, Task, Target, LeaveRequest, MessageToAdmin

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Sum
from app1.models import Staff, Task, Target, LeaveRequest, MessageToAdmin

def admin_task_report(request):
    staff_members = Staff.objects.all()
    task_data = []
    target_data = []

    for staff in staff_members:
        tasks = Task.objects.filter(staff=staff)
        total = tasks.count()
        completed = tasks.filter(status='Completed').count()
        pending = tasks.exclude(status='Completed').count()
        progress = int((completed / total) * 100) if total else 0

        task_data.append({
            'staff': staff,
            'total': total,
            'completed': completed,
            'pending': pending,
            'progress': progress,
        })

        targets = Target.objects.filter(staff=staff)
        total_target = targets.aggregate(Sum('target_amount'))['target_amount__sum'] or 0
        total_achieved = targets.aggregate(Sum('achieved_amount'))['achieved_amount__sum'] or 0
        target_met = total_target > 0 and total_target == total_achieved
        daily_targets = Target.objects.filter(staff=staff).order_by('date')

        target_data.append({
            'staff': staff,
            'target_total': total_target,
            'achieved_total': total_achieved,
            'target_met': target_met,
            'daily_targets': daily_targets,
        })

    # ✅ Leave requests and messages
    leaves = LeaveRequest.objects.select_related('staff').order_by('-requested_at')
    staff_messages = MessageToAdmin.objects.select_related('staff').order_by('-sent_at')

    return render(request, 'admin_task_report.html', {
        'task_data': task_data,
        'target_data': target_data,
        'leaves': leaves,
        'staff_messages': staff_messages,
    })


# ✅ Leave Status Update View
def update_leave_status(request, leave_id, status):
    leave = get_object_or_404(LeaveRequest, id=leave_id)
    if status in ['Approved', 'Rejected']:
        leave.status = status
        leave.save()
        messages.success(request, f"Leave marked as {status}.")
    return redirect('admin_task_report')



from app1.models import MessageToAdmin


def send_message_to_admin(request):
    if request.method == 'POST':
        staff = get_object_or_404(Staff, user=request.user)
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        voice_file = request.FILES.get('voice_message')  # Optional

        MessageToAdmin.objects.create(
            staff=staff,
            subject=subject,
            message=message,
            voice_message=voice_file  # Save the file
        )
        messages.success(request, "Your message (including voice, if any) was sent to the admin.")
        return redirect('staff_dashboard')
    return redirect('staff_dashboard')


