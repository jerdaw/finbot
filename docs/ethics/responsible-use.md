# Responsible Use and Ethical Guidelines

**Last Updated:** 2026-02-12
**Version:** 1.0

## Purpose and Scope

This document outlines the ethical guidelines, limitations, and responsible use practices for the Finbot financial simulation and backtesting platform. These guidelines are designed to ensure users understand the appropriate applications, limitations, and potential risks associated with using this software.

Finbot is an **educational and research tool** developed to demonstrate software engineering capabilities, quantitative analysis skills, and systematic thinking. It is **not** intended as a professional financial advisory service or medical decision-making tool.

## 1. Financial Advice Disclaimer

### 1.1 Not Financial Advice

**IMPORTANT:** Finbot does not provide financial, investment, or tax advice.

- **No Advisory Relationship:** Using this software does not create an advisor-client relationship
- **No Recommendations:** Output from simulations, backtests, or optimizations should not be interpreted as investment recommendations
- **No Suitability Analysis:** The software does not assess individual financial situations, risk tolerance, investment goals, or time horizons
- **Educational Purpose Only:** All tools, simulations, and analyses are provided for educational and research purposes

### 1.2 Professional Advice Required

Users should:
- **Consult Licensed Professionals:** Seek advice from registered investment advisors, certified financial planners, or tax professionals before making investment decisions
- **Verify Independently:** Independently verify all data, assumptions, and conclusions
- **Conduct Due Diligence:** Perform your own research and analysis
- **Understand Risks:** Fully understand the risks of any investment strategy before implementation

### 1.3 Regulatory Compliance

The author:
- Is **not** a registered investment advisor, broker-dealer, or financial planner
- Does **not** hold securities licenses (Series 7, Series 65, etc.)
- Does **not** provide personalized investment advice
- Does **not** receive compensation for investment recommendations

Users are responsible for:
- Complying with all applicable securities laws and regulations
- Understanding tax implications of investment strategies
- Filing required tax forms and disclosures
- Following regulations in their jurisdiction

## 2. Data Privacy and Security

### 2.1 Data Collection and Usage

Finbot operates on publicly available financial data:
- **No Personal Financial Data:** The software does not collect, store, or transmit users' personal financial information
- **Public Market Data Only:** All price data, economic indicators, and index data come from public sources (Yahoo Finance, FRED, Google Finance, etc.)
- **Local Processing:** All simulations and analyses run locally on the user's machine
- **No Cloud Storage:** No user data is transmitted to cloud services or third parties

### 2.2 API Keys and Credentials

Users must:
- **Secure API Keys:** Protect API keys for data providers (FRED, Alpha Vantage, etc.) using environment variables or `.env` files
- **Never Commit Credentials:** Never commit API keys, service account credentials, or passwords to version control
- **Use Service Accounts:** For Google Finance integration, use service accounts with minimal permissions
- **Rotate Keys Regularly:** Periodically rotate API keys and credentials
- **Monitor Usage:** Monitor API usage to detect unauthorized access

### 2.3 Data Security Best Practices

Recommended practices:
- **Keep Software Updated:** Regularly update dependencies to patch security vulnerabilities
- **Review Dependencies:** Periodically audit third-party dependencies using `pip-audit`
- **Use Virtual Environments:** Isolate project dependencies from system Python
- **Restrict Access:** Limit file system permissions on data directories
- **Encrypt Sensitive Data:** If storing sensitive data (not recommended), use encryption

### 2.4 Privacy Considerations

- **No Tracking:** The software does not include analytics, telemetry, or user tracking
- **No Third-Party Services:** No integration with advertising networks or data brokers
- **Open Source:** All code is publicly available for security audits
- **Local Only:** All computations occur on the user's local machine

## 3. Backtesting Limitations and Caveats

### 3.1 Inherent Limitations

Backtesting has fundamental limitations:

**Survivorship Bias:**
- Backtests use current index constituents
- Delisted companies (bankruptcies, mergers) are excluded
- Actual historical performance would be worse than backtests suggest
- Example: S&P 500 backtests exclude companies that went bankrupt

**Overfitting and Data Snooping:**
- Strategies optimized on historical data may not generalize
- Multiple testing increases false discovery risk
- "Backtest until it works" leads to illusory performance
- Parameter optimization may find spurious patterns

**Look-Ahead Bias:**
- Inadvertently using future information in historical analysis
- Index rebalancing dates may not reflect actual historical timing
- Corporate actions (splits, dividends) known with certainty in backtests

**Assumption Violations:**
- Assumes perfect liquidity (all orders fill at close prices)
- Ignores slippage (difference between expected and actual execution prices)
- Simplified commission models (flat $0.001 per share, actual costs vary)
- No market impact (large orders don't move prices)

### 3.2 Past Performance ≠ Future Results

**CRITICAL WARNING:** Past performance does not guarantee future results.

- **Regime Dependency:** Strategies that worked in bull markets may fail in bear markets
- **Black Swan Events:** Backtests cannot predict unprecedented events (2008 crisis, COVID-19 pandemic, etc.)
- **Market Evolution:** Markets adapt; profitable strategies attract capital and diminish returns
- **Structural Changes:** Regulatory changes, technology advances, and market structure evolution

### 3.3 Transaction Costs and Taxes

Backtests underestimate real-world costs:

**Transaction Costs:**
- Commissions (even "zero-commission" brokers have payment for order flow)
- Bid-ask spreads (especially for illiquid securities)
- Market impact (large orders move prices)
- Short-term trading fees (some brokers charge for frequent trading)

**Tax Implications:**
- Short-term capital gains taxed as ordinary income (up to 37% federal)
- Frequent trading generates taxable events
- Wash sale rules complicate tax-loss harvesting
- State and local taxes vary by jurisdiction
- Backtests do not account for tax drag

**Borrowing Costs:**
- Leveraged strategies incur margin interest
- Margin calls force liquidation at unfavorable prices
- Short positions pay borrow fees
- Overnight financing costs vary by broker

### 3.4 Statistical Significance

Beware of false positives:
- Small sample sizes lack statistical power
- Chance can produce impressive backtests
- Multiple hypothesis testing requires correction (Bonferroni, FDR)
- Out-of-sample testing essential (but still not foolproof)
- Walk-forward analysis helps validate robustness

### 3.5 Behavioral Factors

Humans struggle to execute strategies:
- **Emotional Decision-Making:** Fear and greed override systematic rules
- **Recency Bias:** Recent performance dominates decision-making
- **Loss Aversion:** Losses hurt more than equivalent gains feel good
- **Disposition Effect:** Hold losers too long, sell winners too soon
- **Hindsight Bias:** "I knew it all along" prevents learning from mistakes

## 4. Health Economics Ethical Considerations

### 4.1 Not Medical Advice

**IMPORTANT:** Health economics simulations do not constitute medical advice.

- **No Clinical Recommendations:** QALY simulations, cost-effectiveness analyses, and treatment optimizations are educational demonstrations, not clinical guidance
- **No Patient-Specific Analysis:** Simulations use population-level parameters, not individual patient data
- **No Diagnostic Tool:** This software does not diagnose, treat, cure, or prevent any disease
- **Consult Healthcare Professionals:** All medical decisions should be made in consultation with qualified healthcare providers

### 4.2 Methodological Limitations

Health economics simulations have constraints:

**Simplified Models:**
- Constant hazard rates (not age-dependent mortality)
- Independent utility and cost distributions (correlations ignored)
- No discounting of future costs/QALYs (standard practice is 3% discount rate)
- Population averages (individual variation not captured)
- No adverse event modeling (treatment side effects excluded)

**Data Quality:**
- Parameters based on literature estimates (varying quality)
- Studies may not generalize across populations
- Publication bias favors positive results
- Industry-sponsored trials may overestimate benefits

**Ethical Concerns:**
- QALY framework has philosophical limitations (values quantity over quality in some scenarios)
- Willingness-to-pay thresholds vary across countries and contexts
- Equity considerations not modeled (distributional impacts ignored)
- Patient preferences and values not incorporated

### 4.3 Appropriate Use Cases

Health economics tools are appropriate for:
- **Educational Demonstrations:** Teaching health technology assessment methods
- **Methodology Learning:** Understanding cost-effectiveness analysis frameworks
- **Research Skills:** Developing quantitative analysis capabilities
- **Policy Discussion:** Informing general policy discussions (not specific decisions)

Health economics tools are **not** appropriate for:
- Clinical decision-making for individual patients
- Regulatory submissions or health technology assessments
- Reimbursement decisions
- Treatment guideline development
- Resource allocation decisions affecting patient care

### 4.4 Regulatory Context

- **Health Canada, NICE, CADTH:** Official health technology assessments require peer review, stakeholder consultation, and rigorous methodology
- **FDA Approval:** Drug approvals based on clinical trials, not simulation models
- **Clinical Practice Guidelines:** Developed by professional societies using systematic evidence reviews
- **This Software:** Not validated for regulatory or clinical use

### 4.5 Equity and Justice Considerations

Cost-effectiveness analysis raises ethical questions:
- **Age Discrimination:** QALY framework may disadvantage elderly (fewer remaining life years)
- **Disability Rights:** Quality-of-life weights may undervalue lives of people with disabilities
- **Access to Care:** Cost-effectiveness used to deny treatments raises equity concerns
- **Socioeconomic Status:** Health outcomes vary by income, race, geography (models may not capture)

Users should:
- Recognize these limitations when interpreting results
- Consider multiple ethical frameworks (not just cost-effectiveness)
- Prioritize patient autonomy and shared decision-making
- Avoid using cost-effectiveness as the sole criterion for access decisions

## 5. Research and Educational Use

### 5.1 Intended Use Cases

Finbot is designed for:
- **Learning Programming:** Demonstrating software engineering, data science, and quantitative analysis skills
- **Academic Research:** Exploring portfolio theory, algorithmic trading, and health economics methods
- **Skills Portfolio:** Showcasing technical capabilities for job applications and academic admissions
- **Methodology Education:** Teaching backtesting, simulation, and optimization techniques
- **Concept Demonstration:** Illustrating financial concepts (compound growth, volatility, risk-adjusted returns)

### 5.2 Citation and Attribution

If using this software in research or publications:
- Cite the GitHub repository: `github.com/jerdaw/finbot`
- Disclose methodology: Describe simulation parameters, assumptions, and limitations
- Acknowledge limitations: Explicitly state the caveats discussed in this document
- Share code: Follow open science principles by publishing analysis code

### 5.3 Reproducibility

To support reproducible research:
- **Version Control:** All code is tracked in Git
- **Dependency Management:** Use `uv.lock` for exact dependency versions
- **Configuration:** All parameters configurable via YAML files
- **Deterministic:** Set random seeds for Monte Carlo simulations
- **Documentation:** Code is documented with docstrings and ADRs

### 5.4 Academic Integrity

Users conducting academic research must:
- Follow institutional research ethics guidelines
- Obtain IRB approval if research involves human subjects (even survey data)
- Properly attribute ideas and code
- Avoid plagiarism and self-plagiarism
- Disclose conflicts of interest
- Make data and code available when possible

## 6. Liability Limitations

### 6.1 No Warranty

This software is provided "AS IS" without warranty of any kind:
- **No Guarantees:** No guarantee of accuracy, completeness, or fitness for any purpose
- **No Liability:** The author is not liable for financial losses, missed opportunities, or damages
- **Use at Own Risk:** Users assume all risks associated with using this software
- **No Support:** No obligation to provide technical support, bug fixes, or updates

### 6.2 Accuracy of Data

- **Third-Party Data:** Price data, economic indicators, and index values come from third-party sources (Yahoo Finance, FRED, etc.)
- **Data Errors:** Data providers may have errors, gaps, or delays
- **No Verification:** The author does not independently verify data accuracy
- **User Responsibility:** Users must verify data accuracy for critical applications

### 6.3 Software Bugs

- **Bugs May Exist:** Despite testing, software may contain bugs
- **No Certification:** This software is not certified for professional or commercial use
- **Community Testing:** Relies on community testing and issue reports
- **Open Source:** Users can review code and contribute fixes

### 6.4 Forward-Looking Statements

- **Projections Uncertain:** Monte Carlo simulations, DCA optimizations, and strategy backtests involve projections based on assumptions
- **Assumptions May Fail:** Future market conditions may differ from historical patterns
- **No Predictions:** This software does not predict future market movements
- **Scenario Analysis Only:** Simulations explore "what if" scenarios, not forecasts

## 7. User Responsibilities

### 7.1 Independent Judgment

Users must:
- Exercise independent judgment in all financial and health decisions
- Verify all data, assumptions, and conclusions
- Understand the limitations documented here
- Seek professional advice when appropriate
- Take personal responsibility for decisions

### 7.2 Risk Management

Users should:
- Only invest money they can afford to lose
- Diversify across asset classes and strategies
- Maintain emergency funds (3-6 months expenses)
- Understand leverage risks (leveraged ETFs can lose >100% in volatile markets)
- Set stop-losses and position size limits

### 7.3 Continuous Learning

Users are encouraged to:
- Read academic literature on portfolio theory and risk management
- Study market history (bubbles, crashes, recoveries)
- Learn about behavioral finance and cognitive biases
- Practice with paper trading before live implementation
- Keep records of decisions and outcomes for learning

### 7.4 Ethical Conduct

Users must:
- Not use this software for illegal activities (market manipulation, insider trading)
- Comply with securities regulations (accredited investor rules, etc.)
- Respect intellectual property (cite sources, don't plagiarize)
- Act with integrity in research and financial markets
- Consider societal impacts of investment strategies

## 8. Reporting Issues and Feedback

### 8.1 Bug Reports

If you discover bugs:
- Open an issue on GitHub: `github.com/jerdaw/finbot/issues`
- Provide minimal reproducible examples
- Include software version, Python version, and error messages
- Check existing issues to avoid duplicates

### 8.2 Security Vulnerabilities

If you discover security vulnerabilities:
- Report privately to the repository maintainer (see SECURITY.md)
- Do not disclose publicly until a fix is available
- Allow reasonable time for remediation
- Follow responsible disclosure practices

### 8.3 Ethical Concerns

If you identify ethical issues with the software:
- Open a discussion on GitHub Discussions
- Propose improvements to this document
- Share relevant research or best practices
- Contribute to documentation improvements

## 9. Updates and Revisions

This document may be updated to:
- Reflect new features or capabilities
- Address emerging ethical concerns
- Incorporate user feedback
- Comply with evolving regulations
- Improve clarity and comprehensiveness

**Version History:**
- **Version 1.0 (2026-02-12):** Initial release

Users should periodically review this document for updates.

## 10. Conclusion

Finbot is a powerful educational and research tool, but it comes with significant limitations and ethical considerations. Users must:

1. **Understand Limitations:** Recognize that simulations, backtests, and optimizations are subject to survivorship bias, overfitting, and regime dependency
2. **Seek Professional Advice:** Consult licensed financial advisors, tax professionals, and healthcare providers for personalized recommendations
3. **Exercise Caution:** Never risk money you cannot afford to lose
4. **Maintain Ethics:** Use the software responsibly and ethically
5. **Continuous Learning:** Treat the software as a learning tool, not a decision-making oracle

**By using this software, you acknowledge that you have read, understood, and agreed to these guidelines.**

---

## Additional Resources

**Financial Education:**
- [SEC Investor Education](https://www.investor.gov/)
- [FINRA Investor Education](https://www.finra.org/investors)
- [CFA Institute Research Foundation](https://www.cfainstitute.org/research/foundation)

**Health Economics:**
- [NICE International](https://www.nice.org.uk/about/what-we-do/nice-international)
- [CADTH Methods and Guidelines](https://www.cadth.ca/resources/finding-evidence)
- [WHO-CHOICE](https://www.who.int/teams/health-systems-governance-and-financing/economic-analysis/cost-effectiveness/choosing-interventions-that-are-cost-effective)

**Research Ethics:**
- [Declaration of Helsinki (Medical Research)](https://www.wma.net/what-we-do/medical-ethics/declaration-of-helsinki/)
- [COPE Guidelines (Research Publication)](https://publicationethics.org/)
- [Open Science Framework](https://osf.io/)

**Software Security:**
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

---

**For Questions or Clarifications:**
See the [Contributing Guide](../contributing.md) or open an issue on GitHub.
