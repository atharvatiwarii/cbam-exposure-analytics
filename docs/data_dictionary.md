# Data Dictionary — India–EU CBAM Exposure & Export Competitiveness Analytics

**Document:** Data dictionary  
**Version:** 1.0  
**Status:** Initial logical data model  
**Last reviewed:** 15 November 2026

This dictionary defines the canonical fields and intended grain for the project's first release. It is a **target data contract**, not a claim that every source field has already been extracted or validated. Source-native field names must be preserved in raw data and mapped to canonical names during transformation.

## 1. Scope and conventions

- Sector: iron and steel.
- Origin of interest: India.
- Destination market: EU-27.
- Historical period: 2022–2025.
- Primary detailed trade source: Eurostat Comext `DS-045409`.
- Complementary source: UN Comtrade.
- Product identifier: EU CN8 code, stored as text and paired with its nomenclature year.
- Default currency: EUR for Eurostat import values.
- Standard physical quantity for the exposure model: tonnes of goods.
- Standard emissions unit: tonnes of CO₂ equivalent per tonne of goods (`tCO2e/t`).
- Standard carbon-price unit: EUR per tonne of CO₂ equivalent (`EUR/tCO2e`).

### Naming and null conventions

- Canonical column names use `snake_case`.
- Product codes are strings. Never cast CN or HS codes to integers.
- `NULL` means unavailable, missing or not applicable; it is not the same as numeric zero.
- Source special values and status/flag fields must be retained and interpreted using the source metadata.
- Each imported record must carry a source identifier and retrieval timestamp.
- Raw source payloads are immutable. Cleaning and conversions occur in derived tables.

## 2. Source register

| Source ID | Source | Dataset / reference | Main use | Official entry point |
|---|---|---|---|---|
| `EUROSTAT_COMEXT` | Eurostat Comext | `DS-045409` — EU trade since 1988 by HS2-4-6 and CN8 | Detailed EU import value and quantity by CN product, reporter and partner | https://ec.europa.eu/eurostat/databrowser/view/DS-045409/default/table |
| `UN_COMTRADE` | UN Comtrade | API data at HS level | India's reported exports to EU partners and world; comparison and export-dependence denominator | https://comtradeplus.un.org/ |
| `CBAM_SCOPE` | European Commission / legal acts | CBAM Regulation Annex I and current iron and steel guidance | Determine covered CN goods and aggregated goods categories | https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism/cbam-legislation-and-guidance_en |
| `CBAM_DEFAULTS` | European Commission | Implementing Regulation (EU) 2025/2621, as corrected by (EU) 2026/1740 | Default embedded-emissions values | https://eur-lex.europa.eu/eli/reg_impl/2025/2621/2026-01-01/eng |
| `CBAM_BENCHMARKS` | European Commission | Implementing Regulation (EU) 2025/2620 | Free-allocation adjustment benchmark inputs | https://eur-lex.europa.eu/eli/reg_impl/2025/2620/oj/eng |
| `CBAM_PRICE` | European Commission | Published CBAM certificate-price series | Scenario and applicable-period price input | https://taxation-customs.ec.europa.eu/carbon-border-adjustment-mechanism/price-cbam-certificates_en |

Eurostat Comext uses a dedicated API base URL: `https://ec.europa.eu/eurostat/api/comext/dissemination`. Its detailed datasets require filtered queries; the full Comext dataset is too large for an unrestricted API download. Query filters and API metadata must therefore be retained with each extraction.

## 3. Core trade source: `stg_comext_trade_observation`

### Source selection

For the main EU import series, select:

- Frequency: annual.
- Reference years: 2022, 2023, 2024, 2025.
- Partner: India.
- Flow: imports.
- Reporter: EU-27 member states for destination analysis; EU-27 aggregate in a separate headline query where available.
- Product: CN8 codes validated against the applicable CBAM iron and steel scope.
- Indicators: value in euros and quantity in 100 kg, where available.

### Grain

One row per **frequency × reference period × reporter × partner × flow × product × indicator** in the source-observation staging table.

The analytical trade mart may pivot selected indicators to one row per reporter × partner × flow × reference year × CN8 × CN version.

### Canonical fields

| Canonical field | Type | Unit / format | Definition | Validation / notes |
|---|---|---|---|---|
| `source_id` | string | e.g. `EUROSTAT_COMEXT` | Identifies the source system | Required |
| `source_dataset_code` | string | e.g. `DS-045409` | Eurostat dataset identifier | Required for Eurostat rows |
| `frequency` | string | `A` for annual | Observation frequency | Must be annual for the first release |
| `reference_period` | string | `2022`–`2025` | Source reference period | Preserve as text in raw; derive integer year for analysis |
| `reference_year` | integer | calendar year | Normalised year | Must be 2022–2025 in the historical baseline |
| `reporter_code` | string | Eurostat code | EU country or EU-27 aggregate reporting the import | Keep code and label; do not mix aggregate with member totals |
| `reporter_name` | string | country / aggregate label | Display name for reporter | Preserve source label |
| `partner_code` | string | Eurostat code | Trading partner | Must resolve to India for main series |
| `partner_name` | string | country label | Display name for partner | Expected India in main series |
| `flow_code` | string | source code / label | Trade flow direction | Must resolve to imports in main series |
| `product_code` | string | 8-digit CN code where detailed | Product identifier | Preserve leading zeros; do not parse as integer |
| `product_code_system` | string | `CN` | Classification system | Must identify CN for Comext product observations |
| `cn_version_year` | integer | year | CN nomenclature version applicable to observation | Required to interpret yearly code changes |
| `product_description` | string | source description | Product description in source nomenclature | Preserve source description and version |
| `indicator_code` | string | e.g. `VALUE_IN_EUROS` | Identifies the measured indicator | One indicator per staging observation unless explicitly normalised later |
| `observation_value` | decimal | indicator-dependent | Numeric value reported by Eurostat | Never assume unit without `indicator_code` |
| `observation_status` | string / null | source flag | Source status, provisional marker or observation flag | Retain if supplied; document source-specific meanings |
| `unit_code` | string | source unit | Unit associated with the indicator | Required for quantity measures; verify via metadata |
| `retrieved_at_utc` | timestamp | ISO-8601 UTC | Time the API data was retrieved | Required |
| `source_last_update` | date / null | date | Source dataset update date, if available | Record in extraction metadata |
| `query_parameters` | JSON / text | serialised request filters | Exact filters used to retrieve the record | Required for reproducibility |
| `raw_file_path` | string | repository-relative path | Path to immutable raw response | Required |

### Key indicator mapping

| Source indicator | Canonical output field | Unit | Conversion / rule |
|---|---|---|---|
| `VALUE_IN_EUROS` | `trade_value_eur` | EUR | No conversion if source is already euros; preserve observation status |
| `QUANTITY_IN_100KG` | `quantity_100kg` | 100 kg | Preserve source value |
| `QUANTITY_IN_100KG` | `quantity_tonnes` | tonnes | `quantity_100kg × 0.1`; derive only for valid numeric observations |
| Supplementary quantity indicator, if available | `supplementary_quantity` | source-specific | Store separately with its own unit; never assume it is mass |

If quantity is missing, suppressed or special-valued, do not impute zero. The row can still be retained for value-based trade analysis, but it must be excluded from mass-based emissions calculations unless a valid quantity is obtained from a documented source.

## 4. Complementary trade source: `stg_un_comtrade_trade_observation`

### Purpose

UN Comtrade provides the exporter-reported perspective for India and a potential denominator for India's total worldwide exports of comparable products. It is also used to compare India's reported exports with EU-reported imports from India.

### Grain

One row per **reporter × partner × period × HS product code × trade flow × classification** at the source's reported level of detail.

| Canonical field | Type | Unit / format | Definition | Validation / notes |
|---|---|---|---|---|
| `source_id` | string | `UN_COMTRADE` | Source identifier | Required |
| `reporter_code` | string | UN numeric code | Reporting economy | India is code `699` in the current project extraction |
| `reporter_name` | string | country name | Reporting economy label | Preserve source label |
| `partner_code` | string | UN numeric code | Partner economy | EU country or World, as queried |
| `partner_name` | string | country / aggregate label | Partner label | Preserve source label |
| `reference_year` | integer | year | Trade reference year | Must be in agreed range for historical comparison |
| `flow_code` | string | `X` for exports in current script | Trade direction | Verify source definition |
| `hs_code` | string | HS code | Product classification | Preserve exact reported code and classification version |
| `hs_version` | string / null | nomenclature year/version | HS classification vintage | Required where source exposes it; otherwise document limitation |
| `trade_value` | decimal | source currency | Reported trade value | Preserve original currency and valuation basis |
| `trade_value_currency` | string | e.g. USD | Currency of reported trade value | Do not presume USD without confirming API metadata |
| `net_weight_kg` | decimal / null | kg | Reported net weight | Check for missing/zero/special values |
| `quantity` | decimal / null | source-specific | Supplementary or other quantity | Store unit separately |
| `quantity_unit` | string / null | source unit | Unit of supplementary quantity | Never mix with net mass |
| `retrieved_at_utc` | timestamp | ISO-8601 UTC | Extraction timestamp | Required |
| `raw_file_path` | string | repository-relative path | Raw payload location | Required |

**Important:** UN Comtrade and Eurostat are not expected to match exactly. They use different reporting perspectives and can differ due to timing, valuation, partner assignment, revisions, coverage and classification detail. Keep both source series and create a comparison table; do not overwrite one with the other.

## 5. Product classification and CBAM scope: `dim_cbam_product`

### Grain

One row per **CN code × CN nomenclature year × regulatory scope version**. If a source legal entry covers a code prefix, expand it to CN8 only using an authoritative annual CN nomenclature and retain the original legal scope expression.

| Canonical field | Type | Unit / format | Definition | Validation / notes |
|---|---|---|---|---|
| `cn_code` | string | CN8 or source legal prefix | EU product code | Preserve leading zeros and original string |
| `cn_version_year` | integer | year | CN nomenclature year | Must match trade observation version |
| `cn_description` | string | official description | Description for that CN version | Source from official nomenclature |
| `hs6_prefix` | string | six digits | HS-level prefix corresponding to the CN code | Cross-reference only; not a substitute for CN8 |
| `cbam_sector` | string | `iron_and_steel` | CBAM sector classification | Controlled vocabulary |
| `aggregated_goods_category` | string | official category | CBAM aggregated goods category | Use current applicable methodology mapping |
| `cbam_covered_flag` | boolean | true / false | Whether the product is within the relevant CBAM scope | Must be supported by exact legal/reference mapping |
| `coverage_note` | string | text | Scope exception, partial inclusion or condition | Required where scope is not a simple full prefix |
| `scope_effective_from` | date / null | date | Effective start of the cited scope version | Do not infer if not specified |
| `scope_effective_to` | date / null | date | Effective end date, if superseded | Nullable for current open-ended version |
| `legal_reference` | string | regulation / annex / table | Legal source for coverage | Required |
| `guidance_reference` | string | guidance document / table | Explanatory mapping source | Optional supporting reference; legislation prevails |
| `mapping_status` | string | `validated`, `pending`, `ambiguous`, `excluded` | Review status of mapping | Only validated mappings enter core CBAM calculations |

The current Commission iron and steel guidance lists covered goods and explains how 4-, 5- or 6-digit entries relate to CN8 codes. It also notes partial coverage for some products under CN 7205. Therefore, **do not mark all descendants of a broad prefix as covered without checking the relevant legal note and product description**.

## 6. Embedded-emissions reference: `ref_cbam_emissions_default`

### Grain

One row per **CN / aggregated goods category × country-of-production applicability × production route × emissions component × effective year × regulatory version**, as supported by the official table.

| Canonical field | Type | Unit / format | Definition | Validation / notes |
|---|---|---|---|---|
| `cn_code_or_category` | string | CN code or aggregated goods category | Product/category to which the default applies | Retain the exact source level |
| `country_of_production` | string | ISO code or `OTHER` | Country-specific applicability | India-specific value where explicitly listed; otherwise applicable fallback |
| `production_route` | string / null | official route code/name | Production route associated with the value | Do not invent a route if unavailable |
| `emissions_component` | string | direct / indirect / total, as applicable | Type of embedded emissions | Match source annex definition |
| `default_emissions_value` | decimal | source unit | Official default emissions value | Store source value without early rounding |
| `default_emissions_unit` | string | official unit | Unit in source table | Convert only using documented conversion |
| `normalised_intensity_tco2e_per_tonne` | decimal / null | tCO2e/t goods | Normalised value for model use | Populate only after verifying source unit and goods functional unit |
| `default_mark_up_pct` | decimal / null | percentage | Applicable definitive-period mark-up, if relevant | Effective year and sector must be respected |
| `effective_year` | integer | year | Year for which the value applies | Required |
| `regulation_reference` | string | official act and annex | Legal source | Required |
| `source_table_reference` | string | annex/table/row | Exact location of input | Required for traceability |
| `retrieved_at_utc` | timestamp | ISO-8601 UTC | Retrieval time | Required |

Default emissions are regulatory fallback/model inputs, not measurements of a named Indian plant. Some iron and steel values and benchmarks distinguish production routes. The model must not imply that trade data reveals the actual route used by an exporter.

## 7. Free-allocation benchmark reference: `ref_cbam_benchmark`

### Grain

One row per **CN code or applicable goods category × production route × effective year × regulation version**.

| Canonical field | Type | Unit / format | Definition | Validation / notes |
|---|---|---|---|---|
| `cn_code_or_category` | string | CN / category | Product or category to which benchmark applies | Preserve exact source level |
| `production_route` | string / null | official route | Relevant production route | Required when benchmark is route-specific |
| `benchmark_value` | decimal | source unit | Published free-allocation benchmark | No assumed value |
| `benchmark_unit` | string | source unit | Unit in legal table | Verify before normalising |
| `effective_year` | integer | year | Application year | Required |
| `regulation_reference` | string | legal act / annex | Source regulation | Required |
| `source_table_reference` | string | annex/table/column | Exact source location | Required |
| `retrieved_at_utc` | timestamp | ISO-8601 UTC | Retrieval timestamp | Required |

This reference is required for a later adjusted CBAM model. The first gross-cost screening indicator will not be presented as adjusted CBAM liability.

## 8. Certificate price reference: `ref_cbam_certificate_price`

### Grain

One row per **published price period × price methodology/version**.

| Canonical field | Type | Unit / format | Definition | Validation / notes |
|---|---|---|---|---|
| `price_period_start` | date | date | Start of applicable price period | Required |
| `price_period_end` | date | date | End of applicable price period | Required |
| `price_frequency` | string | quarterly / weekly | Official pricing frequency | Preserve policy regime |
| `certificate_price_eur_per_tco2e` | decimal | EUR/tCO2e | Published CBAM certificate price | Required for a price scenario |
| `publication_date` | date | date | Date price was published | Required if available |
| `source_reference` | string | Commission page / legal reference | Origin of the price | Required |
| `retrieved_at_utc` | timestamp | ISO-8601 UTC | Retrieval timestamp | Required |

Use the official CBAM certificate-price series. Do not substitute a generic EU ETS spot quote without documenting the proxy and its limitations.

## 9. Analytical output: `mart_cbam_steel_exposure`

### Grain

One row per **reference year × EU reporter × CN8 × CN version × emissions/default assumption version × scenario**. If the model aggregates across reporters or products, create a separate aggregated table rather than changing this grain silently.

| Canonical field | Type | Unit / format | Definition | Calculation / notes |
|---|---|---|---|---|
| `reference_year` | integer | year | Year of historical trade | 2022–2025 |
| `reporter_code` | string | Eurostat code | EU importing country | EU-27 member state; aggregate series kept separate |
| `cn_code` | string | CN8 | Imported product code | Validated CBAM product only |
| `cn_version_year` | integer | year | Product nomenclature version | Required |
| `trade_value_eur` | decimal | EUR | EU import value from India | From Eurostat |
| `quantity_100kg` | decimal / null | 100 kg | Source quantity indicator | Retain for traceability |
| `quantity_tonnes` | decimal / null | tonnes | Imported mass in tonnes | `quantity_100kg × 0.1`, if source quantity represents the relevant mass |
| `emissions_intensity_tco2e_per_tonne` | decimal / null | tCO2e/t | Selected emissions assumption | Default or other explicitly identified basis |
| `emissions_basis` | string | default / actual / scenario | Basis of emissions intensity | First release expected to use documented defaults/scenarios |
| `production_route_assumption` | string / null | official route | Selected route assumption | Leave null or scenario-tag where route is unknown; do not silently infer |
| `estimated_embedded_emissions_tco2e` | decimal / null | tCO2e | Estimated emissions embodied in imported volume | `quantity_tonnes × emissions_intensity` |
| `certificate_price_eur_per_tco2e` | decimal / null | EUR/tCO2e | Scenario/reference price | From official price table or explicit scenario |
| `gross_carbon_cost_proxy_eur` | decimal / null | EUR | Gross screening indicator | `estimated_embedded_emissions_tco2e × certificate_price_eur_per_tco2e` |
| `adjusted_cbam_cost_estimate_eur` | decimal / null | EUR | More complete indicative estimate | Null until required legal adjustment inputs and methodology are implemented and tested |
| `scenario_id` | string | scenario key | Identifies price/emissions assumptions | Required for scenario output |
| `regulatory_reference_date` | date | date | CBAM rule vintage used for the model | Required |
| `model_version` | string | version | Calculation model version | Required |

## 10. Scenario assumptions: `ref_exposure_scenario`

| Field | Type | Unit / format | Definition |
|---|---|---|---|
| `scenario_id` | string | unique key | Stable scenario identifier |
| `scenario_name` | string | text | Human-readable scenario name |
| `price_change_pct` | decimal | percentage | Assumed change to the selected certificate price |
| `emissions_intensity_change_pct` | decimal | percentage | Assumed change to selected emissions intensity |
| `base_price_period` | string | price period | Reference price period |
| `description` | string | text | Assumptions and intended interpretation |
| `created_at_utc` | timestamp | ISO-8601 UTC | Scenario creation timestamp |

Scenarios are sensitivity tests, not predictions. Every displayed output must identify the scenario assumptions used.

## 11. Data-quality rules

| Rule ID | Rule | Severity / action |
|---|---|---|
| `DQ-001` | `reference_year` must be 2022–2025 in the historical baseline | Reject or quarantine out-of-scope records |
| `DQ-002` | Main Eurostat trade series must resolve to partner India and flow imports | Reject records with wrong partner/flow |
| `DQ-003` | Product code must be stored as text and matched to its CN version | Reject or quarantine unmapped code/version pairs |
| `DQ-004` | Product must have a validated CBAM scope mapping before inclusion in exposure marts | Exclude pending/ambiguous mappings from core totals |
| `DQ-005` | EU-27 aggregate reporter must never be added to member-state reporter rows | Prevent double-counting |
| `DQ-006` | One source indicator must have a known unit before it is converted or aggregated | Quarantine unknown units |
| `DQ-007` | `quantity_100kg` converts to tonnes using × 0.1 only where its source unit is confirmed | Test conversion and preserve original value |
| `DQ-008` | Missing quantity must not be replaced with zero | Retain null and exclude from mass-based emissions calculations |
| `DQ-009` | Detect duplicates at the defined source-observation grain | Investigate before deduplicating |
| `DQ-010` | Product mapping joins must not multiply trade values | Assert row counts and control totals before/after joins |
| `DQ-011` | Preserve observation status and special-value information | Do not silently treat suppressed/missing values as zero |
| `DQ-012` | Every emissions and benchmark input must retain regulation, annex/table and effective-year references | Reject untraceable assumptions |
| `DQ-013` | Gross carbon-cost proxy must not be labelled actual CBAM liability | Enforce in field naming, documentation and dashboard labels |
| `DQ-014` | Historical 2022–2025 scenarios must be labelled retrospective/counterfactual | Enforce in report/dashboard metadata |

## 12. Important analytical distinctions

### India's share of EU imports

For a given year, CN product and EU reporter/aggregate:

`EU imports from India ÷ EU imports from all partners`

This measures India's share in the EU import market for the product.

### India's export dependence on the EU

For a given year and comparable product:

`India's exports to the EU ÷ India's exports to the world`

This requires an India-reported worldwide export denominator, typically from UN Comtrade. Because the numerator and denominator may come from different reporting systems, reconcile product codes, periods, units and valuation basis, and disclose any remaining asymmetry.

### Gross carbon-cost screening indicator

`Imported quantity (tonnes) × selected emissions intensity (tCO2e/tonne) × selected certificate price (EUR/tCO2e)`

This is a gross screening indicator only. It does not by itself include the definitive-period free-allocation adjustment, eligible carbon price paid in the country of origin or all other legally required calculation steps.

## 13. Outstanding items before production use

1. Inspect the existing two-record UN Comtrade HS 7208 extract and verify its raw response, quantity and value units.
2. Retrieve the Eurostat Comext dataset metadata and confirm the exact dimension codes, indicator codes, unit codes and status flags used by the current API response.
3. Build the annual 2022–2025 EU imports-from-India extraction for validated iron and steel CN8 codes.
4. Obtain the official annual CN nomenclature files/correspondence tables needed to version product codes and map HS6 to CN8.
5. Build the CBAM iron and steel scope reference table from the applicable legal Annex and Commission guidance, including exceptions and partial coverage notes.
6. Extract and validate definitive-period emissions defaults and free-allocation benchmarks, with country and production-route distinctions.
7. Define and test the first gross exposure screening model before attempting adjusted CBAM cost estimates.

