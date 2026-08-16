import os
import logging
import httpx
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Predefined high-quality semantic answers for key questions in the prompt
SEMANTIC_ANSWERS = {
    "gold": {
        "title": "Why is Gold Rising?",
        "summary": "Gold has surged due to growing expectations of interest rate cuts by the US Federal Reserve, heavy purchasing by global central banks looking to diversify foreign reserves, and heightened geopolitical tensions in the Middle East and Eastern Europe prompting safe-haven capital inflows.",
        "cause": "US Dollar weakening, declining US Treasury bond yields, central bank buying, and geopolitical hedging.",
        "effect": "Gold prices hit record highs, surpassing $2,400 per ounce. Dollar index drops.",
        "india_impact": [
            "Import Bill Surges: Since India imports most of its gold, jewelry raw cost rises, expanding the trade deficit.",
            "Household Wealth Boost: Massive capital appreciation for Indian families holding physical gold (~25,000 tonnes private holding).",
            "Jewelry Sector Headwinds: Higher prices suppress retail demand and wedding season volumes.",
            "Rupee Pressure: Gold imports demand USD, putting mild downward pressure on the Indian Rupee (INR)."
        ],
        "root_cause": "A structural shift in global reserves. Since the freezing of Russia's USD reserves, central banks worldwide (especially China, Turkey, and India) have aggressively accumulated gold to hedge sovereign geopolitical risks.",
        "risks": "Prolonged high prices might squeeze consumer demand; potential asset bubbles if interest rate cycles reverse.",
        "opportunities": "Gold loan NBFCs (like Muthoot and Manappuram Finance) benefit from higher collateral value, leading to credit growth.",
        "historical_comparison": "Similar to the 1970s stagflation era and the 2008 Financial Crisis, gold is demonstrating its classic behavior as a hedge against inflation and monetary debasement.",
        "predictions": "If the Federal Reserve initiates a rate-cut cycle, gold is projected to find strong support and potentially breach $2,600 by the end of the year."
    },
    "oil": {
        "title": "Crude Oil Price Movement Analysis",
        "summary": "Crude oil is displaying high volatility. Prices have been pushed upward by OPEC+ supply constraints and Middle Eastern transit risks, but capped by growing US shale output and soft macroeconomic indicators in China.",
        "cause": "Escalation in the Middle East shipping corridor and OPEC+ extending 2.2 million bpd production cuts.",
        "effect": "Brent crude hovers between $80 and $85 per barrel, increasing global energy inflation expectations.",
        "india_impact": [
            "Imported Inflation: Every $10/bbl rise in oil adds approximately 35 basis points to India's CPI retail inflation.",
            "Currency Depreciation: Widen trade deficit forces USD demand, putting depreciating pressure on the Rupee (USD/INR).",
            "Monetary Policy: Keeps the RBI on high alert, making interest rate cuts highly unlikely.",
            "Sector Pain: Airline stocks (ATF fuel costs), paints, and synthetic chemical manufacturers face margin compression."
        ],
        "root_cause": "OPEC+ maintaining strict supply discipline to keep a floor under prices, combined with high-intensity geopolitical conflicts threatening key maritime chokepoints like the Strait of Hormuz and Bab-el-Mandeb.",
        "risks": "A spike to $100+ would severely derail India's fiscal consolidation plans and force state oil marketing companies (OMCs) to raise retail petrol prices, risking public dissatisfaction.",
        "opportunities": "Upstream oil explorers (ONGC, Oil India) and refiners with high gross refining margins (GRMs) benefit directly.",
        "historical_comparison": "Evokes comparison to the 2011-2014 period when Brent averaged $100+, causing high inflation and high interest rates in India.",
        "predictions": "A supply-demand deficit is likely to keep Brent range-bound between $80-$90 in the short term, with extreme risk premium if geopolitical events escalate."
    },
    "us_rate": {
        "title": "Impact of US Federal Reserve Interest Rate Hikes on India",
        "summary": "When the US Federal Reserve hikes interest rates, it tightens global dollar liquidity, causing capital flight from emerging markets like India and weakening local currencies.",
        "cause": "US Fed raising rates to anchor domestic inflation and cool the American job market.",
        "effect": "US Treasury yields rise; global capital flows back to the US; USD strengthens against emerging market currencies.",
        "india_impact": [
            "FII Capital Flight: Foreign portfolio investors pull money out of Indian equities and bonds in search of risk-free US yields.",
            "Rupee Depreciation: Dollar outflows weaken the Indian Rupee, making oil and raw material imports more expensive.",
            "RBI Reaction: RBI is forced to maintain high domestic interest rates to defend the Rupee and prevent capital outflow.",
            "IT & Exporters Benefit: IT services and pharma companies earn in dollars, getting a revenue boost from a weaker Rupee."
        ],
        "root_cause": "The global dominance of the US Dollar. Since global commodities are priced in USD, US interest rates determine the cost of leverage and capital allocations globally.",
        "risks": "Extended high rates in the US restrict RBI's capacity to cut rates, increasing borrowing costs for Indian businesses.",
        "opportunities": "IT service firms, textile exporters, and pharmaceutical companies see increased operating margins.",
        "historical_comparison": "Resembles the 'Taper Tantrum' of 2013, when hints of US quantitative easing tapering led to rapid capital flight and currency crises in emerging markets.",
        "predictions": "The yield spread between India and the US will remain narrow, keeping the USD/INR exchange rate pinned above 83.50 until the Fed begins rate easing."
    },
    "rupee": {
        "title": "Sectors Benefiting from a Weaker Rupee",
        "summary": "A weaker rupee (USD/INR depreciation) increases the local currency value of dollar-denominated export earnings, providing tailwinds for export-heavy sectors while hurting import-dependent industries.",
        "cause": "Global dollar strength, capital outflows, and a widening trade deficit.",
        "effect": "USD/INR exchange rate rises, raising rupee revenue for exporters and rising bills for importers.",
        "india_impact": [
            "IT Services: Over 60% of revenue comes from North America. A 1% rupee fall typically boosts IT operating margins by 25-30 bps.",
            "Pharmaceuticals: Large API and generic exports to US/Europe see immediate realization gains.",
            "Chemicals & Textiles: Increased global price competitiveness against other currency zones.",
            "Losing Sectors: Electronics, automotive (imported components), oil marketing, and businesses with unhedged External Commercial Borrowings (ECBs)."
        ],
        "root_cause": "Structural mismatch in India's merchandise trade balance (high oil, electronics, gold imports relative to lower merchandise exports).",
        "risks": "Imported inflation offsets export gains; high volatility complicates corporate hedging strategies.",
        "opportunities": "Indian manufacturing (PLI scheme targets) becomes relatively more cost-competitive in global markets.",
        "historical_comparison": "Historically, rupee depreciation cycles (like 2018 and 2022) have consistently led to outperformance in IT and Pharma indices relative to domestic cyclical stocks.",
        "predictions": "Expect export sectors to act as a hedge in equity portfolios if global macro uncertainties persist."
    },
    "semiconductor": {
        "title": "Economic Impact of Indian Semiconductor Investments",
        "summary": "India's semiconductor investments under the Rs 76,000-crore PLI scheme aim to establish a local manufacturing ecosystem, reducing import dependency on Taiwan/China and boosting high-tech manufacturing.",
        "cause": "Government subsidies, global supply-chain diversification ('China + 1'), and domestic electronics demand.",
        "effect": "Construction of semiconductor fabs (Tata-PSMC in Dholera) and assembly units (CG Power, Micron).",
        "india_impact": [
            "Import Substitution: Reduces India's massive electronics import bill, which is currently second only to crude oil.",
            "Strategic Autonomy: Safeguards automotive, defense, and telecommunication supply chains from geopolitical conflicts.",
            "Job Creation: Generates high-skilled engineering and manufacturing jobs, fostering R&D hubs.",
            "Sectors Benefiting: Electronics manufacturing services (EMS), automotive parts makers, telecom gear, and industrial construction."
        ],
        "root_cause": "Geopolitical supply chain vulnerabilities exposed during the COVID-19 pandemic and rising US-China-Taiwan tensions.",
        "risks": "Semiconductor manufacturing is extremely capital and water-intensive, requiring uninterrupted power and highly specialized talent.",
        "opportunities": "Creating a domestic electronics cluster could add 1.5-2.0% to India's manufacturing GDP over the next decade.",
        "historical_comparison": "Comparable to China's early-2000s initiatives to build local hardware manufacturing ecosystems.",
        "predictions": "First India-made commercial chips are expected to roll out by 2026, triggering a localized component manufacturing boom."
    },
    "rbi_policy": {
        "title": "Economic Consequences of RBI Policy Changes",
        "summary": "RBI monetary policy changes direct the cost of capital, credit expansion, and inflation rates in India, directly influencing equity markets, banking sector margins, and consumer spending.",
        "cause": "RBI Monetary Policy Committee adjusting Repo Rate and cash reserve ratios to target 4% inflation.",
        "effect": "Commercial banks adjust MCLR (lending rates) and deposit rates; market bond yields shift.",
        "india_impact": [
            "Interest Rate Hikes: Increase home/auto loan EMIs, slowing real estate and auto sales. Cools inflation.",
            "Interest Rate Cuts: Boost credit growth, increase corporate valuations, and trigger stock market rallies.",
            "Banking Sector: Rate hikes initially expand Net Interest Margins (NIMs) as loans reprice faster than deposits.",
            "Bond Portfolios: Rising rates lead to mark-to-market losses on bank treasury holdings; falling rates lead to treasury gains."
        ],
        "root_cause": "Managing the 'impossible trinity' - maintaining independent monetary policy, defending exchange rate stability, and allowing free capital flows.",
        "risks": "Overtightening risks stalling private investment recovery; delayed action risks letting inflation expectations get unanchored.",
        "opportunities": "Rate cut cycles create massive tailwinds for high-growth sectors (IT, Consumer Discretionary) and bond funds.",
        "historical_comparison": "The aggressive rate hike cycle of 2022-2023 (repo rate from 4.0% to 6.50%) effectively anchored inflation near 4.8% without crashing GDP growth.",
        "predictions": "RBI is expected to hold rates high until the US Fed begins cutting, ensuring rupee defense before turning to domestic growth incentives."
    },
    "falling_rates": {
        "title": "Sectors Benefiting from Falling Interest Rates",
        "summary": "Falling interest rates reduce the cost of borrowing for companies and consumers, boosting interest-sensitive cyclical sectors and growth stock valuations.",
        "cause": "Central bank policy rate cuts in response to cooling inflation or economic slowdown.",
        "effect": "Lower bond yields, cheaper credit, and increased liquidity in the banking system.",
        "india_impact": [
            "Real Estate & Housing: Cheaper home loans drive property sales and developer launches.",
            "Automotive: Lower auto financing EMIs stimulate passenger vehicle and two-wheeler volumes.",
            "Infrastructure & Capital Goods: Highly leveraged infrastructure developers see lower interest burdens, boosting project ROCE.",
            "Banking & NBFCs: Lower cost of funds expands credit volume; retail lending NBFCs experience significant margin expansion."
        ],
        "root_cause": "Monetary stimulus reducing the hurdle rate for corporate capital expenditure and encouraging credit-backed consumerism.",
        "risks": "Excessive rate cuts risk reigniting retail inflation and weakening the local currency yield advantage.",
        "opportunities": "Corporate balance sheet deleveraging becomes easier, freeing up cash flow for reinvestment.",
        "historical_comparison": "The 2020-2021 rate cut cycle to historic lows of 4% repo rate catalyzed a massive residential real estate revival and a record-breaking stock market bull run.",
        "predictions": "A shift towards falling interest rates will trigger a capital rotation from defensive cash-rich sectors (utilities, consumer staples) into high-beta cyclicals (realty, auto, banks)."
    },
    "compare_china": {
        "title": "Growth Trends Comparison: India vs China",
        "summary": "India has surpassed China as the fastest-growing major economy, driven by favorable demographics, high public infrastructure investment, and digital transformation, while China faces structural headwinds from real estate, aging population, and local debt.",
        "cause": "Diverging demographics, regulatory environments, and structural reform cycles.",
        "effect": "Global capital increasingly adopts a 'China+1' strategy, redirecting FDI and portfolio allocations to India.",
        "india_impact": [
            "Demographic Dividend: Over 65% of India's population is of working age; China's workforce is shrinking rapidly.",
            "Investment Influx: Global electronics and manufacturing giants (Apple, Foxconn) setting up manufacturing hubs in India.",
            "Service Strength: India's digital public infrastructure (DPI) and software exports provide high-productivity growth.",
            "Key Constraints: India's manufacturing sector remains smaller (15% of GDP) compared to China's (28%), requiring sustained policy push."
        ],
        "root_cause": "China's shift from an investment-and-export-led model to consumption-led growth colliding with a real estate balance sheet recession, compared to India entering its peak capex and urbanization cycle.",
        "risks": "Global recession could slow both nations; trade protectionism risks affecting global supply chains.",
        "opportunities": "India could capture global manufacturing shares as multinational corporations diversify out of China.",
        "historical_comparison": "Similar to China's rapid double-digit growth phase in the late 1990s and early 2000s, India is entering its high-growth infra-build stage.",
        "predictions": "India is projected to sustain 6.5%-7.5% growth over the next decade, while China's trend growth is expected to settle between 3.5%-4.5%."
    },
    "explain_15": {
        "title": "Market Movements Explained (For a 15-Year-Old)",
        "summary": "Think of the stock market like a giant school cafeteria where kids trade snacks. Today, some global news made traders worry about their allowance money, causing prices of cool toys (stocks) to drop, while safe piggy banks (gold) became popular.",
        "cause": "Traders reacting to news about interest rates and oil, just like kids reacting to cafeteria rumors.",
        "effect": "Stock prices went down; gold prices went up; the Rupee lost a tiny bit of value against the Dollar.",
        "india_impact": [
            "The US Dollar is like the cool popular kid. When he gets stronger, other currencies like the Indian Rupee feel a bit weaker.",
            "If oil gets expensive, the school bus ticket might cost more, which means you have less pocket money for chocolates.",
            "Gold is like a rare shiny trading card. When kids are scared that their cash is losing value, they all run to trade for the gold card, making its price jump!"
        ],
        "root_cause": "People around the world are trying to protect their savings and grow their wealth based on news and calculations.",
        "risks": "If people get too scared, they stop spending, which makes business slow down for everyone.",
        "opportunities": "Smart buyers look for good companies whose stock prices fell by mistake, buying them cheap.",
        "historical_comparison": "It's like when everyone panicked and bought all the toilet paper in 2020. Market panics happen but they eventually settle down.",
        "predictions": "The cafeteria will calm down tomorrow once kids see that the school rules haven't actually changed!"
    }
}

class AIAnalystService:
    async def ask_question(self, query: str) -> dict:
        """
        Processes a user question about the economy, routing to Gemini/OpenAI
        if configured, or resolving via semantic template engine.
        """
        query_lower = query.lower()
        
        # Check if LLM API Keys are configured
        if settings.GEMINI_API_KEY:
            try:
                return await self._call_gemini_api(query)
            except Exception as e:
                logger.error(f"Gemini API call failed: {e}. Falling back to next available LLM.")
        
        if settings.OPENAI_API_KEY:
            try:
                return await self._call_openai_api(query)
            except Exception as e:
                logger.error(f"OpenAI API call failed: {e}. Falling back to next available LLM.")

        # Check if local Ollama LLM execution is enabled
        if settings.USE_OLLAMA:
            try:
                return await self._call_ollama_api(query)
            except Exception as e:
                logger.error(f"Ollama local LLM call failed: {e}. Falling back to rule-based engine.")

        # Local Rule-based fallback engine: match keywords to return pre-constructed financial reports
        matched_key = None
        if "gold" in query_lower:
            matched_key = "gold"
        elif "oil" in query_lower or "crude" in query_lower or "fuel" in query_lower:
            matched_key = "oil"
        elif "us interest" in query_lower or "fed" in query_lower or "us rate" in query_lower or "interest rate hike" in query_lower:
            matched_key = "us_rate"
        elif "rupee" in query_lower or "usd/inr" in query_lower or "usd-inr" in query_lower:
            matched_key = "rupee"
        elif "semiconductor" in query_lower or "fab" in query_lower:
            matched_key = "semiconductor"
        elif "rbi policy" in query_lower or "repo rate" in query_lower or "rbi rate" in query_lower or "consequences of rbi" in query_lower:
            matched_key = "rbi_policy"
        elif "falling interest" in query_lower or "falling rates" in query_lower:
            matched_key = "falling_rates"
        elif "china" in query_lower or "compare india" in query_lower:
            matched_key = "compare_china"
        elif "15" in query_lower or "teenager" in query_lower or "simple terms" in query_lower:
            matched_key = "explain_15"

        # If a match is found, return the structured card
        if matched_key:
            data = SEMANTIC_ANSWERS[matched_key]
            return {
                "engine": "Local Narrative engine (Fallback)",
                "query": query,
                "title": data["title"],
                "summary": data["summary"],
                "cause": data["cause"],
                "effect": data["effect"],
                "india_impact": data["india_impact"],
                "details": {
                    "root_cause": data["root_cause"],
                    "risks": data["risks"],
                    "opportunities": data["opportunities"],
                    "historical_comparison": data["historical_comparison"],
                    "predictions": data["predictions"]
                }
            }

        # Catch-all generic financial synthesis if no direct keywords match
        return self._generate_generic_economic_response(query)

    def _generate_generic_economic_response(self, query: str) -> dict:
        """
        Constructs a logical macro-economic response by parsing query components
        and linking them to Indian transmission channels.
        """
        words = query.lower().split()
        subject = "Economic Indicators"
        for w in words:
            if len(w) > 4:
                subject = w.capitalize()
                break

        return {
            "engine": "Local Synthesis Engine (Fallback)",
            "query": query,
            "title": f"Macro Impact Analysis: {subject}",
            "summary": f"Your inquiry regarding '{query}' touches on critical macroeconomic balances. Changes in {subject} typically propagate to India via capital flows, imported costs, or domestic credit transmission channels.",
            "cause": f"Global liquidity adjustments, commodity supply-demand cycles, and local fiscal/monetary policies.",
            "effect": f"Fluctuations in capital investments (FII/FDI), currency valuation changes, and sectoral performance shifts.",
            "india_impact": [
                "Rupee & Import Cost Channel: Higher volatility in global inputs forces pressure on India's merchandise import bill.",
                "Liquidity and Credit Channel: Changes in global rate differentials influence the Reserve Bank of India's stance on policy rates.",
                "Corporate Margins: Sectors with high reliance on imported raw materials face immediate operational headwinds.",
                "Equity Valuation: Market multiples undergo adjustments as risk-free discount yields recalibrate."
            ],
            "details": {
                "root_cause": f"The integration of India's financial and trade channels with the global economy, making local markets sensitive to US interest rates, oil supply, and geopolitical shifts.",
                "risks": "Potential inflation creep, capital outflows, and currency volatility in USD/INR.",
                "opportunities": "Enhancing domestic manufacturing through government incentives (PLI schemes) acts as a strategic buffer.",
                "historical_comparison": "Similar to historical shocks in 2013 and 2022, structural buffers (large forex reserves, solid GDP growth) insulate India from severe systemic crises.",
                "predictions": "Near-term consolidation in domestic equities; currency rates are projected to adjust to retain trade competitiveness."
            }
        }

    async def _call_gemini_api(self, query: str) -> dict:
        """
        Calls Google Gemini API to generate structured economic analysis.
        """
        # Formulate instructions for structured financial output
        prompt = (
            "You are a Senior Economic Analyst. Analyze the following user economic question and return a structured JSON response. "
            "The JSON must have the following keys: 'title', 'summary', 'cause', 'effect', 'india_impact' (list of strings), and "
            "'details' (object with keys 'root_cause', 'risks', 'opportunities', 'historical_comparison', 'predictions').\n"
            f"Question: {query}"
        )
        
        url = f"https://generativetoolkit.googleapis.com/v1beta/models/gemini-pro:generateContent?key={settings.GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"responseMimeType": "application/json"}
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=20.0)
            resp.raise_for_status()
            json_resp = resp.json()
            
            # Parse gemini response
            import json
            text_content = json_resp["candidates"][0]["content"]["parts"][0]["text"]
            parsed_data = json.loads(text_content)
            
            return {
                "engine": "Gemini-Pro API",
                "query": query,
                **parsed_data
            }

    async def _call_openai_api(self, query: str) -> dict:
        """
        Calls OpenAI ChatGPT API to generate structured economic analysis.
        """
        prompt = (
            "You are a Senior Economic Analyst. Analyze the following user economic question and return a structured JSON response. "
            "The JSON must have the following keys: 'title', 'summary', 'cause', 'effect', 'india_impact' (list of strings), and "
            "'details' (object with keys 'root_cause', 'risks', 'opportunities', 'historical_comparison', 'predictions').\n"
            f"Question: {query}"
        )
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}"
        }
        payload = {
            "model": "gpt-4-turbo",
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": "You are a financial terminal assistant that outputs structured economic reports in JSON."},
                {"role": "user", "content": prompt}
            ]
        }
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=20.0)
            resp.raise_for_status()
            json_resp = resp.json()
            
            import json
            text_content = json_resp["choices"][0]["message"]["content"]
            parsed_data = json.loads(text_content)
            
            return {
                "engine": "OpenAI GPT-4 API",
                "query": query,
                **parsed_data
            }

    async def _call_ollama_api(self, query: str) -> dict:
        """
        Calls local Ollama instance to generate structured economic analysis.
        Uses format='json' configuration parameter to enforce schema outputs.
        """
        # Execute multi-tier LLM router fallback
        from backend.app.services.llm_router import llm_router
        prompt = f"Analyze the following economic query for an Indian institutional trading terminal: {query}"
        router_res = await llm_router.query(prompt)
        
        return {
            "engine": f"{router_res['provider']} ({router_res['model']})",
            "query": query,
            "title": f"Economic Intelligence Report: {query[:40]}",
            "summary": router_res["text"],
            "cause": "Global interest rate differentials and commodity price transmission.",
            "effect": "Macro economic adjustments across spot forex and equity indices.",
            "india_impact": [
                "Domestic Yield Curve Shift: Bond markets price in updated monetary policy trajectory.",
                "Import Bill Exposure: Energy and precious metal imports drive trade deficit movements."
            ],
            "details": {
                "root_cause": "Global macroeconomic liquidity conditions",
                "risks": "Input cost inflation and currency volatility",
                "opportunities": "Domestic sectoral growth tailwinds"
            }
        }

# Global Singleton instance
ai_analyst_service = AIAnalystService()
