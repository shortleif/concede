from markupsafe import Markup


def convert_to_gold(copper_value):
    """Converts a copper value into a formatted gold, silver, and copper string.

    Args:
        copper_value: The price in copper.

    Returns:
        A formatted string representing the price in gold, silver, and copper (e.g., "22g 0s 99c").
    """
    silver_value = copper_value // 100
    gold_value = silver_value // 100
    silver_remainder = silver_value % 100  # Calculate the remaining silver
    copper_remainder = copper_value % 100

    price_string = (f"<span class='gold'>{gold_value}g</span><span class='silver'>"
                    f"{silver_remainder}s</span><span class='copper'>{copper_remainder}c</span>")
    return Markup(price_string)


def format_price(total_cost_copper):
    return convert_to_gold(total_cost_copper)