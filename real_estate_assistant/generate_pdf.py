# real_estate_assistant/generate_pdf.py

# Ensure you have reportlab installed: pip install reportlab
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False
    print("Warning: reportlab library not found. PDF generation will not be available. Install with 'pip install reportlab'")

def create_pdf_report(report_content_text: str, output_filename: str = "real_estate_report.pdf") -> str:
    """
    Generates a PDF report from the given text content.
    Returns the path to the generated PDF.
    """
    if not REPORTLAB_AVAILABLE:
        print("Cannot generate PDF: reportlab library is missing.")
        return f"Error: PDF generation failed due to missing reportlab. Content:\n{report_content_text}"

    doc = SimpleDocTemplate(output_filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = styles['h1']
    title_text = "Real Estate Analysis Report" # You can make this dynamic
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 0.2 * inch))

    # Body Text
    # Split the report content by lines and add as paragraphs
    # This handles basic formatting like newlines.
    # For more complex markdown-like structures, more parsing would be needed.
    normal_style = styles['Normal']
    report_lines = report_content_text.split('\n')
    for line in report_lines:
        if line.strip() == "": # Handle empty lines as spacers or skip
            story.append(Spacer(1, 0.1 * inch))
        else:
            # Basic bold/heading handling (very rudimentary)
            current_style = normal_style
            if line.startswith("## "):
                current_style = styles['h2']
                line = line[3:]
            elif line.startswith("**") and line.endswith("**"):
                 # This is a bit simplistic for bold, ReportLab has better ways for inline styles
                 # For now, just make it a distinct paragraph.
                line = line[2:-2] # Remove asterisks
                # Consider creating a custom 'Bold' style if needed often
            
            p = Paragraph(line, current_style)
            story.append(p)
    
    try:
        doc.build(story)
        print(f"PDF report generated successfully: {output_filename}")
        return output_filename
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return f"Error: PDF generation failed. {e}"

if __name__ == '__main__':
    if REPORTLAB_AVAILABLE:
        sample_report_text = """## Property Overview
**Address:** 123 Main St, Anytown, USA
**Price:** $500,000
This is a lovely property in a prime location. It features 3 bedrooms and 2 bathrooms.

## Market Comparables
- 125 Main St: Sold for $490,000
- 120 Main St: Listed at $510,000

## Analysis
The property seems fairly priced based on recent sales and current listings in the neighborhood.
Consider offering slightly below asking to account for minor repairs needed.
"""
        pdf_path = create_pdf_report(sample_report_text, output_filename="sample_real_estate_report.pdf")
        print(f"Sample PDF report saved to: {pdf_path}")
    else:
        print("Skipping PDF generation example because reportlab is not installed.")

