# India–EU CBAM Exposure & Export Competitiveness Analytics

**Document:** Project charter  
**Version:** 1.0  
**Status:** Approved analytical baseline  
**Last reviewed:** 15 November 2026  
**Project owner:** Atharva

---

## 1. Executive summary

This project will build a reproducible analytics pipeline to assess India's historical trade exposure to EU imports of iron and steel goods that fall within the EU Carbon Border Adjustment Mechanism (CBAM) product scope.

The project will combine EU-reported product-level import statistics, CBAM product classifications, official embedded-emissions defaults and benchmarks, and CBAM certificate-price inputs. It will produce trade, emissions and scenario-based financial exposure indicators, then communicate the results through Tableau.

The first implementation sector is **iron and steel**. The initial historical observation window is **2022–2025**. **Eurostat Comext** is the primary source for detailed EU import statistics at Combined Nomenclature (CN) product level. **UN Comtrade** is a complementary source for India's reported exports and independent comparisons; it will not be silently merged with Eurostat observations.

The analysis applies the CBAM product scope and definitive-period reference methodology in force at the time of analysis to historical trade flows. Accordingly, historical outputs are retrospective exposure indicators or counterfactual screening estimates. They are **not** evidence that CBAM certificate liabilities were payable on those historical shipments in 2022–2025.

## 2. Business problem

The EU's CBAM establishes a carbon-related mechanism for selected imported goods. For affected supply chains, embedded emissions, product classification, production route, carbon-price inputs and regulatory adjustments can influence the carbon-cost implications associated with imports.

Indian exporters, industry analysts and investors need a way to understand which Indian iron and steel products have material exposure to the EU market, how large those trade flows are, what emissions assumptions may apply, and how alternative carbon-price or emissions-intensity assumptions change the indicative cost picture.

Trade values alone do not answer these questions. Trade data must be joined carefully to the legally defined CBAM product scope and to emissions and pricing reference data. Public aggregate trade data also does not reveal the verified installation-level emissions of each Indian producer.

## 3. Primary research question

**How significant is India's exposure to EU imports of CBAM-covered iron and steel goods, and how do product mix, trade concentration, embedded-emissions assumptions and carbon-price scenarios affect indicative financial exposure?**

## 4. Supporting research questions

1. What value and physical quantity of in-scope iron and steel goods did EU countries import from India in each year from 2022 to 2025?
2. Which CN product codes and EU destination markets account for the largest shares of those imports?
3. What official default embedded-emissions values and production-route distinctions are relevant to each in-scope product?
4. Which product/destination combinations produce the largest gross carbon-cost screening indicators under stated assumptions?
5. How does India's share of EU imports vary by product and year?
6. How sensitive are screening indicators to alternative certificate prices and emissions-intensity assumptions?
7. Which products should be prioritised for better emissions data, supplier engagement or further commercial analysis?

## 5. Scope and approved project decisions

| Decision | Approved baseline |
|---|---|
| Exporting economy | India |
| Destination market | EU-27 (the current EU-27 composition, with country-level reporting retained) |
| Initial sector | Iron and steel only |
| Historical period | Calendar years 2022, 2023, 2024 and 2025 |
| Primary detailed trade source | Eurostat Comext dataset `DS-045409` |
| Complementary trade source | UN Comtrade, for India's reported exports and cross-checks |
| Product classification | EU CN8 product codes, versioned by nomenclature year; HS6 used as a cross-reference, not as a replacement for CN8 |
| Analytical presentation | Tableau |
| Processing stack | Python, Pandas, DuckDB, SQL, dbt, Pytest, Git/GitHub |

### In-scope activities

- Extract annual EU imports from India for 2022–2025 at the most detailed available CN product level relevant to iron and steel.
- Retain reporter-country detail for the EU-27 member states and create a separate EU-27 aggregate view where available.
- Identify only products confirmed against the applicable CBAM legal product list and the current Commission iron and steel guidance.
- Preserve the CN nomenclature year and source description for each code. Do not assume that a CN code or description is unchanged across all years.
- Retrieve and document the relevant official default emissions values and free-allocation benchmark inputs for definitive-period scenario work.
- Build a clearly labelled screening model and scenario analysis.
- Compare Eurostat EU-reported imports with UN Comtrade India-reported exports after aligning product level, period, partner and units as far as possible.
- Publish the data model, methods, data-quality results, limitations and Tableau dashboards.

### Explicitly out of scope for the first release

- Aluminium, cement, fertilisers, hydrogen and electricity. These may be future extensions after the steel pipeline is validated.
- Facility-level emissions estimates for named Indian producers unless verified, attributable data is obtained.
- A legal determination of any importer's CBAM obligation or certificate surrender.
- Company revenue, profit-margin or share-price forecasts.
- A causal claim that CBAM caused a change in India's exports during 2022–2025.
- Treating trade statistics as shipment-level customs declarations.

## 6. Data sources and intended roles

### 6.1 Eurostat Comext — primary trade source

- Dataset: **EU trade since 1988 by HS2-4-6 and CN8**.
- Dataset code: `DS-045409`.
- Intended selection: annual frequency; EU-27 member-state reporter (or EU-27 aggregate in a separate query); India as partner; imports; relevant CN8 product codes; years 2022–2025.
- Intended measures: trade value in euros and quantity in 100 kg, where available. Supplementary quantities are retained separately with their own unit.
- Comext API base: `https://ec.europa.eu/eurostat/api/comext/dissemination`.
- Dataset browser: https://ec.europa.eu/eurostat/databrowser/view/DS-045409/default/table

The Comext API requires filtered requests because the full dataset is too large for an unrestricted download. Query design and response metadata must be recorded.

### 6.2 UN Comtrade — complementary trade source

- API / portal: https://comtradeapi.un.org/ and https://comtradeplus.un.org/
- Intended use: India-reported exports to EU partners and to the world, at HS level, to provide an exporter-side perspective and a comparison with Eurostat's importer-side records.
- UN Comtrade and Eurostat values may differ because of reporting perspective, valuation, timing, partner attribution, revisions and product-classification detail. Differences must be analysed, not forcibly reconciled.

### 6.3 CBAM legal scope and product guidance

- CBAM Regulation (EU) 2023/956 and subsequent applicable amendments.
- Commission iron and steel sector guidance for the definitive period, including its CN-code table and explanatory notes.
- Official source: https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism/cbam-legislation-and-guidance_en

The legal Annex and applicable legislation take precedence over explanatory guidance. Broad CN prefixes must not automatically be treated as fully covered where the legal text or guidance specifies exceptions or partial coverage. In particular, the Commission guidance notes that some products under CN 7205 have conditional/partial coverage.

### 6.4 Embedded-emissions defaults

Use the applicable definitive-period default-value legislation, including Commission Implementing Regulation (EU) 2025/2621 as corrected by Commission Implementing Regulation (EU) 2026/1740, with the correct country, goods category, production-route and effective-year distinctions. Preserve the source regulation, annex/table, unit and effective date for every value.

### 6.5 Free-allocation benchmarks and adjustments

Use the applicable free-allocation-adjustment rules and benchmark tables, including Commission Implementing Regulation (EU) 2025/2620 where applicable. Do not estimate an adjusted CBAM certificate requirement until the required product, production-route, emissions and regulatory inputs have been mapped and tested.

### 6.6 CBAM certificate prices

Use the European Commission's published CBAM certificate price series. Preserve the applicable price period, publication date, currency, unit and frequency. Do not substitute a generic EU ETS spot-price series without documenting why it is an appropriate proxy.

Official price page: https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism/price-cbam-certificates_en

## 7. Unit of analysis and data grain

The core cleaned trade fact table will have one row per:

**reference year × EU reporter × partner × trade flow × CN code × CN nomenclature year**.

The source-level Comext observations may arrive as one observation per indicator. The ingestion layer must preserve the original indicator/value records; a later transformation may pivot value and quantity indicators into separate columns.

A second EU-27 aggregate series may be used for headline totals. It must never be added to the sum of the 27 individual member-state reporter records, as that would double-count trade.

Product mapping and CBAM coverage are maintained in a separate reference table. A many-to-many or one-to-many classification relationship must be resolved explicitly before joining to trade facts; joins must not multiply trade values.

## 8. Core metrics and definitions

| Metric | Definition | Interpretation / caveat |
|---|---|---|
| EU imports from India (EUR) | Eurostat import value for partner India and selected CN product | EU-reported import-side value; retain source valuation and status metadata |
| Import quantity (tonnes) | `QUANTITY_IN_100KG × 0.1`, where the source indicator is present and valid | Do not use a supplementary unit as mass without a validated conversion |
| India's share of EU imports | EU imports from India ÷ EU imports from all partners for the same reporter, year and CN code | Measures India's share in the EU import market for that product |
| India's EU export dependence | India's exports to EU ÷ India's exports to the world for the same comparable product and year | Requires UN Comtrade or another suitable exporter-side denominator; do not derive from Eurostat India-only records |
| Estimated embedded emissions (tCO₂e) | Import quantity (tonnes) × selected emissions intensity (tCO₂e/tonne) | Screening estimate; depends on valid product/route/country default mapping |
| Gross carbon-cost screening indicator (EUR) | Estimated embedded emissions × selected CBAM certificate price | Not legal CBAM liability; excludes required regulatory adjustments unless explicitly added in a later model |
| Adjusted CBAM cost estimate | Calculated under the applicable definitive-period legal methodology | Build only after modelling free-allocation adjustment, eligible carbon price paid, production route and all required inputs |

## 9. Historical-period interpretation

The 2022–2025 period is a historical trade baseline. The project may apply the CBAM product scope and definitive-period assumptions current at the model's stated reference date to those historical flows to identify retrospective exposure patterns.

Such calculations must be labelled **historical exposure proxy** or **counterfactual screening scenario**. They must not be labelled historical CBAM certificate costs, actual CBAM payments, or proof of a causal CBAM effect. The definitive CBAM regime began in 2026.

The project must keep at least two dates distinct:

- `reference_year`: the year in which the trade occurred.
- `regulatory_reference_date` / `model_vintage`: the date/version of the CBAM rules and assumptions used to screen that historical trade.

## 10. Methodology and technical architecture

1. **Extract:** retrieve filtered Comext records and selected UN Comtrade comparison records.
2. **Preserve:** store unmodified source responses, retrieval timestamps, query parameters and source metadata in `data/raw/`.
3. **Validate:** check schema, duplicates, missing values, special values, units, product codes, periods and observation flags.
4. **Standardise:** create canonical country, period, flow, product, unit and indicator fields without discarding original source fields.
5. **Map:** connect CN8 codes to the applicable CBAM goods categories and versioned legal scope.
6. **Model:** use DuckDB and dbt to create staging, intermediate and analytical models.
7. **Calculate:** create emissions and financial screening indicators with documented assumptions and tests.
8. **Visualise:** develop Tableau dashboards for executive overview, product/sector exposure, destination analysis and scenario sensitivity.
9. **Communicate:** publish findings, caveats and recommendations in project documentation.

## 11. Model assumptions and controls

- All currency values retain their source currency; convert only with a documented exchange-rate source and date if conversion is needed.
- Product codes are strings, not integers, so leading zeros are preserved.
- Every CN code is associated with its nomenclature year/version.
- Trade quantity, net mass and supplementary quantity are distinct concepts until source metadata confirms their units and meaning.
- Missing quantity is not imputed as zero.
- Missing values and Eurostat special values are not silently converted to zero.
- Eurostat aggregate EU-27 reporter observations are not summed with the 27 member-state reporters.
- Product-code mappings are validated for each CN year and are not joined on a broad HS prefix alone where that could create duplicate or over-inclusive matches.
- Default emissions values are model inputs, not measured emissions from Indian installations.
- Carbon-price and emissions scenarios are labelled assumptions, not forecasts.
- Gross carbon-cost indicators are distinct from adjusted CBAM certificate obligations.

## 12. Project deliverables

1. Python extraction modules and reproducible query configuration.
2. Raw source files and retrieval metadata.
3. Validated, documented trade datasets.
4. Versioned CN8-to-CBAM product reference table.
5. Embedded-emissions and benchmark reference tables.
6. DuckDB database and dbt models.
7. Pytest data-quality and calculation tests.
8. CBAM exposure screening and scenario model.
9. Tableau dashboards.
10. README, methodology, assumptions, data dictionary, data-quality report and final findings.

## 13. Definition of done

The first release is complete when:

- Trade data can be extracted reproducibly for all in-scope years and products.
- Source data, queries, data vintages and limitations are traceable.
- Every included product is supported by the applicable CBAM CN-code scope reference.
- Quantity and value measures have verified meanings and units.
- Joins preserve the agreed grain and do not multiply trade values.
- Data-quality tests pass and unresolved issues are disclosed.
- Emissions and price assumptions are versioned and documented.
- Screening calculations are independently reproducible and clearly distinguished from legal liability.
- Tableau dashboards communicate the analytical findings and limitations.
- The project owner can explain the business problem, sources, data model, calculations and conclusions independently.
