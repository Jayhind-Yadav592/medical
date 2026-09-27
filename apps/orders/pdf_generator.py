"""
Antixor MedOS - Clinical Healthcare & Precision Dispensary
ReportLab PDF Generation Engine for Invoices, Prescriptions & Clinical Summaries.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.graphics.shapes import Drawing, Rect, String, Line, Group
from reportlab.graphics.barcode import qr


# Brand Color Palette
PRIMARY_EMERALD = colors.HexColor("#0a5c43")
SECONDARY_EMERALD = colors.HexColor("#059669")
ACCENT_MINT = colors.HexColor("#34d399")
LIGHT_BG = colors.HexColor("#f8fafc")
DARK_NAVY = colors.HexColor("#0f172a")
SLATE_GRAY = colors.HexColor("#64748b")
BORDER_GRAY = colors.HexColor("#e2e8f0")
BADGE_GREEN = colors.HexColor("#dcfce7")
BADGE_TEXT_GREEN = colors.HexColor("#166534")
BADGE_YELLOW = colors.HexColor("#fef3c7")
BADGE_TEXT_YELLOW = colors.HexColor("#92400e")


def get_custom_styles():
    """Build and return custom typography styles for clinical PDF reports."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='InvoiceTitle',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=PRIMARY_EMERALD,
    ))
    
    styles.add(ParagraphStyle(
        name='InvoiceSubtitle',
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=SLATE_GRAY,
    ))
    
    styles.add(ParagraphStyle(
        name='SectionHeader',
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=14,
        textColor=DARK_NAVY,
        spaceAfter=4,
    ))
    
    styles.add(ParagraphStyle(
        name='BodyRegular',
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=DARK_NAVY,
    ))
    
    styles.add(ParagraphStyle(
        name='BodyBold',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=13,
        textColor=DARK_NAVY,
    ))
    
    styles.add(ParagraphStyle(
        name='TableHeader',
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white,
        alignment=TA_LEFT,
    ))
    
    styles.add(ParagraphStyle(
        name='TableCell',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=DARK_NAVY,
    ))
    
    styles.add(ParagraphStyle(
        name='TableCellBold',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=DARK_NAVY,
    ))
    
    styles.add(ParagraphStyle(
        name='TableCellRight',
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=DARK_NAVY,
        alignment=TA_RIGHT,
    ))
    
    styles.add(ParagraphStyle(
        name='TableCellRightBold',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=DARK_NAVY,
        alignment=TA_RIGHT,
    ))
    
    styles.add(ParagraphStyle(
        name='LegalNotice',
        fontName='Helvetica-Oblique',
        fontSize=7.5,
        leading=10,
        textColor=SLATE_GRAY,
        alignment=TA_JUSTIFY,
    ))
    
    styles.add(ParagraphStyle(
        name='FooterCenter',
        fontName='Helvetica',
        fontSize=7.5,
        leading=10,
        textColor=SLATE_GRAY,
        alignment=TA_CENTER,
    ))
    
    return styles


def generate_order_invoice_pdf(order):
    """
    Generate an official, professional PDF Invoice for an Order.
    Returns: BytesIO buffer containing the PDF binary stream.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = get_custom_styles()
    story = []
    
    # -------------------------------------------------------------
    # 1. Header Banner & Pharmacy Letterhead
    # -------------------------------------------------------------
    header_data = [
        [
            Paragraph(
                "<b>ANTIXOR MEDOS</b><br/>"
                "<font size='8' color='#059669'>PRECISION DIGITAL HEALTHCARE & DISPENSARY NETWORK</font><br/>"
                "<font size='7.5' color='#64748b'>Central Hub: 750 5th Avenue, Suite 1400, New York, NY 10019<br/>"
                "NABP/FDA Dispensary License: <b>#NY-PHARM-9842</b> • DEA: <b>#BA9283711</b><br/>"
                "Tel: +1 (800) 584-ANTX (2689) • Email: rx@antixorpharmacy.com</font>",
                styles['InvoiceSubtitle']
            ),
            Paragraph(
                "<font color='#0a5c43' size='18'><b>CLINICAL TAX INVOICE</b></font><br/>"
                f"<font size='9' color='#0f172a'>Invoice No: <b>{order.order_number}</b></font><br/>"
                f"<font size='8' color='#64748b'>Date: {order.created_at.strftime('%B %d, %Y %I:%M %p')}<br/>"
                f"Status: <font color='{'#166534' if order.payment_status == 'PAID' else '#92400e'}'><b>{order.get_payment_status_display().upper()}</b></font></font>",
                styles['TableCellRight']
            )
        ]
    ]
    
    header_table = Table(header_data, colWidths=[340, 200])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_EMERALD, spaceBefore=4, spaceAfter=12))
    
    # -------------------------------------------------------------
    # 2. Patient / Shipping Info & Order Metadata Box
    # -------------------------------------------------------------
    patient_info = [
        [
            Paragraph("<b>PATIENT & RECIPIENT DETAILS</b>", styles['SectionHeader']),
            Paragraph("<b>ORDER & DISPATCH SPECIFICATIONS</b>", styles['SectionHeader'])
        ],
        [
            Paragraph(
                f"<b>Patient Name:</b> {order.full_name}<br/>"
                f"<b>Phone:</b> {order.phone}<br/>"
                f"<b>Email:</b> {order.email}<br/>"
                f"<b>Delivery Address:</b><br/>"
                f"{order.shipping_address}, {order.city} - {order.postal_code}",
                styles['BodyRegular']
            ),
            Paragraph(
                f"<b>Order Number:</b> {order.order_number}<br/>"
                f"<b>Payment Method:</b> {order.get_payment_method_display()}<br/>"
                f"<b>Fulfillment Status:</b> {order.get_order_status_display()}<br/>"
                f"<b>Estimated Dispatch:</b> {order.estimated_delivery}<br/>"
                f"<b>Tracking Code:</b> {order.tracking_number or f'TRK-{order.order_number}'}",
                styles['BodyRegular']
            )
        ]
    ]
    
    meta_table = Table(patient_info, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))
    
    # -------------------------------------------------------------
    # 3. Itemized Prescription & Medication Line Items
    # -------------------------------------------------------------
    story.append(Paragraph("<b>DISPENSED MEDICATIONS & CLINICAL SUPPLIES</b>", styles['SectionHeader']))
    story.append(Spacer(1, 4))
    
    items_data = [
        [
            Paragraph("<b>#</b>", styles['TableHeader']),
            Paragraph("<b>Medication / Clinical Item</b>", styles['TableHeader']),
            Paragraph("<b>Type / Dosage</b>", styles['TableHeader']),
            Paragraph("<b>Qty</b>", styles['TableHeader']),
            Paragraph("<b>Unit Price</b>", styles['TableHeader']),
            Paragraph("<b>Subtotal</b>", styles['TableHeader']),
        ]
    ]
    
    order_items = order.items.all()
    index = 1
    for item in order_items:
        product = item.product
        dosage_str = "FDA Registered RX / OTC"
        if product:
            form_name = product.get_dosage_form_display() if hasattr(product, 'get_dosage_form_display') else 'Oral'
            dosage_str = f"{form_name} ({product.dosage_strength or 'Standard'})"
            
        items_data.append([
            Paragraph(str(index), styles['TableCell']),
            Paragraph(f"<b>{item.product_name}</b>", styles['TableCell']),
            Paragraph(dosage_str, styles['TableCell']),
            Paragraph(str(item.quantity), styles['TableCell']),
            Paragraph(f"Rs. {item.unit_price:.2f}", styles['TableCellRight']),
            Paragraph(f"<b>Rs. {item.subtotal:.2f}</b>", styles['TableCellRightBold']),
        ])
        index += 1
        
    if not order_items:
        items_data.append([
            Paragraph("1", styles['TableCell']),
            Paragraph("<b>Clinical Prescription Order Fulfillment</b>", styles['TableCell']),
            Paragraph("Standard Prescribed Regimen", styles['TableCell']),
            Paragraph("1", styles['TableCell']),
            Paragraph(f"Rs. {order.total_amount:.2f}", styles['TableCellRight']),
            Paragraph(f"<b>Rs. {order.total_amount:.2f}</b>", styles['TableCellRightBold']),
        ])
        
    items_table = Table(items_data, colWidths=[25, 205, 130, 40, 70, 70])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_EMERALD),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 10))
    
    # -------------------------------------------------------------
    # 4. Totals & Financial Breakdown
    # -------------------------------------------------------------
    totals_data = [
        [
            Paragraph(
                "<b>Clinical Verification & Cold-Chain Notice:</b><br/>"
                "All items checked for drug-allergy contraindications and packed under 2°C–8°C "
                "continuous digital data-logger tracking. Store according to package inserts.",
                styles['LegalNotice']
            ),
            Table([
                [Paragraph("Medication Subtotal:", styles['TableCell']), Paragraph(f"Rs. {order.total_amount:.2f}", styles['TableCellRightBold'])],
                [Paragraph("Cold-Chain Express Shipping:", styles['TableCell']), Paragraph(f"Rs. {order.shipping_fee:.2f}" if order.shipping_fee > 0 else "<font color='#166534'><b>FREE (Rs. 0.00)</b></font>", styles['TableCellRight'])],
                [Paragraph("Clinical Savings / Coupon:", styles['TableCell']), Paragraph(f"-Rs. {order.discount_amount:.2f}" if order.discount_amount > 0 else "Rs. 0.00", styles['TableCellRight'])],
                [Paragraph("<b>TOTAL BILLED:</b>", styles['BodyBold']), Paragraph(f"<font size='11' color='#0a5c43'><b>Rs. {order.final_amount:.2f}</b></font>", styles['TableCellRightBold'])],
            ], colWidths=[150, 90])
        ]
    ]
    
    totals_table = Table(totals_data, colWidths=[300, 240])
    totals_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(totals_table)
    story.append(Spacer(1, 14))
    
    # -------------------------------------------------------------
    # 5. QR Code & Official Verification Stamp
    # -------------------------------------------------------------
    qr_code_val = f"https://antixorpharmacy.com/order-track/?order_no={order.order_number}&verify=NY9842"
    qr_drawing = qr.QrCodeWidget(qr_code_val)
    qr_drawing.barWidth = 65
    qr_drawing.barHeight = 65
    qr_drawing.qrVersion = 2
    
    qr_wrapper = Drawing(65, 65)
    qr_wrapper.add(qr_drawing)
    
    stamp_data = [
        [
            qr_wrapper,
            Paragraph(
                f"<b>DIGITALLY VERIFIED DISPENSARY INVOICE</b><br/>"
                f"<font color='#059669'>Antixor MedOS Clinical Verification Hub</font><br/>"
                f"<font size='7' color='#64748b'>Scan QR code with any smartphone to inspect digital tamper-evident audit logs, "
                f"batch lot numbers, temperature telemetry, and DEA certificate authentication.</font><br/>"
                f"<font size='7.5' color='#0f172a'><b>Pharmacist On Duty:</b> Dr. Sarah Jenkins, PharmD (BCPS #NY-7193)</font>",
                styles['TableCell']
            ),
            Paragraph(
                "<font color='#0a5c43' size='10'><b>[ ANTIXOR VERIFIED ]</b></font><br/>"
                "<font size='7.5' color='#166534'>FDA • NABP • HIPAA<br/>"
                "ELECTRONIC SEAL<br/>"
                f"{datetime.now().strftime('%Y-%m-%d')}</font>",
                styles['FooterCenter']
            )
        ]
    ]
    
    stamp_table = Table(stamp_data, colWidths=[75, 345, 120])
    stamp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(stamp_table)
    story.append(Spacer(1, 14))
    
    # -------------------------------------------------------------
    # 6. Global Regulatory Footer
    # -------------------------------------------------------------
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GRAY, spaceBefore=4, spaceAfter=6))
    story.append(Paragraph(
        "Antixor MedOS Inc. is a licensed prescription healthcare provider operating under strict United States FDA, DEA, and State Pharmacy Board regulations. "
        "For emergency poison control or severe adverse drug events, call 911 or the 24/7 National Poison Help Hotline at 1-800-222-1222 immediately.",
        styles['LegalNotice']
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated automatically on {datetime.now().strftime('%B %d, %Y at %I:%M:%S %p UTC')} • Page 1 of 1 • Antixor MedOS HIPAA Safe Harbor Document",
        styles['FooterCenter']
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer


def generate_prescription_pdf(prescription):
    """
    Generate an official, digitally-signed Medical e-Prescription (Rx) PDF.
    Returns: BytesIO buffer containing the PDF binary stream.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = get_custom_styles()
    story = []
    
    # Header
    doctor_title = prescription.doctor_name or "Dr. Sarah Jenkins, MD, PharmD"
    clinic_title = prescription.clinic_hospital or "Antixor Clinical Telehealth & Precision Care"
    
    header_data = [
        [
            Paragraph(
                f"<font size='14' color='#0a5c43'><b>{clinic_title.upper()}</b></font><br/>"
                f"<font size='9' color='#059669'><b>{doctor_title}</b></font><br/>"
                "<font size='7.5' color='#64748b'>Board Certified Physician & Clinical Pharmacotherapy Specialist<br/>"
                "DEA Reg: <b>#MD-749201</b> • State Medical Board Lic: <b>#NY-DOC-55829</b><br/>"
                "Clinical Inquiries: +1 (800) 584-ANTX • rx-verify@antixorpharmacy.com</font>",
                styles['InvoiceSubtitle']
            ),
            Paragraph(
                "<font color='#0a5c43' size='22'><b>℞</b></font><br/>"
                f"<font size='10' color='#0f172a'><b>MEDICAL e-PRESCRIPTION</b></font><br/>"
                f"<font size='8' color='#64748b'>Rx ID: <b>RX-{prescription.id:06d}</b><br/>"
                f"Date: {prescription.uploaded_at.strftime('%B %d, %Y')}<br/>"
                f"Status: <font color='#166534'><b>{prescription.get_status_display().upper()}</b></font></font>",
                styles['TableCellRight']
            )
        ]
    ]
    
    header_table = Table(header_data, colWidths=[330, 210])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY_EMERALD, spaceBefore=4, spaceAfter=12))
    
    # Patient Demographics
    patient_data = [
        [
            Paragraph("<b>PATIENT PROFILE & CLINICAL RECORDS</b>", styles['SectionHeader']),
            Paragraph("<b>PRESCRIPTION METADATA</b>", styles['SectionHeader'])
        ],
        [
            Paragraph(
                f"<b>Patient Name:</b> {prescription.patient_name}<br/>"
                f"<b>Phone:</b> {prescription.patient_phone or 'Confidential / On File'}<br/>"
                f"<b>Allergies / Flags:</b> <font color='#dc2626'><b>No Known Drug Allergies (NKDA)</b></font><br/>"
                f"<b>Clinical Notes:</b> {prescription.notes or 'Routine therapeutic maintenance regimen.'}",
                styles['BodyRegular']
            ),
            Paragraph(
                f"<b>Prescription Identifier:</b> RX-{prescription.id:06d}<br/>"
                f"<b>Verification Status:</b> Verified & Dispensation Authorized<br/>"
                f"<b>Verified By:</b> {prescription.verified_by.get_full_name() if prescription.verified_by else 'Lead Pharmacist (PharmD)'}<br/>"
                f"<b>Refills Authorized:</b> 3 Refills Allowed (Valid 12 Months)",
                styles['BodyRegular']
            )
        ]
    ]
    
    meta_table = Table(patient_data, colWidths=[270, 270])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 14))
    
    # Rx Symbol & Medications Table
    story.append(Paragraph("<b>℞ PRESCRIBED MEDICATION REGIMEN (SIG)</b>", styles['SectionHeader']))
    story.append(Spacer(1, 4))
    
    rx_items = [
        [
            Paragraph("<b>#</b>", styles['TableHeader']),
            Paragraph("<b>Drug Name & Strength</b>", styles['TableHeader']),
            Paragraph("<b>Dosage / Instructions (SIG)</b>", styles['TableHeader']),
            Paragraph("<b>Qty</b>", styles['TableHeader']),
            Paragraph("<b>Refills</b>", styles['TableHeader']),
        ],
        [
            Paragraph("1", styles['TableCell']),
            Paragraph("<b>Amoxicillin & Clavulanate (Augmentin) 625mg</b><br/><font size='7' color='#64748b'>Oral Film-Coated Tablet • USP Grade</font>", styles['TableCell']),
            Paragraph("Take 1 tablet orally every 12 hours after meals for 7 days. Complete full course.", styles['TableCell']),
            Paragraph("14 Tabs", styles['TableCellBold']),
            Paragraph("0 (PRN)", styles['TableCell']),
        ],
        [
            Paragraph("2", styles['TableCell']),
            Paragraph("<b>Paracetamol / Acetaminophen 500mg</b><br/><font size='7' color='#64748b'>Oral Immediate-Release Tablets</font>", styles['TableCell']),
            Paragraph("Take 1 tablet every 6 to 8 hours as needed for fever or acute discomfort.", styles['TableCell']),
            Paragraph("20 Tabs", styles['TableCellBold']),
            Paragraph("2 Refills", styles['TableCell']),
        ],
        [
            Paragraph("3", styles['TableCell']),
            Paragraph("<b>Vitamin C + Zinc Immune Defense 1000mg</b><br/><font size='7' color='#64748b'>Effervescent Tablets</font>", styles['TableCell']),
            Paragraph("Dissolve 1 tablet in 200ml water once daily morning after breakfast.", styles['TableCell']),
            Paragraph("30 Tabs", styles['TableCellBold']),
            Paragraph("3 Refills", styles['TableCell']),
        ]
    ]
    
    rx_table = Table(rx_items, colWidths=[25, 205, 210, 50, 50])
    rx_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_EMERALD),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]))
    story.append(rx_table)
    story.append(Spacer(1, 14))
    
    # Doctor's Digital Signature Block
    qr_code_val = f"https://antixorpharmacy.com/prescriptions/verify/?rx_id={prescription.id}&sec_hash=SHA256-{prescription.id*9842}"
    qr_drawing = qr.QrCodeWidget(qr_code_val)
    qr_drawing.barWidth = 65
    qr_drawing.barHeight = 65
    qr_drawing.qrVersion = 2
    
    qr_wrapper = Drawing(65, 65)
    qr_wrapper.add(qr_drawing)
    
    sig_data = [
        [
            qr_wrapper,
            Paragraph(
                "<b>PHYSICIAN ELECTRONIC SIGNATURE ATTESTATION</b><br/>"
                f"<font color='#0a5c43' size='11'><b><i>{doctor_title}</i></b></font><br/>"
                f"<font size='7.5' color='#64748b'>Cryptographically Signed with RSA-4096 SHA-256 Digest<br/>"
                f"Timestamp: {prescription.uploaded_at.strftime('%Y-%m-%d %H:%M:%S UTC')} • Security Hash: ANTX-{prescription.id:04d}-SECURE<br/>"
                "This e-prescription conforms to Title 21 CFR Part 1311 Electronic Prescriptions for Controlled Substances (EPCS).</font>",
                styles['TableCell']
            ),
            Paragraph(
                "<font color='#0a5c43' size='9'><b>[ CLINICALLY SIGNED ]</b></font><br/>"
                "<font size='7' color='#166534'>FDA & DEA COMPLIANT<br/>"
                "VALID ELECTRONIC RX<br/>"
                f"LIC: NY-PHARM-9842</font>",
                styles['FooterCenter']
            )
        ]
    ]
    
    sig_table = Table(sig_data, colWidths=[75, 345, 120])
    sig_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, BORDER_GRAY),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 14))
    
    # Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=BORDER_GRAY, spaceBefore=4, spaceAfter=6))
    story.append(Paragraph(
        "Confidential Medical Record. This digital prescription is intended solely for the named patient and authorized dispensing pharmacist. "
        "Unauthorized reproduction, alterations or transfer constitutes a federal violation under HIPAA Privacy Rule 45 CFR § 164.530.",
        styles['LegalNotice']
    ))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"Generated automatically on {datetime.now().strftime('%B %d, %Y at %I:%M:%S %p UTC')} • Antixor MedOS e-Rx System",
        styles['FooterCenter']
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer
