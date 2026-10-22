# Amazon Product Data Transformation Contract

## Purpose

This contract defines how the raw Amazon product export is converted into an
analytics-ready product observation dataset. The raw value should be retained
when it contains information that cannot be represented safely by a single
typed field.

## Source

- Input file: `amazon_sales_data_uncleaned.csv`
- Grain: one scraped product observation per row
- Missing-value convention: use `NULL` for unknown or unavailable values
- Do not replace unknown values with zero

## Transformation rules

| Source field | Target field(s) | Target type | Transformation and validation |
|---|---|---|---|
| `Title` | `title` | string | Trim leading/trailing whitespace. Require a non-empty value. Do not lowercase, title-case, or use alone for deduplication. |
| `Rating` | `rating` | decimal | Extract the numeric portion from text such as `4.6 out of 5 stars`. Accept only values from 0 through 5. Invalid or missing values become `NULL`. |
| `Number_of_reviews` | `number_of_reviews` | integer | Remove thousands separators, then convert to integer. Accept values greater than or equal to 0. Invalid or missing values become `NULL`. |
| `bought_in_last_month` | `monthly_purchases_lower_bound` | integer | Parse values such as `100+`, `1K+`, and `20K+` as 100, 1,000, and 20,000. Scraper text that does not describe purchases becomes `NULL`. |
| `Current/discounted_price` | `current_price` | decimal(10,2) | Remove currency symbols and thousands separators. Accept values greater than or equal to 0. Missing values remain `NULL`. |
| `Price_on_variant` | `price_on_variant_raw` | string | Preserve unchanged while its meaning is profiled. Do not cast or calculate with it yet. |
| `Listed_price` | `listed_price`, `has_discount` | decimal(10,2), boolean | Parse numeric prices. Convert `No Discount` to `listed_price = NULL` and `has_discount = FALSE`. A valid separate list price produces `has_discount = TRUE` only when it exceeds `current_price`. |
| `is_best_seller` | `badge_text`, `is_best_seller` | string, boolean | Preserve the original badge text. Set `is_best_seller = TRUE` only for `Best Seller`; other badge text becomes `FALSE`. |
| `is_sponsored` | `is_sponsored` | boolean | Map `Organic` to `FALSE` and `Sponsored` to `TRUE`. Unexpected values become invalid records for review. |
| `is_couponed` | `coupon_text`, `is_couponed`, `coupon_type`, `coupon_value` | string, boolean, category, decimal | `No Coupon` maps to `FALSE`. Parse `Save 15% with coupon` as percentage 15 and `Save $16.00 with coupon` as fixed amount 16. Preserve the original text. |
| `buy_box_availability` | `buy_box_action` | string | Preserve `Add to cart` as the observed action. Missing values remain `NULL`; do not infer that they mean unavailable. |
| `delivery_details` | `delivery_details_raw`, `delivery_is_free`, `has_fastest_delivery`, `has_delivery_threshold` | string, boolean, boolean, boolean | Preserve raw text. Detect explicit phrases such as `FREE delivery`, `fastest delivery`, and `on $35 of items`. Do not infer dates until year and timezone handling are defined. |
| `sustainability_badges` | `sustainability_badges_raw`, `primary_badge`, `additional_badge_count` | string, string, integer | Preserve raw text. Extract the main label and a suffix such as `+3 more` when present. Do not derive a generic sustainability boolean. |
| `image_url` | `image_url` | URL string | Trim and validate as an HTTPS URL. Preserve the URL as text. Do not use it as a product key. |
| `product_url` | `product_url_raw`, `asin`, `product_path` | string, string, string | Preserve the raw relative URL. Extract the 10-character ASIN from direct `/dp/` paths or encoded sponsored links. Normalize the clean path to `/dp/{asin}`. Missing source URLs produce `NULL`. |
| `collected_at` | `collected_at` | timestamp | Parse `dd-MM-yyyy HH:mm`. Treat the result as timezone-unknown/local time because the source provides no timezone. |

## Record-level validation

The ETL should produce a validation report containing:

- total input and output row counts
- rejected-row count and rejection reasons
- null counts for every target field
- invalid rating, review, purchase, and price counts
- invalid URL and ASIN counts
- unparseable timestamp counts
- duplicate checks based on observation identity, not `title` alone

## Pending semantic decision

`Price_on_variant` is not yet ready for transformation. Its values include
variant descriptions such as `basic variant price: 2.4GHz` and values ending
in `nan`, so the next profiling task is to determine whether the field is a
price, a variant label, or a scraper artifact.

## Output model for version 1

The first cleaned dataset should contain the typed fields above plus selected
raw fields ending in `_raw` or `_text`. Keeping both forms makes the pipeline
auditable and allows transformation rules to be improved without recollecting
the source data.
