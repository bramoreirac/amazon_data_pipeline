import unittest
from datetime import datetime

from etl_script import (
    clean_buy_box_action,
    clean_collected_at,
    clean_coupon,
    clean_delivery_details,
    clean_image_url,
    clean_is_best_seller,
    clean_is_sponsored,
    clean_listed_price,
    clean_monthly_pur_lb,
    clean_n_reviews,
    clean_price,
    clean_product_url,
    clean_rating,
    clean_sustainability,
    clean_title,
    clean_var_metadata,
    transform_row,
)


class CleaningFunctionTests(unittest.TestCase):
    def test_clean_title(self):
        assert clean_title("") is None
        assert clean_title(" ") is None
        assert clean_title(None) is None
        assert clean_title(" wireless headset ") == "wireless headset"

    def test_clean_rating(self):
        assert clean_rating("") is None
        assert clean_rating(None) is None
        assert clean_rating("out of 5 stars") is None
        assert clean_rating("6.2 out of 5 stars") is None
        assert clean_rating("5 out of 5 stars") == 5.0
        assert clean_rating(" 4.6 out of 5 stars") == 4.6
        assert clean_rating("4.6 out of 5 stars") == 4.6

    def test_clean_n_reviews(self):
        assert clean_n_reviews("") is None
        assert clean_n_reviews(None) is None
        assert clean_n_reviews("5,257") == 5257
        assert isinstance(clean_n_reviews("5,257"), int)
        assert clean_n_reviews(" 1,234 ") == 1234
        assert clean_n_reviews("5,25") is None
        assert clean_n_reviews("-5") is None
        assert clean_n_reviews("25.5") is None
        assert clean_n_reviews("unknown") is None

    def test_clean_monthly_pur_lb(self):
        assert clean_monthly_pur_lb("100+ bought in past month") == 100
        assert clean_monthly_pur_lb("1K+ bought in past month") == 1000
        assert clean_monthly_pur_lb("1k+ bought in past month") == 1000
        assert clean_monthly_pur_lb(" 500+ bought in past month") == 500
        assert clean_monthly_pur_lb("No featured offers available") is None
        assert clean_monthly_pur_lb(None) is None

    def test_clean_price(self):
        assert clean_price("$29.99") == 29.99
        assert clean_price("$1,299.00") == 1299.00
        assert isinstance(clean_price("$29.99"), float)
        assert clean_price("NaN") is None
        assert clean_price("$1,29.00") is None
        assert clean_price("$0.00") == 0.0
        assert clean_price("0") == 0.0
        assert clean_price("-5.00") is None
        assert clean_price("$abc") is None

    def test_clean_var_metadata(self):
        assert clean_var_metadata(" basic variant price: 2.4GHz ") == "basic variant price: 2.4GHz"
        assert clean_var_metadata("basic variant price: nan") == "basic variant price: nan"
        assert clean_var_metadata("") is None
        assert clean_var_metadata("   ") is None
        assert clean_var_metadata(None) is None

    def test_clean_listed_price(self):
        assert clean_listed_price("$99.99", "$79.99") == (99.99, True)
        assert clean_listed_price("$99.99", "$99.99") == (99.99, False)
        assert clean_listed_price("$79.99", "$99.99") == (79.99, False)
        assert clean_listed_price(" No Discount ", "$79.99") == (None, False)
        assert clean_listed_price(None, "$79.99") == (None, None)
        assert clean_listed_price("$99.99", None) == (99.99, None)

    def test_clean_is_best_seller(self):
        assert clean_is_best_seller(" Best Seller ") == ("Best Seller", True)
        assert clean_is_best_seller("best seller") == ("best seller", True)
        assert clean_is_best_seller("No Badge") == ("No Badge", False)
        assert clean_is_best_seller("Limited time deal") == ("Limited time deal", False)
        assert clean_is_best_seller(" ") == (None, None)
        assert clean_is_best_seller(None) == (None, None)

    def test_clean_is_sponsored(self):
        assert clean_is_sponsored("Sponsored") is True
        assert clean_is_sponsored(" sponsored ") is True
        assert clean_is_sponsored("Organic") is False
        assert clean_is_sponsored(" organic ") is False
        assert clean_is_sponsored("") is None
        assert clean_is_sponsored("   ") is None
        assert clean_is_sponsored(None) is None
        assert clean_is_sponsored("Unknown") is None

    def test_clean_coupon(self):
        assert clean_coupon("No Coupon") == (False, None, None)
        assert clean_coupon(" no coupon ") == (False, None, None)
        assert clean_coupon("Save 15% with coupon") == (True, "percent", 15.0)
        assert clean_coupon("Save 7.5% with coupon") == (True, "percent", 7.5)
        assert clean_coupon("Save $16.00 with coupon") == (True, "fixed", 16.0)
        assert clean_coupon("Save with coupon") == (None, None, None)
        assert clean_coupon("Save $5 and 10% with coupon") == (None, None, None)
        assert clean_coupon("Save 150% with coupon") == (None, None, None)
        assert clean_coupon(None) == (None, None, None)

    def test_clean_buy_box_action(self):
        assert clean_buy_box_action(" Add to cart ") == "Add to cart"
        assert clean_buy_box_action("See all buying options") == "See all buying options"
        assert clean_buy_box_action("") is None
        assert clean_buy_box_action("   ") is None
        assert clean_buy_box_action(None) is None

    def test_clean_delivery_details(self):
        assert clean_delivery_details(None) == (None, None, None, None)
        assert clean_delivery_details("Delivery Mon, Sep 1") == (
            "Delivery Mon, Sep 1", False, False, False
        )
        delivery_text = (
            "FREE delivery Wed, Sep 3 on $35 of items shipped by Amazon "
            "Or fastest delivery Sun, Aug 31"
        )
        assert clean_delivery_details(delivery_text) == (
            delivery_text, True, True, True
        )

    def test_clean_sustainability(self):
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

    def test_clean_image_url(self):
        assert clean_image_url(
            " https://m.media-amazon.com/images/I/example.jpg "
        ) == "https://m.media-amazon.com/images/I/example.jpg"
        assert clean_image_url("http://example.com/image.jpg") is None
        assert clean_image_url("/images/example.jpg") is None
        assert clean_image_url("not a url") is None
        assert clean_image_url("https:///image.jpg") is None
        assert clean_image_url("") is None
        assert clean_image_url(None) is None

    def test_clean_product_url(self):
        direct_url = "/Product-Name/dp/B0DNZB7TQG/ref=sr_1"
        assert clean_product_url(direct_url) == (
            direct_url, "B0DNZB7TQG", "/dp/B0DNZB7TQG"
        )
        encoded_url = "/sspa/click?url=%2FProduct-Name%2Fdp%2FB0DNZB7TQG%2Fref"
        assert clean_product_url(encoded_url) == (
            encoded_url, "B0DNZB7TQG", "/dp/B0DNZB7TQG"
        )
        assert clean_product_url("/products/example") == (
            "/products/example", None, None
        )
        assert clean_product_url("") == (None, None, None)
        assert clean_product_url(None) == (None, None, None)

    def test_clean_collected_at(self):
        assert clean_collected_at("21-08-2025 11:14") == datetime(2025, 8, 21, 11, 14)
        assert clean_collected_at(" 21-08-2025 11:14 ") == datetime(2025, 8, 21, 11, 14)
        assert clean_collected_at("2025-08-21 11:14") is None
        assert clean_collected_at("31-02-2025 11:14") is None
        assert clean_collected_at("") is None
        assert clean_collected_at(None) is None

    def test_transform_row_with_sample_record(self):
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
            "delivery_details": (
                "FREE delivery Wed, Sep 3 on $35 of items shipped by Amazon "
                "Or fastest delivery Sun, Aug 31"
            ),
            "sustainability_badges": "Energy efficiency +3 more",
            "image_url": "https://m.media-amazon.com/images/I/example.jpg",
            "product_url": "/sspa/click?url=%2FWireless-Headset%2Fdp%2FB0DNZB7TQG%2Fref",
            "collected_at": "21-08-2025 11:14",
        }

        cleaned = transform_row(sample)

        assert cleaned["title"] == "wireless headset"
        assert cleaned["rating"] == 4.6
        assert cleaned["number_of_reviews"] == 2457
        assert cleaned["current_price"] == 29.99
        assert cleaned["has_discount"] is True
        assert cleaned["is_couponed"] is True
        assert cleaned["asin"] == "B0DNZB7TQG"
        assert cleaned["collected_at"] == datetime(2025, 8, 21, 11, 14)


if __name__ == "__main__":
    unittest.main()
