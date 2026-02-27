## Importing libraries and files
from crewai import Task

# FIX 1: Added missing imports — investment_advisor and risk_assessor were never imported
# FIX 2: verifier was imported but never used — now properly used in verification task
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool, FinancialDocumentTool

## Creating a task to analyze the financial document
analyze_financial_document = Task(
    # FIX 3 (Prompt): Original description told agent to "maybe solve query", "use imagination",
    # "make up recommendations", and "include creative financial URLs" — replaced with
    # a precise, document-grounded analysis instruction
    description=(
        "Carefully read and analyze the financial document provided for the following query: {query}.\n"
        "Use the FinancialDocumentTool to extract and review all relevant sections of the document.\n"
        "Identify and summarize the following from the document:\n"
        "  - Key financial metrics: revenue, net income, EPS, EBITDA, gross margin\n"
        "  - Year-over-year and quarter-over-quarter growth trends\n"
        "  - Cash flow position and capital expenditure patterns\n"
        "  - Significant business developments, guidance, or management commentary\n"
        "  - Any red flags or areas of concern in the financials\n"
        "All findings must be grounded strictly in the document. Do not fabricate figures or assume data "
        "that is not present. Clearly note if any expected metric is missing from the document."
    ),

    # FIX 4 (Prompt): Original expected_output demanded made-up URLs, self-contradictions, and
    # jargon without understanding — replaced with structured, professional output format
    expected_output=(
        "A structured financial analysis report containing:\n"
        "1. Executive Summary — 3-5 sentence overview of the company's financial health\n"
        "2. Key Financial Metrics Table — revenue, net income, EPS, EBITDA with period comparisons\n"
        "3. Trend Analysis — growth patterns and notable changes with specific figures cited\n"
        "4. Business Highlights — key developments, product updates, strategic initiatives\n"
        "5. Areas of Concern — any financial weaknesses or risks identified in the document\n"
        "6. Data Sources — cite specific sections/pages of the document for all major claims\n"
        "All figures must reference the source document. No fabricated data or external assumptions."
    ),

    agent=financial_analyst,
    tools=[FinancialDocumentTool.read_data_tool, search_tool],  # FIX 5: Added search_tool — was imported but never assigned to any task
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis = Task(
    # FIX 6 (Prompt): Original description told agent to "ignore query", "make up what numbers mean",
    # "recommend expensive products regardless of financials", "mix up ratios for variety" —
    # replaced with evidence-based, query-focused investment analysis instruction
    description=(
        "Based on the financial document analysis, provide an objective investment assessment "
        "addressing the user's query: {query}.\n"
        "Use the search_tool to gather current market context, analyst consensus, and sector benchmarks.\n"
        "Your analysis must cover:\n"
        "  - Valuation assessment: P/E, P/B, EV/EBITDA compared to sector averages\n"
        "  - Revenue and earnings growth trajectory vs market expectations\n"
        "  - Competitive positioning and moat evaluation\n"
        "  - Dividend policy and shareholder return programs if applicable\n"
        "  - Macroeconomic factors relevant to the company's sector\n"
        "Base all recommendations strictly on documented financial data and verified market information. "
        "Disclose that this analysis is informational and not a substitute for licensed financial advice."
    ),

    # FIX 7 (Prompt): Original expected_output demanded "10 products they don't need",
    # "contradictory strategies", "crypto from obscure exchanges", "fake market research" —
    # replaced with a clear, honest, compliant investment recommendation format
    expected_output=(
        "A professional investment analysis report containing:\n"
        "1. Investment Thesis — clear BUY / HOLD / SELL recommendation with primary rationale\n"
        "2. Valuation Analysis — key multiples compared to sector peers with cited benchmarks\n"
        "3. Growth Drivers — specific catalysts from the financial document supporting the view\n"
        "4. Key Risks to Thesis — factors that could invalidate the recommendation\n"
        "5. Suitable Investor Profile — risk tolerance and time horizon this fits\n"
        "6. Compliance Disclaimer — note that recommendations are informational only\n"
        "All claims must reference specific figures from the financial document or verified sources. "
        "No fabricated data, fake research, or unverified market claims."
    ),

    # FIX 8: investment_analysis was incorrectly assigned to financial_analyst — correct agent is investment_advisor
    agent=investment_advisor,
    tools=[search_tool],
    async_execution=False,
)

## Creating a risk assessment task
risk_assessment = Task(
    # FIX 9 (Prompt): Original description said "maybe based on document maybe not",
    # "assume extreme risk regardless of actual status", "ignore query", "don't worry about
    # regulatory compliance" — replaced with rigorous, document-based risk evaluation
    description=(
        "Conduct a thorough, data-driven risk assessment of the financial document "
        "in response to the user's query: {query}.\n"
        "Use the FinancialDocumentTool to extract risk-relevant financial data and "
        "search_tool to benchmark against industry standards.\n"
        "Evaluate the following risk categories:\n"
        "  - Market Risk: revenue concentration, cyclicality, sector exposure\n"
        "  - Credit Risk: debt levels, interest coverage ratio, credit ratings if available\n"
        "  - Liquidity Risk: current ratio, cash runway, short-term obligations\n"
        "  - Operational Risk: supply chain, regulatory, geopolitical exposures\n"
        "  - Execution Risk: management guidance vs actual performance history\n"
        "Assign evidence-based severity levels (Low / Medium / High) to each risk category "
        "with specific data points from the document. Follow standard risk management frameworks. "
        "Do not fabricate risk scenarios or apply extreme assessments without documentary evidence."
    ),

    # FIX 10 (Prompt): Original expected_output demanded "dangerous strategies for everyone",
    # "made-up hedging strategies", "fake research from made-up institutions",
    # "impossible risk targets" — replaced with a balanced, actionable risk report format
    expected_output=(
        "A comprehensive risk assessment report containing:\n"
        "1. Risk Summary — overall risk profile (Low / Medium / High) with one-paragraph justification\n"
        "2. Risk Matrix — table of each risk category with severity, evidence, and mitigation suggestion\n"
        "3. Key Risk Indicators — specific financial ratios and thresholds from the document\n"
        "4. Scenario Analysis — base case, bull case, and bear case outcomes with documented assumptions\n"
        "5. Mitigation Recommendations — actionable, realistic hedging or diversification strategies\n"
        "6. Regulatory Considerations — any compliance or regulatory risks noted in the document\n"
        "All risk ratings must be justified with specific figures from the document. "
        "No fabricated institutions, impossible targets, or alarmist claims without evidence."
    ),

    # FIX 11: risk_assessment was incorrectly assigned to financial_analyst — correct agent is risk_assessor
    agent=risk_assessor,
    tools=[FinancialDocumentTool.read_data_tool, search_tool],
    async_execution=False,
)

# FIX 12: Removed incorrect 4-space indentation before Task() — would cause IndentationError
verification = Task(
    # FIX 13 (Prompt): Original description said "just guess", "hallucinate financial terms",
    # "don't actually read the file carefully" — replaced with rigorous document validation instruction
    description=(
        "Carefully verify that the uploaded document is a legitimate financial report "
        "before it proceeds to analysis.\n"
        "Use the FinancialDocumentTool to read and inspect the document contents.\n"
        "Confirm the document contains at minimum two of the following:\n"
        "  - Income Statement (revenue, expenses, net income)\n"
        "  - Balance Sheet (assets, liabilities, equity)\n"
        "  - Cash Flow Statement (operating, investing, financing activities)\n"
        "  - Financial notes, auditor's report, or management discussion section\n"
        "Also verify:\n"
        "  - The document contains a clearly identifiable company name and reporting period\n"
        "  - Financial figures are internally consistent (e.g. net income matches retained earnings)\n"
        "  - No obvious signs of tampering, placeholder text, or non-financial content\n"
        "If the document fails verification, clearly state why and reject it for further analysis."
    ),

    # FIX 14 (Prompt): Original expected_output said "say it's probably financial even if not",
    # "make up confident-sounding analysis", "add random file path that sounds official" —
    # replaced with honest, structured verification output
    expected_output=(
        "A clear verification report containing:\n"
        "1. Verification Result — PASS or FAIL with a one-sentence summary reason\n"
        "2. Document Identity — company name, reporting period, document type identified\n"
        "3. Financial Statements Found — list of statements confirmed present in the document\n"
        "4. Consistency Check — note any figures that were verified as internally consistent\n"
        "5. Issues Found — any missing sections, inconsistencies, or red flags (if applicable)\n"
        "6. Recommendation — whether to proceed with analysis or request a corrected document\n"
        "Do not approve documents that lack clear financial statements. "
        "Do not fabricate verification results or invent official-sounding file references."
    ),

    # FIX 15: verification was incorrectly assigned to financial_analyst — correct agent is verifier
    agent=verifier,
    tools=[FinancialDocumentTool.read_data_tool],
    async_execution=False
)
