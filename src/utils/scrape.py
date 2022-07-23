import pandas as pd
import webbrowser
import urllib.request
from io import BytesIO
from PIL import Image
import pytesseract
from PyPDF2 import PdfReader
import io


def parser(doc_URL, csvPath):
    # URL containing all invoices
    

    #Read Files
    csv_ = pd.read_csv(csvPath)

    # From pandas to list
    column_values = csv_['RedactedSupportingInvoiceId'].tolist()

    #cleaned columns from nan value
    cleaned_column = [int(x) for x in column_values if x == x]

    # read hosted document with index doc  w.m: we only checking the first document for now  
    wFile = urllib.request.urlopen(doc_URL + str(cleaned_column[0]))
    bytes_stream = BytesIO(wFile.read())
    reader_ = PdfReader(bytes_stream)
    # get the first page from the document
    page = reader_.pages[0]

    pages_text = page.extractText()

    #get lines
    lines=[] 
    #iterate through lines
    for line in io.StringIO(pages_text):
        lines.append(line)
    
    return lines


result=parser('http://search.electoralcommission.org.uk/Api/Spending/Invoices/','C:\\Users\\yassi\\OneDrive\\Desktop\\results.csv')

print(result)





    





