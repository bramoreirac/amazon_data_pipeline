import re
from urllib.parse import urlparse
from urllib.parse import unquote
from datetime import datetime

# Clean title function
def clean_title(value):
    if value is None:
        return None

    clean_value = value.strip()
    return clean_value or None

# Clean rating function
def clean_rating(value):
    if value is None:
        return None

    match = re.search(r"^\s*\d+(?:\.\d+)?", value)

    if match:
        clean_value = float(match.group())
        return clean_value if (0 <= clean_value <= 5) else None
    return None

# Clean review numbers function
def clean_n_reviews(value):
    if value is None:
        return None

    pattern = r"^\s*\d+(?:,\d{3})*\s*$"
    match = re.search(pattern, value)

    if match:
        clean_value = match.group().strip().replace(",", "")
        return int(clean_value)
    return None

# Clean lower bound of monthly purchases
def clean_monthly_pur_lb(value):
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
def clean_price(value):
    if value is None:
        return None

    pattern = r"^\s*\$?(\d+)(?:,\d{3})*(?:\.\d+)?\s*$"
    match = re.search(pattern, value)

    if match:
        clean_value = match.group().strip().replace("$", "").replace(",", "")
        return float(clean_value)
    return None

# Clean metadata, stores normalized text if not None
def clean_var_metadata(value):
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
def clean_is_sponsored(value):
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
def clean_buy_box_action(value):
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

    val_free = bool(match_free)
    val_fast = bool(match_fast)
    val_amount = bool(match_amount)

    if match_free:
        val_free = True
    if match_fast:
        val_fast = True
    if match_amount:
        val_amount = True

    return normalized, val_free, val_fast, val_amount

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

def clean_collected_at(value):
    normalized = clean_title(value)

    if normalized is None:
        return None

    try:
        return datetime.strptime(normalized, "%d-%m-%Y %H:%M")
    except ValueError:
        return None

def transform_row(raw_row):
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
    # Evaluating clean_title()
    """"
    assert clean_title("") is None
    assert clean_title(" ") is None
    assert clean_title(None) is None
    assert clean_title(" wireless headset ") == "wireless headset"
    """

    # Evaluating clean_rating()
    """
    assert clean_rating("") is None
    assert clean_rating(None) is None
    assert clean_rating("out of 5 stars") is None
    assert clean_rating("6.2 out of 5 stars") is None
    assert clean_rating("5 out of 5 stars") == 5.0
    assert clean_rating(" 4.6 out of 5 stars") == 4.6
    assert clean_rating("4.6 out of 5 stars") == 4.6
    """

    # Evaluating clean_n_reviews()
    """
    assert clean_n_reviews("") is None
    assert clean_n_reviews(None) is None
    assert clean_n_reviews("5,257") == 5257
    assert isinstance(clean_n_reviews("5,257"), int)
    assert clean_n_reviews(" 1,234 ") == 1234
    assert clean_n_reviews("5,25") is None
    assert clean_n_reviews("-5") is None
    assert clean_n_reviews("25.5") is None
    assert clean_n_reviews("unknown") is None
    """

    # Evaluating clean_monthly_pur_lb()
    """
    assert clean_monthly_pur_lb("100+ bought in past month") == 100
    assert clean_monthly_pur_lb("1K+ bought in past month") == 1000
    assert clean_monthly_pur_lb("1k+ bought in past month") == 1000
    assert clean_monthly_pur_lb(" 500+ bought in past month") == 500
    assert clean_monthly_pur_lb("No featured offers available") is None
    assert clean_monthly_pur_lb(None) is None
    """

    # Evaluating clean_price()
    """
    assert clean_price("$29.99") == 29.99
    assert clean_price("$1,299.00") == 1299.00
    assert isinstance(clean_price("$29.99"), float)
    assert clean_price("NaN") is None
    assert clean_price("$1,29.00") is None
    assert clean_price("$0.00") == 0.0
    assert clean_price("0") == 0.0
    assert clean_price("-5.00") is None
    assert clean_price("$abc") is None
    """

    # Evaluating clean_var_metadata()
    """
    assert clean_var_metadata(" basic variant price: 2.4GHz ") == "basic variant price: 2.4GHz"
    assert clean_var_metadata("basic variant price: nan") == "basic variant price: nan"
    assert clean_var_metadata("") is None
    assert clean_var_metadata("   ") is None
    assert clean_var_metadata(None) is None
    """

    # Evaluating clean_listed_price()
    """
    assert clean_listed_price("$99.99", "$79.99") == (99.99, True)
    assert clean_listed_price("$99.99", "$99.99") == (99.99, False)
    assert clean_listed_price("$79.99", "$99.99") == (79.99, False)
    assert clean_listed_price(" No Discount ", "$79.99") == (None, False)
    assert clean_listed_price(None, "$79.99") == (None, None)
    assert clean_listed_price("$99.99", None) == (99.99, None)
    """

    # Evaluating clean_is_best_seller()
    """
    assert clean_is_best_seller(" Best Seller ") == ("Best Seller", True)
    assert clean_is_best_seller("best seller") == ("best seller", True)
    assert clean_is_best_seller("No Badge") == ("No Badge", False)
    assert clean_is_best_seller("Limited time deal") == ("Limited time deal", False)
    assert clean_is_best_seller(" ") == (None, None)
    assert clean_is_best_seller(None) == (None, None)
    """

    # Evaluating clean_is_sponsored()
    """
    assert clean_is_sponsored("Sponsored") is True
    assert clean_is_sponsored(" sponsored ") is True
    assert clean_is_sponsored("Organic") is False
    assert clean_is_sponsored(" organic ") is False
    assert clean_is_sponsored("") is None
    assert clean_is_sponsored("   ") is None
    assert clean_is_sponsored(None) is None
    assert clean_is_sponsored("Unknown") is None
    """

    # Evaluating clean_coupon()
    """
    assert clean_coupon("No Coupon") == (False, None, None)
    assert clean_coupon(" no coupon ") == (False, None, None)
    assert clean_coupon("Save 15% with coupon") == (True, "percent", 15.0)
    assert clean_coupon("Save 7.5% with coupon") == (True, "percent", 7.5)
    assert clean_coupon("Save $16.00 with coupon") == (True, "fixed", 16.0)
    assert clean_coupon("Save with coupon") == (None, None, None)
    assert clean_coupon("Save $5 and 10% with coupon") == (None, None, None)
    assert clean_coupon("Save 150% with coupon") == (None, None, None)
    assert clean_coupon(None) == (None, None, None)
    """

    # Evaluating clean_buy_action()
    """
    assert clean_buy_box_action(" Add to cart ") == "Add to cart"
    assert clean_buy_box_action("See all buying options") == "See all buying options"
    assert clean_buy_box_action("") is None
    assert clean_buy_box_action("   ") is None
    assert clean_buy_box_action(None) is None
    """

    # Evaluating clean_delivery_details()
    """
    assert clean_delivery_details(None) == (None, None, None, None)
    assert clean_delivery_details("Delivery Mon, Sep 1") == (
        "Delivery Mon, Sep 1", False, False, False
    )
    assert clean_delivery_details(
        "FREE delivery Wed, Sep 3 on $35 of items shipped by Amazon "
        "Or fastest delivery Sun, Aug 31"
    ) == (
               "FREE delivery Wed, Sep 3 on $35 of items shipped by Amazon "
               "Or fastest delivery Sun, Aug 31",
               True, True, True
           )
    """

    # Evaluating clean_sustainability()
    """
    assert clean_sustainability("Carbon impact") == (
        "Carbon impact", "Carbon impact", 0
    )
    assert clean_sustainability("Energy efficiency +3 more") == (
        "Energy efficiency +3 more", "Energy efficiency", 3
    )
    assert clean_sustainability("Works with Alexa") == (
        "Works with Alexa", "Works with Alexa", 0
    )
    assert clean_sustainability("Alexa Built-in") == (
        "Alexa Built-in", "Alexa Built-in", 0
    )
    assert clean_sustainability(None) == (None, None, None)
    """

    # Evaluating clean_image_url()
    """
    assert clean_image_url(
        " https://m.media-amazon.com/images/I/example.jpg "
    ) == "https://m.media-amazon.com/images/I/example.jpg"
    assert clean_image_url("http://example.com/image.jpg") is None
    assert clean_image_url("/images/example.jpg") is None
    assert clean_image_url("not a url") is None
    assert clean_image_url("https:///image.jpg") is None
    assert clean_image_url("") is None
    assert clean_image_url(None) is None
    """

    # Evaluating clean_product_url()
    """
    assert clean_product_url(
        "/Product-Name/dp/B0DNZB7TQG/ref=sr_1"
    ) == (
               "/Product-Name/dp/B0DNZB7TQG/ref=sr_1",
               "B0DNZB7TQG",
               "/dp/B0DNZB7TQG",
           )
    assert clean_product_url(
        "/sspa/click?url=%2FProduct-Name%2Fdp%2FB0DNZB7TQG%2Fref"
    ) == (
               "/sspa/click?url=%2FProduct-Name%2Fdp%2FB0DNZB7TQG%2Fref",
               "B0DNZB7TQG",
               "/dp/B0DNZB7TQG",
           )
    assert clean_product_url("/products/example") == (
        "/products/example",
        None,
        None,
    )
    assert clean_product_url("") == (None, None, None)
    assert clean_product_url(None) == (None, None, None)
    """

    # Evaluating clean_collected_at()

    """
    assert clean_collected_at("21-08-2025 11:14") == datetime(2025, 8, 21, 11, 14)
    assert clean_collected_at(" 21-08-2025 11:14 ") == datetime(2025, 8, 21, 11, 14)
    assert clean_collected_at("2025-08-21 11:14") is None
    assert clean_collected_at("31-02-2025 11:14") is None
    assert clean_collected_at("") is None
    assert clean_collected_at(None) is None
    """

    sample = {
        "Title": " wireless headset ",
        "Rating": "4.6 out of 5 stars",
        "Number_of_reviews": "2,457",
        "bought_in_last_month": "1K+ bought in past month",
        "Current/discounted_price": "$29.99",
        "Price_on_variant": "basic variant price: 2.4GHz",
        "Listed_price": "$39.99",
        "is_best_seller": "Best Seller",
        "is_sponsored": "Sponsored",
        "is_couponed": "Save 15% with coupon",
        "buy_box_availability": "Add to cart",
        "delivery_details": "FREE delivery Wed, Sep 3 on $35 of items shipped by Amazon Or fastest delivery Sun, Aug 31",
        "sustainability_badges": "Energy efficiency +3 more",
        "image_url": "https://m.media-amazon.com/images/I/example.jpg",
        "product_url": "/sspa/click?url=%2FWireless-Headset%2Fdp%2FB0DNZB7TQG%2Fref",
        "collected_at": "21-08-2025 11:14",
    }
    print(transform_row(sample))
