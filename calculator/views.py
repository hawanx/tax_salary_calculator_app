from django.shortcuts import render
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Create your views here.

standard_deduction = 75000  # fixed

def create_session():
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # number of retries
        backoff_factor=1,  # wait 1, 2, 4 seconds between retries
        status_forcelist=[500, 502, 503, 504]  # HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    return session

def calculate_tax(salary):
    url = "https://lma.co.in/resources/Calculators/Tax_Calculator/Call_WebService.asmx/gettax"
    payload = f"{{txtSalary: \"{salary}\",txtIFHProperty: \"0\",txtBIncome: \"0\",txtOthers: \"0\",txtOtherIncome: \"0\",txtDUs80: \"0\",txtChild: \"0\",txtParent: \"0\",txtOtherDeduction: \"0\",txt20Tax: \"0\",txt10Tax: \"0\",txtSOWSTTaxpaid: \"0\",txtWFCountries: \"0\",txtAIncome: \"0\",rdoLstStatus: \"Individual\",rdoLstComType: \"Domestic\",rdoIndstatus: \"O\",fyear: \"2025\",ded80tta: \"-99999\",TURNOVER: \"0\",txtnew20Taxshort: \"0\",txtnew12Taxlong: \"0\",flag1: 0,flag2: 0,sflag1: \"\",sflag2: \"\"\r\n}}"
    
    headers = {
        'content-type': 'application/json; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        session = create_session()
        response = session.post(url, headers=headers, data=payload, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = json.loads(response.text)["d"].split(",")
        total_tax = float(data[0]) + float(data[8]) - float(data[-2])
        net_annual_salary = float(salary) + standard_deduction - total_tax
        net_monthly_salary = net_annual_salary / 12
        return total_tax, net_annual_salary, net_monthly_salary
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error connecting to tax calculation service: {str(e)}")
    except (json.JSONDecodeError, IndexError, ValueError) as e:
        raise Exception(f"Error processing tax calculation response: {str(e)}")

@csrf_exempt
def tax_calculator(request):
    result = None
    if request.method == 'POST':
        try:
            monthly_salary = float(request.POST.get('monthly_salary', 0))
            epf_amount = float(request.POST.get('epf_amount', 0))
            total_salary = monthly_salary + epf_amount
            annual_salary = 12 * total_salary
            total_tax, net_annual_salary, net_monthly_salary = calculate_tax(annual_salary - standard_deduction)
            result = {
                'total_tax': f"{total_tax:.0f}",
                'net_monthly_salary': f"{net_monthly_salary - epf_amount:.0f}",
                'net_money': f"{net_monthly_salary:.0f}"
            }
        except Exception as e:
            result = {'error': str(e)}
    return render(request, 'calculator/tax_calculator.html', {'result': result})
