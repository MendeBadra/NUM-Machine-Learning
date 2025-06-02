# real_estate_assistant/generate_pdf.py

# Ensure you have weasyprint installed: pip install weasyprint
import pandas as pd
import os
import re
from datetime import datetime

try:
    from weasyprint import HTML, CSS
    from weasyprint.text.fonts import FontConfiguration
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("Warning: weasyprint library not found. PDF generation will not be available. Install with 'pip install weasyprint'")

def create_pdf_report(report_data: dict, filename: str = "real_estate_report.pdf") -> str:
    """
    Creates a structured PDF report with header, market analysis, and conclusion sections using weasyprint.
    """
    if not WEASYPRINT_AVAILABLE:
        print("Cannot generate PDF: weasyprint library is missing.")
        return f"Error: PDF generation failed due to missing weasyprint. Content:\n{report_data}"

    try:
        # Create HTML content
        html_content = generate_html_report(report_data)
        
        # Create PDF using weasyprint
        font_config = FontConfiguration()
        html_doc = HTML(string=html_content)
        
        # Generate PDF
        html_doc.write_pdf(filename, font_config=font_config)
        
        print(f"PDF report generated: {filename}")
        return os.path.abspath(filename)
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return f"Error: PDF generation failed. {e}"

def generate_html_report(report_data: dict) -> str:
    """
    Generates HTML content for the PDF report.
    """
    # Get current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # Generate market data table HTML if available
    market_data_table = ""
    if report_data.get("market_data_df") is not None:
        df = report_data["market_data_df"]
        market_data_table = f"""
        <div class="market-data-section">
            <h2>Зах Зээлийн Өгөгдөл</h2>
            <table class="market-table">
                <thead>
                    <tr>
                        <th>Дүүрэг</th>
                        <th>2025 Мар (MNT сая)</th>
                        <th>Өөрчлөлт</th>
                        <th>Хувь (%)</th>
                        <th>Төрөл</th>
                    </tr>
                </thead>
                <tbody>
                    {generate_table_rows(df)}
                </tbody>
            </table>
        </div>
        """
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Үл Хөдлөх Хөрөнгийн Тайлан</title>
        <style>
            @page {{
                size: A4;
                margin: 2cm;
            }}
            
            body {{
                font-family: 'Times New Roman', 'DejaVu Serif', serif;
                margin: 0;
                padding: 0;
                line-height: 1.6;
                color: #333;
                font-size: 12pt;
            }}
            
            .header {{
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #2c5aa0;
                padding-bottom: 20px;
            }}
            
            .main-title {{
                color: #2c5aa0;
                font-size: 22pt;
                font-weight: bold;
                margin-bottom: 10px;
            }}
            
            .property-info {{
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 25px;
                border: 1px solid #dee2e6;
            }}
            
            .property-info h2 {{
                color: #28a745;
                font-size: 16pt;
                margin-bottom: 15px;
                border-bottom: 1px solid #28a745;
                padding-bottom: 5px;
            }}
            
            .property-table {{
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
            }}
            
            .property-table td {{
                padding: 8px 12px;
                border: 1px solid #ddd;
                vertical-align: top;
            }}
            
            .property-table td:first-child {{
                background-color: #e9ecef;
                font-weight: bold;
                width: 25%;
            }}
            
            .market-data-section {{
                margin: 25px 0;
                page-break-inside: avoid;
            }}
            
            .market-data-section h2 {{
                color: #28a745;
                font-size: 16pt;
                margin-bottom: 15px;
                border-bottom: 1px solid #28a745;
                padding-bottom: 5px;
            }}
            
            .market-table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 10pt;
                margin-bottom: 20px;
            }}
            
            .market-table th, .market-table td {{
                padding: 6px 8px;
                text-align: left;
                border: 1px solid #ddd;
            }}
            
            .market-table th {{
                background-color: #2c5aa0;
                color: white;
                font-weight: bold;
            }}
            
            .market-table tr:nth-child(even) {{
                background-color: #f8f9fa;
            }}
            
            .section {{
                margin: 25px 0;
                page-break-inside: avoid;
            }}
            
            .section h2 {{
                color: #28a745;
                font-size: 16pt;
                margin-bottom: 15px;
                border-bottom: 1px solid #28a745;
                padding-bottom: 5px;
            }}
            
            .content {{
                text-align: justify;
                margin-bottom: 15px;
                line-height: 1.7;
            }}
            
            .footer {{
                margin-top: 30px;
                padding-top: 15px;
                border-top: 1px solid #ddd;
                font-size: 10pt;
                color: #666;
            }}
            
            .price-highlight {{
                color: #dc3545;
                font-weight: bold;
                font-size: 14pt;
            }}
            
            .page-break {{
                page-break-before: always;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="main-title">ҮЛ ХӨДЛӨХ ХӨРӨНГИЙН ШИНЖИЛГЭЭНИЙ ТАЙЛАН</div>
        </div>
        
        <div class="property-info">
            <h2>Орон Сууцны Мэдээлэл</h2>
            <table class="property-table">
                <tr>
                    <td>Гарчиг:</td>
                    <td>{report_data.get('title', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Үнэ:</td>
                    <td class="price-highlight">{report_data.get('price', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Талбай:</td>
                    <td>{report_data.get('area', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Байршил:</td>
                    <td>{format_location(report_data.get('location', 'N/A'))}</td>
                </tr>
            </table>
        </div>
        
        {market_data_table}
        
        <div class="section">
            <h2>Зах Зээлийн Шинжилгээ</h2>
            <div class="content">
                {format_content(report_data.get('market_analysis', 'Зах зээлийн шинжилгээ байхгүй байна.'))}
            </div>
        </div>
        
        <div class="section">
            <h2>Дүгнэлт ба Зөвлөмж</h2>
            <div class="content">
                {format_content(report_data.get('conclusion', 'Дүгнэлт байхгүй байна.'))}
            </div>
        </div>
        
        <div class="footer">
            <p>Тайлан үүсгэсэн огноо: {timestamp}</p>
            {f'<p>Эх сурвалж: <span style="word-break: break-all;">{report_data.get("url", "")}</span></p>' if report_data.get("url") else ''}
        </div>
    </body>
    </html>
    """
    
    return html_template

def generate_table_rows(df: pd.DataFrame) -> str:
    """
    Generates HTML table rows from pandas DataFrame.
    """
    rows = ""
    for _, row in df.iterrows():
        rows += f"""
        <tr>
            <td>{row.get('District', 'N/A')}</td>
            <td>{row.get('2025 Mar', 'N/A')}</td>
            <td>{row.get('Value', 'N/A')}</td>
            <td>{row.get('Percent', 'N/A')}</td>
            <td>{row.get('Type', 'N/A')}</td>
        </tr>
        """
    return rows

def format_location(location: str) -> str:
    """
    Format location text for better display in PDF.
    """
    if len(location) > 300:
        return location[:300] + "..."
    return location

def format_content(content: str) -> str:
    """
    Format content for HTML display, handling markdown formatting and converting to HTML.
    """
    if not content:
        return ""
    
    # Convert markdown headers to HTML
    content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
    content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
    content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
    
    # Convert markdown bold text
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    content = re.sub(r'__(.*?)__', r'<strong>\1</strong>', content)
    
    # Convert markdown italic text
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    content = re.sub(r'_(.*?)_', r'<em>\1</em>', content)
    
    # Convert markdown code blocks
    content = re.sub(r'```(.*?)```', r'<pre><code>\1</code></pre>', content, flags=re.DOTALL)
    content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
    
    # Handle bullet points (both - and * markers)
    content = re.sub(r'^[\s]*[-*+]\s+(.*?)$', r'<li>\1</li>', content, flags=re.MULTILINE)
    
    # Wrap consecutive list items in <ul> tags
    content = re.sub(r'(<li>.*?</li>(?:\s*<li>.*?</li>)*)', r'<ul>\1</ul>', content, flags=re.DOTALL)
    
    # Handle numbered lists
    content = re.sub(r'^[\s]*(\d+\.)\s+(.*?)$', r'<li value="\1">\2</li>', content, flags=re.MULTILINE)
    content = re.sub(r'<li value="(\d+)\.">(.*?)</li>', r'<li>\2</li>', content)
    
    # Wrap numbered list items in <ol> tags
    content = re.sub(r'(<li>(?:(?!<ul>|<ol>).*?)</li>(?:\s*<li>(?:(?!<ul>|<ol>).*?)</li>)*)', 
                    lambda m: f'<ol>{m.group(1)}</ol>' if re.search(r'^\d+\.', m.group(0)) else m.group(0), 
                    content, flags=re.DOTALL)
    
    # Convert line breaks to HTML breaks (but not inside lists or other block elements)
    lines = content.split('\n')
    formatted_lines = []
    in_block = False
    
    for line in lines:
        stripped = line.strip()
        
        # Check if we're entering or exiting a block element
        if any(tag in stripped for tag in ['<ul>', '<ol>', '<li>', '<h1>', '<h2>', '<h3>', '<pre>', '<blockquote>']):
            in_block = True
        elif any(tag in stripped for tag in ['</ul>', '</ol>', '</li>', '</h1>', '</h2>', '</h3>', '</pre>', '</blockquote>']):
            in_block = False
        
        # Add <br> for non-empty lines that aren't block elements
        if stripped and not in_block and not any(tag in stripped for tag in ['<ul>', '<ol>', '<li>', '<h1>', '<h2>', '<h3>', '<pre>', '<blockquote>', '</ul>', '</ol>', '</li>', '</h1>', '</h2>', '</h3>', '</pre>', '</blockquote>']):
            formatted_lines.append(stripped + '<br>')
        else:
            formatted_lines.append(stripped)
    
    content = '\n'.join(formatted_lines)
    
    # Clean up extra <br> tags
    content = re.sub(r'<br>\s*<br>', '<br>', content)
    content = re.sub(r'<br>\s*$', '', content)
    
    # Handle blockquotes (lines starting with >)
    content = re.sub(r'^>\s+(.*?)$', r'<blockquote>\1</blockquote>', content, flags=re.MULTILINE)
    
    return content

if __name__ == '__main__':
    if WEASYPRINT_AVAILABLE:
        # Sample market data
        sample_df = pd.DataFrame({
            'District': ['Bayangol', 'Bayanzurkh', 'Songinokhairkhan', 'Sukhbaatar'],
            '2025 Mar': [4.41, 4.04, 3.33, 5.44],
            'Value': [0.64, 0.40, 0.62, 1.52],
            'Percent': [17.0, 11.0, 23.0, 38.7],
            'Type': ['New', 'New', 'New', 'New']
        })
        
        sample_report_data = {
            "title": "Бгд төмөр замд 2 өрөө 49.5мкв байр",
            "price": "MNT 239,000,000",
            "area": "49.5 м²",
            "location": "2021 онд ашиглалтад орсон. байршил БГД 3-р хороо, нарны гүүрний баруун талд 73-р сургуулийн урь талд байрладаг",
            "market_analysis": "Энэ орон сууцны үнэ зах зээлийн дундаж үнээс доогуур байна. Баянгол дүүргийн дундаж үнэтэй харьцуулахад энэ нь сайн зардал болж байна.",
            "conclusion": "Сайн зардал гэж үзэж болно. Байршил сайн, үнэ хямд байна.",
            "url": "https://www.unegui.mn/adv/9129580_tomor-zamd-2-oroo-zarna/",
            "market_data_df": sample_df
        }
        pdf_path = create_pdf_report(sample_report_data, filename="sample_real_estate_report.pdf")
        print(f"Sample PDF report saved to: {pdf_path}")
    else:
        print("Skipping PDF generation example because weasyprint is not installed.")

