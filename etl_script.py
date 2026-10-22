import re
import csv
from typing import Any
from urllib.parse import urlparse
from urllib.parse import unquote
from datetime import datetime

# Clean title function
def clean_title(value: str | None) -> str | None:
    if value is None:
        return None

    clean_value = value.strip()
    return clean_value or None

# Clean rating function
def clean_rating(value: str | None) -> float | None:
    if value is None:
        return None

    match = re.search(r"^\s*\d+(?:\.\d+)?", value)

    if match:
        clean_value = float(match.group())
        return clean_value if (0 <= clean_value <= 5) else None
    return None

# Clean review numbers function
def clean_n_reviews(value: str | None) -> int | None:
    if value is None:
        return None

    pattern = r"^\s*\d+(?:,\d{3})*\s*$"
    match = re.search(pattern, value)

    if match:
        clean_value = match.group().strip().replace(",", "")
        return int(clean_value)
    return None

# Clean lower bound of monthly purchases
def clean_monthly_pur_lb(value: str | None) -> int | None:
    if value is None:
        return None

    pattern = r"^\s*(\d+)([Kk])?\+"
    match = re.search(pattern, value)

    if match:
        if match.group(2) in ("K", "k"):
            clean_value = int(match.group(1)) * 1000
            return clean_value
        return int(match.group(1))
    return None

# Clean price, removes dollar sign
def clean_price(value: str | None) -> float | None:
    if value is None:
        return None

    pattern = r"^\s*\$?(\d+)(?:,\d{3})*(?:\.\d+)?\s*$"
    match = re.search(pattern, value)

    if match:
        clean_value = match.group().strip().replace("$", "").replace(",", "")
        return float(clean_value)
    return None

# Clean metadata, stores normalized text if not None
def clean_var_metadata(value: str | None) -> str | None:
    if value is None:
        return None

    clean_value = value.strip()
    return clean_value or None

# Clean listed price, finds is any discount is present
def clean_listed_price(
    listed_price: str | None,
    current_price: str | None,
) -> tuple[float | None, bool | None]:
    # Normalizing listed price
    if listed_price is None:
        norm_lp = None
    else:
        norm_lp = listed_price.strip().lower()

    if norm_lp == "no discount":
        return None, False
    else:
        clean_lp = clean_price(norm_lp)
        clean_cp = clean_price(current_price)
        if clean_lp is None:
            return None, None
        elif clean_cp is None:
            return clean_lp, None
        else:
            if clean_lp > clean_cp:
                return clean_lp, True
            else:
                return clean_lp, False

def clean_is_best_seller(
    badge_text: str | None,
) -> tuple[str | None, bool | None]:
    # Normalizing badge_text
    if badge_text is None:
        norm_badge_text = None
        return norm_badge_text, None
    else:
        norm_badge_text = badge_text.strip().lower()
        if len(norm_badge_text) == 0:
            norm_badge_text = None
            return norm_badge_text, None

    # Evaluating if badge_text is bestseller
    if norm_badge_text == "best seller":
        return clean_title(badge_text), True
    else:
        return clean_title(badge_text), False

# Clean Sponsored value
def clean_is_sponsored(value: str | None) -> bool | None:
    normalized = clean_title(value)

    if normalized is None:
        return None

    return {
        "sponsored": True,
        "organic": False,
    }.get(normalized.lower())

# Clean coupon discount, saves either percentage of fixed-value
def clean_coupon(
    value: str | None,
) -> tuple[bool | None, str | None, float | None]:
    normalized = clean_title(value)

    if normalized is None:
        return None, None, None

    if normalized.lower() == "no coupon":
        return False, None, None
    else:
        pattern_percent = r"\d+(?:\.\d+)?%"
        pattern_fixed = r"\$\d+(?:\.\d+)?"

        match_percent = re.search(pattern_percent, normalized)
        match_fixed = re.search(pattern_fixed, normalized)

        if match_percent and match_fixed:
            return None, None, None
        if match_percent:
            clean_match_percent = match_percent.group().replace("%", "")
            percentage = float(clean_match_percent)

            if not 0 <= percentage <= 100:
                return None, None, None

            return True, "percent", float(clean_match_percent)
        if match_fixed:
            clean_match_fixed = match_fixed.group().replace("$", "")
            return True, "fixed", float(clean_match_fixed)
        else:
            return None, None, None

# Clean buy box information, stores normalized text only
def clean_buy_box_action(value: str | None) -> str | None:
    return clean_title(value)

# Clean delivery details, evaluates if free, fast and min amount
def clean_delivery_details(value: str | None) -> tuple[str | None, bool | None, bool | None, bool | None]:
    normalized = clean_title(value)

    if normalized is None:
        return None, None, None, None

    pattern_free = r"free delivery"
    pattern_fast = r"fastest delivery"
    pattern_amount = r"on\s+\$\d+(?:\.\d+)?\s+of items"

    match_free = re.search(pattern_free, normalized, re.IGNORECASE)
    match_fast = re.search(pattern_fast, normalized, re.IGNORECASE)
    match_amount = re.search(pattern_amount, normalized, re.IGNORECASE)

    return normalized, bool(match_free), bool(match_fast), bool(match_amount)

def clean_sustainability(
    value: str | None,
) -> tuple[str | None, str | None, int | None]:
    normalized = clean_title(value)

    if normalized is None:
        return None, None, None

    pattern = r"^(.+?)(?:\s+\+(\d+)\s+more)?$"
    match = re.search(pattern, normalized, re.IGNORECASE)
    badge_count = 0

    if match:
        primary_badge = match.group(1)
        if match.group(2) is not None:
            badge_count = int(match.group(2))
        return normalized, primary_badge, badge_count
    else:
        return None, None, None

def clean_image_url(value: str | None) -> str | None:
    # Return a normalized HTTPS image URL, or ``None`` if it is invalid.
    normalized = clean_title(value)
    if normalized is None:
        return None

    try:
        parsed = urlparse(normalized)
        is_valid = parsed.scheme.casefold() == "https" and bool(parsed.hostname)
    except ValueError:
        return None

    return normalized if is_valid else None

# Clean product url to get ASIN code
def clean_product_url(value: str | None) -> tuple[str | None, str | None, str | None]:
    normalized = clean_title(value)
    if normalized is None:
        return None, None, None

    decoded_url = unquote(normalized)
    pattern_asin = r"/dp/([A-Z0-9]{10})(?:[/?]|$)"

    match = re.search(pattern_asin, decoded_url, re.IGNORECASE)

    if match:
        asin = match.group(1).upper()
        product_path = "/dp/" + asin
        return normalized, asin, product_path
    return normalized, None, None

def clean_collected_at(value: str | None) -> datetime | None:
    normalized = clean_title(value)

    if normalized is None:
        return None

    try:
        return datetime.strptime(normalized, "%d-%m-%Y %H:%M")
    except ValueError:
        return None

def transform_row(raw_row: dict[str, str | None]) -> dict[str, Any]:
    listed_price, has_discount = clean_listed_price(
        raw_row["Listed_price"],
        raw_row["Current/discounted_price"]
    )

    badge_text, is_best_seller = clean_is_best_seller(raw_row["is_best_seller"])
    is_couponed, coupon_type, coupon_value = clean_coupon(raw_row["is_couponed"])
    (
        delivery_details_raw,
        delivery_is_free,
        has_fastest_delivery,
        has_delivery_threshold,
    ) = clean_delivery_details(raw_row["delivery_details"])
    (
        sustainability_badges_raw,
        primary_badge,
        additional_badge_count,
    ) = clean_sustainability(raw_row["sustainability_badges"])
    product_url_raw, asin, product_path = clean_product_url(raw_row["product_url"])

    cleaned_row = {
        "title": clean_title(raw_row["Title"]),
        "rating": clean_rating(raw_row["Rating"]),
        "number_of_reviews": clean_n_reviews(raw_row["Number_of_reviews"]),
        "monthly_purchases_lower_bound": clean_monthly_pur_lb(raw_row["bought_in_last_month"]),
        "current_price": clean_price(raw_row["Current/discounted_price"]),
        "variant_metadata": clean_var_metadata(raw_row["Price_on_variant"]),
        "listed_price": listed_price,
        "has_discount": has_discount,
        "badge_text": badge_text,
        "is_best_seller": is_best_seller,
        "is_sponsored": clean_is_sponsored(raw_row["is_sponsored"]),
        "coupon_text": clean_title(raw_row["is_couponed"]),
        "is_couponed": is_couponed,
        "coupon_type": coupon_type,
        "coupon_value": coupon_value,
        "buy_box_action": clean_buy_box_action(raw_row["buy_box_availability"]),
        "delivery_details_raw": delivery_details_raw,
        "delivery_is_free": delivery_is_free,
        "has_fastest_delivery": has_fastest_delivery,
        "has_delivery_threshold": has_delivery_threshold,
        "sustainability_badges_raw": sustainability_badges_raw,
        "primary_badge": primary_badge,
        "additional_badge_count": additional_badge_count,
        "image_url": clean_image_url(raw_row["image_url"]),
        "product_url_raw": product_url_raw,
        "asin": asin,
        "product_path": product_path,
        "collected_at": clean_collected_at(raw_row["collected_at"]),
    }

    return cleaned_row


if __name__ == "__main__":
    with open("amazon_sales_data_uncleaned.csv", mode="r", encoding="utf-8-sig", newline="") as read_file:
        reader = csv.DictReader(read_file)

        with open("outputs/clean_data.csv", mode="w", encoding="utf-8-sig", newline="") as write_file:
            first_raw_row = next(reader, None)

            if first_raw_row is None:
                print("The CSV has no data rows to transform.")
            else:
                first_clean_row = transform_row(first_raw_row)
                writer = csv.DictWriter(
                    write_file,
                    fieldnames=list(first_clean_row.keys()),
                )
                writer.writeheader()
                writer.writerow(first_clean_row)

                for row in reader:
                    clean_row = transform_row(row)
                    writer.writerow(clean_row)
