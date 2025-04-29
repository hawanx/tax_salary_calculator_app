from django.shortcuts import render
import requests
import json
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

standard_deduction = 75000  # fixed

def calculate_tax(salary):
    url = "https://lma.co.in/resources/Calculators/Tax_Calculator/Call_WebService.asmx/gettax"
    payload = f"{{txtSalary: \"{salary}\",txtIFHProperty: \"0\",txtBIncome: \"0\",txtOthers: \"0\",txtOtherIncome: \"0\",txtDUs80: \"0\",txtChild: \"0\",txtParent: \"0\",txtOtherDeduction: \"0\",txt20Tax: \"0\",txt10Tax: \"0\",txtSOWSTTaxpaid: \"0\",txtWFCountries: \"0\",txtAIncome: \"0\",rdoLstStatus: \"Individual\",rdoLstComType: \"Domestic\",rdoIndstatus: \"O\",fyear: \"2025\",ded80tta: \"-99999\",TURNOVER: \"0\",txtnew20Taxshort: \"0\",txtnew12Taxlong: \"0\",flag1: 0,flag2: 0,sflag1: \"\",sflag2: \"\"\r\n}}"
    headers = {'content-type': 'application/json; charset=UTF-8'}
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response ,"RESPONSE-Text=" response.text)
    data = json.loads(response.text)["d"].split(",")
    total_tax = float(data[0]) + float(data[8]) - float(data[-2])
    net_annual_salary = float(salary) + standard_deduction - total_tax
    net_monthly_salary = net_annual_salary / 12
    return total_tax, net_annual_salary, net_monthly_salary

@csrf_exempt
def tax_calculator(request):
    result = None
    monthly_salary = request.POST.get('monthly_salary', '')
    epf_amount = request.POST.get('epf_amount', '')
    
    if request.method == 'POST':
        try:
            monthly_salary_float = float(monthly_salary)
            epf_amount_float = float(epf_amount)
            total_salary = monthly_salary_float + epf_amount_float
            annual_salary = 12 * total_salary
            total_tax, net_annual_salary, net_monthly_salary = calculate_tax(annual_salary - standard_deduction)
            result = {
                'total_tax': f"{total_tax:.0f}",
                'net_monthly_salary': f"{net_monthly_salary - epf_amount_float:.0f}",
                'net_money': f"{net_monthly_salary:.0f}"
            }
        except Exception as e:
            result = {'error': str(e)}
    
    context = {
        'result': result,
        'monthly_salary': monthly_salary,
        'epf_amount': epf_amount
    }
    return render(request, 'calculator/tax_calculator.html', context)
