# Initial UN Comtrade Extraction — Data Quality Findings

**Dataset:** Indian exports of HS 7208 to World  
**Reporting year:** 2024  
**Source:** UN Comtrade API  
**Extraction date:** 11 November 2026  
**Classification:** H6  
**Validation status:** Retained for investigation; not approved for exposure calculations.

## 1. Dataset Overview

The initial extraction was conducted to test the UN Comtrade API connection and retrieve trade statistics for Indian exports of HS 7208 (flat-rolled products of iron or non-alloy steel).

The API request was successful and returned two observations containing 50 fields each.

The following parameters were used:

| Parameter | Value |
| Reporter country | India |
| Reporter code | 699 |
| Partner | World |
| Partner code | 0 |
| Reporting year | 2024 |
| Product code | 7208 |
| Trade flow | Exports (X) |
| Classification | H6 |
| Records returned | 2 |

The `primaryValue` field contains approximately 1.5485 billion in trade value for each returned observation.

However, the initial inspection identified several data-quality concerns that must be resolved before the dataset can be used for financial exposure modelling.

## 2. Finding 1 — Missing Physical Quantity Data

The dataset contains insufficient physical quantity information for emissions calculations.

The relevant fields returned the following values:

| Field | Retrieved value |
|---|---|
| qtyUnitCode | -1 |
| qtyUnitAbbr | Missing |
| qty | 0 |
| netWgt | Missing |
| grossWgt | 0 |
| isQtyEstimated | False |
| isNetWgtEstimated | False |

Although monetary trade values are available, usable physical export quantities are not.

A zero quantity in this response should not be interpreted as evidence that no physical goods were exported, particularly because the corresponding trade value is positive.

This creates a significant limitation for the project.

The calculation of estimated embedded emissions requires physical export quantities:

**Estimated embedded emissions = Export quantity (tonnes) × Emissions intensity (tCO₂e per tonne)**

Since a reliable export quantity is unavailable, total embedded emissions cannot currently be calculated.

**Decision:** This dataset will not be used to calculate physical export volumes or total embedded emissions. Quantity and weight fields will need to be investigated further or obtained from an alternative source.

## 3. Finding 2 — Identical Trade Values Across Two Records

Both observations contain the same `primaryValue`, approximately 1.5485 billion.

However, they differ in their secondary partner classification:

| Field | Record 1 | Record 2 |
|---|---:|---:|
| partnerCode | 0 | 0 |
| partner2Code | 0 | 899 |
| primaryValue | Approximately 1.5485bn | Approximately 1.5485bn |
| isReported | False | False |
| isAggregate | True | True |

According to UN Comtrade reference information, `partner2Code` represents a secondary partner classification. Code 899 refers to Areas Not Elsewhere Specified (Areas NES), which is used when the trading partner cannot be specifically identified or disclosed.

It does not represent the European Union.

The two observations therefore cannot automatically be treated as independent trade transactions.

Although the dataset contains no exact duplicate rows according to Pandas' `duplicated()` function, this does not establish that the observations are independent.

A complete understanding of the reporting dimensions and aggregation structure is required before performing any aggregation.

**Decision:** The two trade values will not be added together. The observations will be retained separately until their statistical relationship and reporting grain have been verified.

## 4. Finding 3 — Aggregated and Non-Reported Observations

Both records contain:

- `isReported = False`
- `isAggregate = True`

UN Comtrade defines these fields as indicators of whether a record was reported by the country and whether it was aggregated by the United Nations Statistics Division.

This indicates that the returned observations are aggregated rather than straightforward country-reported records.

This does not automatically invalidate the monetary values. However, their reporting provenance needs to be understood before using them as the basis for financial analysis.

The dataset also contains missing descriptive fields, including:

- reporterDesc
- partnerDesc
- flowDesc
- cmdDesc
- motDesc

These descriptions may be enriched through the relevant UN Comtrade reference tables using their corresponding numeric codes.

The `refMonth` value of 52 is the annual reporting convention used by UN Comtrade and should not be interpreted as a missing or incorrect reporting month.

**Decision:** The observations will be retained for reference but will not be accepted into the analytical exposure model until their reporting and aggregation characteristics have been investigated.

## 5. Overall Data Quality Assessment

The initial extraction produced the following results:

| Quality dimension | Assessment |
|---|---|
| API connectivity | Passed |
| Record retrieval | Passed |
| Trade value availability | Available; requires provenance validation |
| Physical quantity completeness | Failed |
| Net weight completeness | Failed |
| Exact duplicate detection | No exact duplicates found |
| Partner classification | Requires investigation |
| Reporting provenance | Requires investigation |
| Product descriptions | Requires reference enrichment |
| CBAM product coverage | Not yet established |
| Suitability for emissions modelling | Not approved |

## 6. Impact on the CBAM Exposure Project

The objective of the project is to estimate India's potential exposure to CBAM-covered exports through the combination of international trade statistics, embedded emissions assumptions and applicable carbon prices.

The initial UN Comtrade dataset does not currently meet the requirements for this analysis.

In particular, the absence of reliable physical quantities prevents the calculation of total embedded emissions.

Additionally, the aggregation and partner-classification differences introduce uncertainty when interpreting trade values.

Using these observations without further validation could lead to double counting or misleading exposure estimates.

## 7. Corrective Actions

The following actions have been identified:

1. Retain the original JSON response and processed CSV as extraction evidence.
2. Investigate the significance of the two secondary partner classifications.
3. Verify the trade-value aggregation and reporting provenance.
4. Investigate the availability of physical quantities and net weights.
5. Retrieve detailed EU import statistics through Eurostat Comext.
6. Use CN8 product classifications to establish the actual CBAM-covered steel products.
7. Validate the Eurostat dataset's quantity and value fields before using it in the exposure model.
8. Retain UN Comtrade as a supporting source for independent trade comparisons.

## 8. Final Assessment

The initial UN Comtrade extraction successfully demonstrated API connectivity, authentication, data retrieval and local data storage.

However, successful extraction does not necessarily imply analytical suitability.

The dataset is therefore classified as **retained for investigation but not approved for CBAM financial exposure calculations**.

For the next stage, Eurostat Comext will be investigated as the primary source of EU-reported imports from India, owing to its more detailed Combined Nomenclature product classification.

This will allow the project to establish a more appropriate foundation for product-level trade analysis and subsequent emissions modelling.

---

### Sources

- [UN Comtrade API Documentation](https://comtradeplus.un.org/en/api-docs)
- [UN Comtrade Data Items Reference](https://comtradeplus.un.org/en/reference-tables?table=dataitem)
- [UN Comtrade Partner Reference Table](https://comtradeplus.un.org/en/reference-tables?table=partner)
- [UN Comtrade — Areas Not Elsewhere Specified](https://uncomtrade.org/docs/areas-not-elsewhere-specified/)

**Note:** These findings apply to the initial 2024 HS 7208 extraction and should not be generalised to all UN Comtrade trade observations or India's entire steel export dataset. 