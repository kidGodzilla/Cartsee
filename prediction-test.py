import unittest

from model import Order, Item, OrderLineItem, User, PredictedCart
from model import db

from server import app, connect_to_db

from datetime import datetime

from numpy import array, mean, std


class PredictCartTestCase(unittest.TestCase):

    def setUp(self):
        """Sets up user and multiple orders, items and line items in db session for
        testing methods on Order, Item, and User classes that are used in prediction algorithm"""

        test_gmail = "test1@gmail.com"
        self.user = User(user_gmail=test_gmail, access_token="test_token")

        db.session.add(self.user)

        date_string_1 = "16 November 2014"
        delivery_date_1 = datetime.strptime(date_string_1, "%d %B %Y")
        amazon_fresh_order_id_1 = "test1"

        self.order_1 = Order(amazon_fresh_order_id=amazon_fresh_order_id_1,
                           delivery_date=delivery_date_1,
                           delivery_day_of_week="Sunday",
                           delivery_time="10:00am - 1:00pm",
                           user_gmail=test_gmail)


        date_string_2 = "13 February 2015"
        delivery_date_2 = datetime.strptime(date_string_2, "%d %B %Y")
        amazon_fresh_order_id_2 = "test2"

        self.order_2 = Order(amazon_fresh_order_id=amazon_fresh_order_id_2,
                           delivery_date=delivery_date_2,
                           delivery_day_of_week="Friday",
                           delivery_time="3:00pm - 6:00pm",
                           user_gmail=test_gmail)

        date_string_3 = "13 May 2015"
        delivery_date_3 = datetime.strptime(date_string_3, "%d %B %Y")
        amazon_fresh_order_id_3 = "test3"

        self.order_3 = Order(amazon_fresh_order_id=amazon_fresh_order_id_3,
                           delivery_date=delivery_date_3,
                           delivery_day_of_week="Monday",
                           delivery_time="3:00pm - 6:00pm",
                           user_gmail=test_gmail)

        db.session.add(self.order_1)
        db.session.add(self.order_2)
        db.session.add(self.order_3)


        self.item_1 = Item(description="Test item 1",
                         description_key="testitem1")

        self.item_2 = Item(description="Test item 2",
                         description_key="testitem2")


        db.session.add(self.item_1)
        db.session.add(self.item_2)

        db.session.flush()

        self.order_line_item_1 = OrderLineItem(amazon_fresh_order_id=amazon_fresh_order_id_1,
                                             item_id=self.item_1.item_id,
                                             unit_price_cents=100,
                                             quantity=2)

        self.order_line_item_2 = OrderLineItem(amazon_fresh_order_id=amazon_fresh_order_id_1,
                                             item_id=self.item_2.item_id,
                                             unit_price_cents=200,
                                             quantity=3)

        self.order_line_item_3 = OrderLineItem(amazon_fresh_order_id=amazon_fresh_order_id_2,
                                             item_id=self.item_2.item_id,
                                             unit_price_cents=100,
                                             quantity=1)

        self.order_line_item_4 = OrderLineItem(amazon_fresh_order_id=amazon_fresh_order_id_3,
                                             item_id=self.item_2.item_id,
                                             unit_price_cents=50,
                                             quantity=1)

        db.session.add(self.order_line_item_1)
        db.session.add(self.order_line_item_2)
        db.session.add(self.order_line_item_3)
        db.session.add(self.order_line_item_4)

        db.session.flush()

    def tearDown(self):
        db.session.remove() # db.session.rollback() will work as well.

    def test_order_methods(self):
        """Test of the following Order object methods:
           calc_order_total
           calc_order_quantity
           get_num_line_items"""

        order = Order.query.filter_by(amazon_fresh_order_id="test1").one()

        self.assertEqual(order.calc_order_total(), 800)
        self.assertEqual(order.calc_order_quantity(), 5)
        self.assertEqual(order.get_num_line_items(), 2)


    def test_item_methods(self):
        """Test of the following Item object methods:
           get_last_order_date
           get_last_price
           get_deliv_dates
           calc_days_btw"""

        item = Item.query.filter_by(description="Test item 2").one()
        date_string_1 = "16 November 2014"
        delivery_date_1 = datetime.strptime(date_string_1, "%d %B %Y")
        date_string_2 = "13 February 2015"
        delivery_date_2 = datetime.strptime(date_string_2, "%d %B %Y")
        date_string_3 = "13 May 2015"
        delivery_date_3 = datetime.strptime(date_string_3, "%d %B %Y")
        days_btw = array([(delivery_date_2 - delivery_date_1).days, (delivery_date_3 - delivery_date_2).days])

        self.assertEqual(item.get_last_order_date(), delivery_date_3)
        self.assertEqual(item.get_last_price(), 50)
        self.assertEqual(sorted(item.get_deliv_dates()), [delivery_date_1, delivery_date_2, delivery_date_3])
        self.assertEqual(item.calc_days_btw(), (mean(days_btw, axis=0).item(), std(days_btw, axis=0).item()))


    def test_user_methods(self):
        """Test of the following User object methods:
           get_items
           get_first_deliv_date
           get_last_deliv_date
           implement_hist_cutoff
           calc_cart_qty
           get_min_day_btw
           calc_cart_date
           calc_cutoff
           predict_cart"""

        user = User.query.filter_by(user_gmail="test1@gmail.com").one()
        item1 = Item.query.filter_by(description="Test item 1").one()
        item2 = Item.query.filter_by(description="Test item 2").one()
        date_string_1 = "16 November 2014"
        delivery_date_1 = datetime.strptime(date_string_1, "%d %B %Y")
        date_string_2 = "13 February 2015"
        delivery_date_2 = datetime.strptime(date_string_2, "%d %B %Y")
        date_string_3 = "13 May 2015"
        delivery_date_3 = datetime.strptime(date_string_3, "%d %B %Y")
        items_order_1 = OrderLineItem.query.filter_by(amazon_fresh_order_id="test1").all()
        items_order_2 = OrderLineItem.query.filter_by(amazon_fresh_order_id="test2").all()
        items_order_3 = OrderLineItem.query.filter_by(amazon_fresh_order_id="test3").all()
        quant_arr = array([len(items_order_1), len(items_order_2), len(items_order_3)])
        mean_qty = mean(quant_arr, axis=0)
        std_qty = std(quant_arr, axis=0)
        filtered_quants_arr = quant_arr[abs(quant_arr - mean(quant_arr)) < 2 * std(quant_arr)]
        cart_date = datetime.strptime("05/20/2015", "%m/%d/%Y")

        self.assertEquals(sorted(user.get_items()), sorted(set([item1, item2])))
        self.assertEquals(user.get_first_deliv_date(), delivery_date_1)
        self.assertEquals(user.get_last_deliv_date(), delivery_date_3)
        self.assertEquals(user.implement_hist_cutoff(), False)
        self.assertEquals(user.calc_cart_qty(), int(mean(filtered_quants_arr, axis=0).item()))
        self.assertEquals(user.get_min_day_btw(), (delivery_date_2 - delivery_date_1).days)
        self.assertEquals(user.calc_cart_date("05/20/2015"), datetime.strptime("05/20/2015", "%m/%d/%Y"))
        self.assertEquals(user.calc_cart_date("05/20/2016"), datetime.strptime("05/13/2015", "%m/%d/%Y") + (delivery_date_2 - delivery_date_1))
        self.assertEquals(user.calc_cutoff("5/20/2015"), (80 * (cart_date - delivery_date_3).days)/100)
        self.assertEquals(user.predict_cart("5/20/2015"), ([item2], int(mean(filtered_quants_arr, axis=0).item())))

if __name__ == "__main__":
    connect_to_db(app, db, "freshstats.db")
    unittest.main()
