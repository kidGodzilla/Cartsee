function showVisualization() {

    $.get('/visualization', function(user_orders_json) {
      $("#display-div").append(
        "<h3>" + user_orders_json["user_gmail"] + "</h3>");
        $("#display-div").append("<ol>");
        for (var i = 0; i < user_orders_json["orders"].length; i++)  {
          $("#display-div").append(
          "<li>" + "Order # " +
          user_orders_json["orders"][i]["amazon_fresh_order_id"] +
            "<ul>" +
              "<li>" + "delivery date: " + user_orders_json["orders"][i]["delivery_date"] + "</li>" +
              "<li>" + "delivery time: " + user_orders_json["orders"][i]["delivery_time"] + "</li>" +
              "<li id='order_line_items" + i.toString() + "'>items bought <br></li>"
          + "</ul>"
        + "</li>" );
        $("#display-div").append("<ol>");

        var order_total = 0;
        for (var j = 0; j < user_orders_json["orders"][i]["order_line_items_serialized"].length; j++) {
          console.log(user_orders_json["orders"][i]["amazon_fresh_order_id"]);
          console.log("j equals " + j);
          $("#order_line_items" + i.toString()).append(
            "line item # " +
            user_orders_json["orders"][i]["order_line_items_serialized"][j]["order_line_item_id"]
            + ", unit price: " + "$" +
            user_orders_json["orders"][i]["order_line_items_serialized"][j]["unit_price"]
            + " quantity: " +
            user_orders_json["orders"][i]["order_line_items_serialized"][j]["quantity"]
            + " " +
            user_orders_json["orders"][i]["order_line_items_serialized"][j]["description"]
            + "<br>"
          );
          line_item_total = user_orders_json["orders"][i]["order_line_items_serialized"][j]["unit_price"] * user_orders_json["orders"][i]["order_line_items_serialized"][j]["quantity"]
          order_total = order_total + line_item_total;

          }

        $("#order_line_items" + i.toString()).append("order total: $" + order_total);
        $("#order_line_items" + i.toString()).append("order total: $" + order_total);
        $("#order_line_items" + i.toString()).append(user_orders_json["orders"][i]["order_total"]) 

          }



      }

    );

  }

showVisualization()
