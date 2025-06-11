import jwt
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi.responses import StreamingResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from models.schemes import BillRequest
from io import BytesIO


router = APIRouter()
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try: 
        token = credentials.credentials
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

def generate_pdf(data):
    elements = []

    full_name = f"{data['last_name']} {data['first_name']} {data['middle_name']}"

    pdfmetrics.registerFont(TTFont('Roboto', 'resources/fonts/Roboto-VariableFont_wdth,wght.ttf'))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='content',
        fontName='Roboto',
        fontSize=14
    ))

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements.append(Paragraph(f'Плательщик: {full_name}', style=styles['content']))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f'Адрес: {data["address"]}', style=styles['content']))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f'Период оплаты: {data["period"]}', style=styles['content']))
    elements.append(Spacer(1, 30))
    
    services_table_data = [['Услуга', 'Количество', 'Цена за ед.', 'Сумма']]

    for service in data['services']:
        row = []
        for column_name in ['service_name', 'units', 'cost_per_unit', 'total_cost']:
            row.append(Paragraph(str(service[column_name]), style=styles['content']))

        services_table_data.append(row)

    services_table_data.append([Paragraph('ИТОГО', style=styles['content']), '', '', Paragraph(f"{data['total_amount']} ₽", style=styles['content'])])

    services_table = Table(
        services_table_data
    )
    service_style = TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Roboto'),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('FONTSIZE', (0, 0), (-1, -1), 14),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ])
    services_table.setStyle(service_style)

    elements.append(services_table)
    elements.append(Spacer(1, 70))

    bottom_table = Table(
        [[Paragraph(f'Дата создания: {data["created_at"]}', style=styles['content']), 
         Paragraph(f'Подпись: ______________', style=styles['content'])]]
    )
    
    elements.append(bottom_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer

@router.post("/")
async def generate_receipt(data: BillRequest, current_user = Depends(get_current_user)):
    data = data.model_dump()
    address_model = data['address']
    
    address = f"{address_model['region']}, {address_model['city']}, ул. {address_model['street']}, д. {address_model['house']}, кв. {address_model['apartment']}"

    data['address'] = address
    
    data['created_at'] = datetime.now()

    buffer = generate_pdf(data)

    headers = {'Content-Disposition': 'inline; filename="receipt.pdf"',"content-type": "application/octet-stream"}
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers=headers
    )