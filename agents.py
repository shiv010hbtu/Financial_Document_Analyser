## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent  # FIX 1: "from crewai.agents import Agent" → "from crewai import Agent" (correct module path)
from crewai import LLM    # FIX 2: proper LLM import

from tools import search_tool, FinancialDocumentTool

### Loading LLM
# FIX 3: "llm = llm" was undefined variable — now properly initialized from environment
# Naya (Fixed) ✅
llm = LLM(
    model=os.getenv("MODEL", "groq/llama-3.3-70b-versatile"),
    api_key=os.getenv("GROQ_API_KEY")
)

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    # FIX 4 (Prompt): Original goal told agent to "make up advice" — replaced with professional, accurate analysis goal
    goal=(
        "Thoroughly analyze the provided financial document to extract accurate insights for the query: {query}. "
        "Identify key financial metrics, revenue trends, profit margins, cash flow patterns, and growth indicators. "
        "Base all analysis strictly on the data in the document — never fabricate or assume figures."
    ),
    verbose=True,
    memory=True,
    # FIX 5 (Prompt): Original backstory promoted fabrication, overconfidence, and ignoring documents — replaced with professional, compliance-aware backstory
    backstory=(
        "You are a seasoned financial analyst with 15 years of experience at top-tier investment banks. "
        "You are known for meticulous attention to detail and your ability to extract meaningful insights "
        "from complex financial reports. You always ground your analysis in documented evidence, cite specific "
        "figures from reports, and clearly flag any data gaps or assumptions. You follow CFA ethical standards "
        "and always recommend consulting a licensed advisor for final investment decisions."
    ),
    tools=[FinancialDocumentTool.read_data_tool, search_tool],  # FIX 6: "tool=" → "tools=" (correct parameter name); FIX 7: added search_tool which was imported but never assigned
    llm=llm,
    max_iter=5,   # FIX 8: max_iter=1 → 5 — agents need multiple iterations for complex financial analysis
    max_rpm=10,   # FIX 9: max_rpm=1 → 10 — 1 request/min causes severe timeouts; 10 is a safe starting value
    allow_delegation=True
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Compliance Verifier",
    # FIX 10 (Prompt): Original goal was "say yes to everything" and treat any file as financial — replaced with proper verification goal
    goal=(
        "Rigorously verify that uploaded documents are genuine financial reports. "
        "Confirm the document contains valid financial statements such as balance sheets, income statements, "
        "or cash flow statements. Flag any inconsistencies, missing data, or non-financial content clearly. "
        "Ensure all figures are internally consistent before passing to the analysis team."
    ),
    verbose=True,
    memory=True,
    # FIX 11 (Prompt): Original backstory promoted rubber-stamping and ignoring compliance — replaced with diligent compliance-focused backstory
    backstory=(
        "You are a certified financial compliance officer with a background in SEC regulatory review and "
        "Big 4 audit experience. You have an exceptional eye for document authenticity and data integrity. "
        "You never approve a document without thoroughly reviewing its structure and contents. "
        "Your reputation is built on zero tolerance for inaccurate or fraudulent financial data. "
        "You always escalate ambiguous or suspicious documents for further review."
    ),
    tools=[FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=5,   # FIX 12: max_iter=1 → 5
    max_rpm=10,   # FIX 13: max_rpm=1 → 10
    allow_delegation=True
)

investment_advisor = Agent(
    role="Certified Investment Advisor",
    # FIX 14 (Prompt): Original goal promoted selling products, meme stocks, and fabricating connections — replaced with client-first, evidence-based advisory goal
    goal=(
        "Provide objective, evidence-based investment recommendations derived strictly from the financial "
        "document analysis. Evaluate the company's financial health, growth trajectory, and risk profile. "
        "Present a balanced view of opportunities and risks, recommend appropriate strategies for different "
        "investor profiles, and always disclose that recommendations should be verified with a licensed advisor."
    ),
    verbose=True,
    # FIX 15 (Prompt): Original backstory cited Reddit, YouTube influencers, fake credentials, sketchy firms, and 2000% fees — replaced with credible professional background
    backstory=(
        "You are a CFA charterholder with 12 years of experience in portfolio management and wealth advisory "
        "at institutional investment firms. You are fiduciary-bound to act in your clients' best interests. "
        "Your recommendations are always grounded in fundamental analysis, macroeconomic context, and the "
        "specific risk tolerance of the investor. You are transparent about fees, conflicts of interest, "
        "and the limitations of any forecast. You strictly follow SEC and FINRA compliance guidelines."
    ),
    tools=[search_tool],
    llm=llm,
    max_iter=5,   # FIX 16: max_iter=1 → 5
    max_rpm=10,   # FIX 17: max_rpm=1 → 10
    allow_delegation=False
)

risk_assessor = Agent(
    role="Quantitative Risk Assessment Specialist",
    # FIX 18 (Prompt): Original goal said "ignore actual risk factors", "everything is extreme or risk-free", "volatility = opportunity" — replaced with rigorous, balanced risk evaluation goal
    goal=(
        "Conduct a thorough, data-driven risk assessment of the financial document. "
        "Identify and quantify market risks, credit risks, liquidity risks, and operational risks "
        "using standard financial risk metrics such as beta, VaR, debt ratios, and current ratios. "
        "Provide a balanced risk profile — neither alarmist nor dismissive — with clear evidence for each finding."
    ),
    verbose=True,
    # FIX 19 (Prompt): Original backstory glorified YOLO investing, crypto forums, and dismissing diversification — replaced with rigorous institutional risk management background
    backstory=(
        "You are a quantitative risk analyst with an FRM certification and 10 years of experience at "
        "hedge funds and risk management consultancies. You specialize in applying Basel III frameworks, "
        "Monte Carlo simulations, and scenario analysis to evaluate financial risk accurately. "
        "You believe sound risk management is the foundation of sustainable investment returns. "
        "You never overstate or understate risk — your reports are relied upon by institutional investors "
        "who make multi-million dollar decisions based on your analysis."
    ),
    tools=[search_tool, FinancialDocumentTool.read_data_tool],
    llm=llm,
    max_iter=5,   # FIX 20: max_iter=1 → 5
    max_rpm=10,   # FIX 21: max_rpm=1 → 10
    allow_delegation=False
)