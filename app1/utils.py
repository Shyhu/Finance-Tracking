from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.template.loader import get_template
from .models import Loan

def generate_loan_pdf(request, loan_id):
    loan = get_object_or_404(Loan, pk=loan_id)
    template_path = 'loan_pdf.html'
    context = {'loan': loan}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Loan_{loan_id}_summary.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors while generating the PDF', status=500)
    return response
