# P1-L1: What is a Factor and Why Does Anyone Care?

**Project:** 1 — Factor Research Copilot
**Phase:** 1 — Concept Lessons
**Lesson date:** 2026-05-25
**Status:** Complete

---

## The core observation

Stock returns are not independent of each other. They share common patterns of movement. Apple (AAPL) and Microsoft (MSFT) move together more than AAPL and Coca-Cola (KO). Something is making many stocks move in similar directions at similar times.

Quant equity research, for ~60 years, has been answering one question: **what is doing this?**

## The factor framework

The framework's answer: stock returns are driven by exposures to a small number of common underlying forces called **factors**.

For any stock on any day, you can decompose the return as:

```
return = (exposure₁ × factor₁_return) + (exposure₂ × factor₂_return) + ... + idiosyncratic
```

### Key vocabulary

- **Factor** — a common return driver shared across many stocks. Examples: the overall market, value, size, momentum, quality.
- **Exposure** (also called **loading** or **beta**) — how plugged in a particular stock is to a factor. A defensive utility might have low market beta; a tech stock might have high. Stocks can have negative exposure to a factor (e.g., expensive growth stocks have negative value exposure).
- **Idiosyncratic return** (also called the **residual**) — whatever's left after factors are accounted for. The stock-specific portion.

---

## The historical arc

Worth knowing because the way the field currently thinks is shaped by which assumptions broke when.

### Capital Asset Pricing Model (CAPM) — 1960s, one factor: the market

Developed by Sharpe, Lintner, and Mossin. Claim: a stock's expected excess return over the risk-free rate should equal its beta times the market's excess return.

```
E[Rᵢ] - Rf = βᵢ × (E[Rm] - Rf)
```

Translation: the only risk you get paid for is market risk. Stock-specific risk doesn't earn a premium because you could diversify it away by holding more names.

Won Sharpe a Nobel. Empirically incomplete.

### Empirical breaks (1970s–80s)

CAPM couldn't explain everything researchers saw in the data:

- **Size effect** (Banz, 1981) — small-cap stocks outperformed what CAPM predicted.
- **Value effect** (Basu, 1977) — cheap stocks (low price-to-earnings (P/E), low price-to-book (P/B)) outperformed what CAPM predicted.

Either CAPM was incomplete, or the market was systematically mispricing. The field mostly accepted the first explanation.

### Fama-French 3-factor (1992) — adds size and value

Eugene Fama and Kenneth French added two factors to CAPM:

- **Small Minus Big (SMB)** — return of small-cap stocks minus large-cap stocks.
- **High Minus Low (HML)** — return of high book-to-market stocks (cheap/value) minus low book-to-market stocks (expensive/growth).

Became the academic standard for evaluating stock returns. Fama got a Nobel.

### Carhart 4-factor (1997) — adds momentum

- **Up Minus Down (UMD, also called MOM)** — stocks that went up over the last 12 months tend to keep going up for the next few months.

Theoretically awkward — under clean efficient-market stories, momentum shouldn't exist, because the information that drove the stock up should already be priced in. It works anyway, persistently, across asset classes and decades. The most famous behavioral/anomaly factor.

### Modern landscape — the "factor zoo"

Over 400 factors have been published. Most don't replicate when retested with proper methodology (the term "factor zoo" is the field's own self-criticism). Factors that have held up reasonably well:

- Market
- Size
- Value
- Momentum
- Quality (profitable, low-debt companies)
- Low-volatility (low-vol stocks have outperformed risk-adjusted)
- Investment (companies investing aggressively underperform)
- Profitability

---

## Two distinct uses of factors

Keep these mentally separate. They use the same vocabulary but answer different questions.

### Factor as risk model

Used to **explain and decompose** returns after the fact. Feed in a portfolio's holdings; the model spits out "your portfolio's risk comes 60% from market, 20% from value, 15% from sector tilts, 5% idiosyncratic." Barra (now Morgan Stanley Capital International (MSCI)) built a commercial empire on this. Risk teams and performance attribution use it.

### Factor as alpha source

Used **proactively** to construct portfolios that capture factor premiums. Smart-beta Exchange-Traded Funds (ETFs), factor investing, much of quant equity. AQR Capital Management (AQR) and Dimensional Fund Advisors (DFA) are canonical examples. The bet: factors like value and momentum have delivered positive premiums historically; build a portfolio that tilts toward them and earn the premium over time.

**Project 1 sits on the alpha-source side.**

---

## Why a portfolio manager cares

1. **Performance attribution.** A manager beats the Standard & Poor's 500 (S&P 500) by 3% in a year — is that skill, or just heavy value exposure in a year value worked? Factor decomposition answers it.

2. **Risk control.** A long-only equity fund that thinks it's diversified across 50 names might be 70% loaded on a single factor without realizing it.

3. **Manager evaluation.** Institutional allocators use factor regression to check whether a hedge fund delivers real alpha or just packages cheap factor exposure at hedge-fund fees.

4. **Strategy construction.** Entire fund families are built around factor harvesting (AQR, DFA). The Factor Research Copilot is a tool for this kind of work.

---

## Beyond equities: cross-asset factor investing

The factor framework is not restricted to public equities. It has been extended across virtually every asset class, with varying maturity and rigor.

### Fixed income (bonds)

Well-developed. Common bond factors:

- **Term / duration** — sensitivity to interest rates
- **Credit** — compensation for default risk (spread)
- **Carry** — high-yield bonds tend to outperform low-yield, default-adjusted
- **Value** — yield vs. fundamentals, or relative to peers
- **Momentum** — yes, it works in bonds too
- **Quality** and **low volatility**

Major players: AQR, Pacific Investment Management Company (PIMCO), BlackRock, Robeco. Smart-beta bond ETFs exist.

### Foreign Exchange (FX)

One of the cleanest non-equity factor areas.

- **Carry trade** — long high-yielding currencies, short low-yielding; the foundational FX strategy
- **Momentum** — short-term continuation in exchange rates
- **Value** — purchasing power parity (PPP) mean reversion
- **Defensive / risk-off** — safe-haven currencies (Japanese Yen (JPY), Swiss Franc (CHF), US Dollar (USD)) outperform in stress

### Commodities

- **Momentum**, **value**, and **carry** (carry here is based on futures curve shape: backwardation vs. contango)

Winton, AQR, and other systematic macro funds have built businesses on commodity factor strategies.

### Options / volatility

Different framework but factor-like:

- **Volatility Risk Premium (VRP)** — selling options earns a premium because implied volatility tends to exceed realized volatility
- **Variance risk premium**, **skew premium**, **term-structure premium**

Often grouped under "alternative risk premia."

### Credit derivatives

Same factors as cash credit (credit risk, term, liquidity). Credit Default Swap Index (CDX) trading uses similar frameworks. Less mature than cash-bond factor investing.

### Private Equity (PE)

The most controversial application. The academic critique — notably Ludovic Phalippou at Oxford — decomposes PE returns into:

- **Public equity beta** (PE is largely a leveraged equity bet)
- **Size factor** (PE tends to buy smaller companies)
- **Value factor** (PE often buys at lower multiples than public peers)
- **Leverage**
- **Illiquidity premium** (compensation for locked capital)

Phalippou's argument: once you adjust for these factors plus PE's smoothed reporting (which artificially deflates measured volatility and inflates Sharpe ratios), PE alpha is much smaller than the industry claims. Contested, but it's the rigorous academic view.

### Private credit

Similar story to PE: credit factor + illiquidity premium + leverage. Less factor-research literature, but the framework applies.

### Cross-asset factor investing

A whole research stream. The canonical paper is "Value and Momentum Everywhere" (Asness, Moskowitz, Pedersen, 2013), which showed value and momentum signals work across equities, bonds, currencies, and commodities. Some funds — AQR is the textbook example — run multi-asset factor strategies that combine these.

### Caveats

1. **Equity is the most mature.** Decades of research, clean data, many securities. Other asset classes have less statistical power (~30 major currency pairs vs. thousands of stocks).
2. **Data quality varies dramatically.** Public equities have clean, daily, point-in-time data. Private markets have stale, smoothed, self-reported data that makes everything look better than it is.
3. **Implementation costs vary.** A 0.5% annual factor alpha works in liquid equities; in illiquid credit it gets eaten by transaction costs.
4. **Some "private-market factors" are really just leverage + illiquidity + accounting artifacts** (Phalippou's whole point about PE).
5. **For Project 1:** equity-only by design — cleanest data via yfinance, most documented research to compare against, right place to learn the mechanics. The intuition transfers everywhere; implementation details differ by asset class.

---

## Connection to Project 1

The Factor Research Copilot will:

1. Take a natural-language hypothesis (e.g., "test 12-month momentum on the S&P 500")
2. Compute the factor across the universe and across history
3. Test predictive power (Information Coefficient (IC), decile spreads, factor decay)
4. Generate a research memo with methodology risk checks

Lessons P1-L2 through P1-L10 build out the missing pieces: defining the universe, computing returns properly, constructing signals, evaluating predictive power, managing biases, modeling costs, and computing performance metrics.

---

## Key vocabulary recap

| Term | Meaning |
|------|---------|
| Factor | Common return driver across many stocks |
| Exposure / loading / beta | How plugged-in a stock is to a factor |
| Idiosyncratic / residual return | Stock-specific portion after factors removed |
| CAPM | 1-factor model: market only |
| Fama-French 3-factor | Market + size + value |
| Carhart 4-factor | Market + size + value + momentum |
| SMB | "Small Minus Big" — size factor |
| HML | "High Minus Low" — value factor |
| MOM / UMD | "Up Minus Down" — momentum factor |
| Factor zoo | The 400+ published factors, most non-replicating |
| Risk model use | Decompose returns after the fact |
| Alpha source use | Construct portfolios to capture factor premiums |

---

## Open questions / things to revisit

*(Empty — add as they come up in later lessons.)*
