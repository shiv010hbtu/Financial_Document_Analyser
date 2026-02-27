## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

# FIX 1: Removed "from crewai_tools import tools" — wrong/unused import that doesn't exist
from crewai_tools import SerperDevTool          # FIX 2: Correct import path for SerperDevTool
from crewai.tools import tool                   # FIX 3: Import @tool decorator — required for CrewAI agent tool discovery
from pypdf import PdfReader                     # FIX 4: PdfReader was never imported — "Pdf" class doesn't exist in any installed package

## Creating search tool
# FIX 5: Added SERPER_API_KEY validation with clear error message instead of silent failure
if not os.getenv("SERPER_API_KEY"):
    raise EnvironmentError(
        "SERPER_API_KEY is not set. Please add it to your .env file.\n"
        "Get your free key at: https://serper.dev"
    )
search_tool = SerperDevTool()

## Creating custom PDF reader tool
class FinancialDocumentTool():

    @tool("Financial Document Reader")          # FIX 6: Added @tool decorator — CrewAI cannot discover or call tools without it
    def read_data_tool(path: str = 'data/sample.pdf') -> str:
        # FIX 7: Removed "async" — CrewAI tools must be synchronous, async tools are silently skipped
        # FIX 8: Removed "self" replaced with proper @tool static usage — @tool decorated methods don't use self
        """Tool to read and extract text data from a PDF financial document.

        Args:
            path (str): Path of the PDF file. Defaults to 'data/sample.pdf'.

        Returns:
            str: Full extracted text content of the financial document.
        """
        # FIX 9: Replaced non-existent "Pdf(file_path=path).load()" with correct pypdf API
        # pypdf reads via PdfReader — pages accessed via reader.pages[i].extract_text()
        if not os.path.exists(path):
            return f"Error: File not found at path '{path}'. Please check the file path and try again."

        try:
            reader = PdfReader(path)
            full_report = ""

            for page in reader.pages:
                content = page.extract_text()
                if not content:
                    continue

                # Clean and format the financial document data
                while "\n\n" in content:
                    content = content.replace("\n\n", "\n")

                full_report += content + "\n"

            if not full_report.strip():
                return "Error: No text could be extracted from the PDF. The file may be scanned or image-based."

            return full_report

        except Exception as e:
            return f"Error reading PDF: {str(e)}"


## Creating Investment Analysis Tool
class InvestmentTool:

    @tool("Investment Analyzer")                # FIX 10: Added missing @tool decorator
    def analyze_investment_tool(financial_document_data: str) -> str:
        # FIX 11: Removed "async" — must be synchronous for CrewAI
        # FIX 12: Removed missing "self" — @tool decorated methods don't use self
        """Analyze financial document data and extract key investment indicators.

        Args:
            financial_document_data (str): Raw extracted text from a financial document.

        Returns:
            str: Structured investment analysis with key metrics and indicators.
        """
        # FIX 13: Replaced TODO stub with actual implementation
        if not financial_document_data or not financial_document_data.strip():
            return "Error: No financial data provided for analysis."

        # Clean up the data format — remove extra whitespace
        processed_data = financial_document_data
        while "  " in processed_data:
            processed_data = processed_data.replace("  ", " ")
        processed_data = processed_data.strip()

        # Extract key investment sections from document text
        lines = processed_data.split("\n")
        investment_keywords = [
            "revenue", "net income", "earnings", "eps", "ebitda",
            "gross profit", "operating income", "cash flow", "guidance",
            "outlook", "growth", "margin", "dividend", "buyback", "capex"
        ]

        relevant_sections = []
        for line in lines:
            if any(keyword in line.lower() for keyword in investment_keywords):
                relevant_sections.append(line.strip())

        if not relevant_sections:
            return (
                "Investment Analysis: No standard financial metrics found in document.\n"
                "Raw document has been passed to the investment advisor agent for manual review."
            )

        analysis_output = "=== INVESTMENT ANALYSIS — KEY METRICS EXTRACTED ===\n\n"
        analysis_output += "\n".join(relevant_sections[:50])  # Cap at 50 most relevant lines
        analysis_output += "\n\n=== END OF EXTRACTED INVESTMENT DATA ==="

        return analysis_output


## Creating Risk Assessment Tool
class RiskTool:

    @tool("Risk Assessment Analyzer")          # FIX 14: Added missing @tool decorator
    def create_risk_assessment_tool(financial_document_data: str) -> str:
        # FIX 15: Removed "async" — must be synchronous for CrewAI
        # FIX 16: Removed missing "self" — @tool decorated methods don't use self
        """Extract and structure risk-relevant data from a financial document.

        Args:
            financial_document_data (str): Raw extracted text from a financial document.

        Returns:
            str: Structured risk-relevant sections including debt, liabilities, and risk factors.
        """
        # FIX 17: Replaced TODO stub with actual implementation
        if not financial_document_data or not financial_document_data.strip():
            return "Error: No financial data provided for risk assessment."

        processed_data = financial_document_data.strip()
        lines = processed_data.split("\n")

        risk_keywords = [
            "risk", "debt", "liability", "liabilities", "interest expense",
            "default", "covenant", "credit", "liquidity", "cash and cash equivalents",
            "current ratio", "leverage", "volatility", "regulatory", "litigation",
            "impairment", "write-off", "contingent", "exposure", "uncertainty",
            "inflation", "supply chain", "competition", "market risk"
        ]

        risk_sections = []
        for line in lines:
            if any(keyword in line.lower() for keyword in risk_keywords):
                risk_sections.append(line.strip())

        if not risk_sections:
            return (
                "Risk Assessment: No explicit risk factors found in document text.\n"
                "Document passed to risk assessor agent for comprehensive manual review."
            )

        risk_output = "=== RISK ASSESSMENT — KEY RISK FACTORS EXTRACTED ===\n\n"
        risk_output += "\n".join(risk_sections[:50])  # Cap at 50 most relevant lines
        risk_output += "\n\n=== END OF EXTRACTED RISK DATA ==="

        return risk_output