from django.template.loader import render_to_string
from django.conf import settings
from api2pdf import Api2Pdf
from secrets import token_urlsafe
from utils.aws import S3Client
import boto3
import io


class PdfManager:

    def __init__(self, template, context, encrypt=True):
        self.template = template
        self.context = context
        self.pdf_client = Api2Pdf(settings.PDF_API_KEY)
        self.s3_client = S3Client(settings.AWS_VINOCOUNT_IMAGES_BUCKET_NAME)

    
    def generate(self, filename):
        html = render_to_string(self.template, self.context)
        response = self.pdf_client.HeadlessChrome.convert_from_html(html)
        pdf = response.download_pdf()
        
        file_data = io.BytesIO(pdf)
        file_data.seek(0)
        filename = 'invoices/{}'.format(filename)
        self.s3_client.upload_object(file_data, filename, 'application/pdf')
        return filename