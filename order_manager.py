"""
Order Manager - Manages order state and extraction
Interview Learning: How to parse natural language into structured data
"""

from pydantic import BaseModel
from typing import List, Optional
import re

class Pizza(BaseModel):
    """Using Pydantic for data validation - Interview best practice"""
    size: Optional[str] = None
    crust: Optional[str] = None
    toppings: List[str] = []
    quantity: int = 1

class Order(BaseModel):
    pizzas: List[Pizza] = []
    drinks: List[str] = []
    sides: List[str] = []
    desserts: List[str] = []
    delivery_address: Optional[str] = None

class OrderManager:
    def __init__(self):
        """Initialize order tracking"""
        self.order = Order()
        self.valid_sizes = ["small", "medium", "large", "extra large"]
        self.valid_crusts = ["thin", "regular", "thick", "stuffed"]
        self.valid_toppings = [
            "pepperoni", "mushroom", "onion", "sausage", "bacon",
            "cheese", "olives", "bell pepper", "pineapple", "spinach"
        ]
    
    def extract_from_message(self, message: str) -> None:
        """
        Extract pizza order details from user message.
        
        Interview Learning: NLP parsing, regex, string matching techniques
        Real production systems would use NER (Named Entity Recognition)
        """
        message_lower = message.lower()
        
        # Extract size
        for size in self.valid_sizes:
            if size in message_lower:
                if not self.order.pizzas:
                    self.order.pizzas.append(Pizza())
                self.order.pizzas[-1].size = size
        
        # Extract crust type
        for crust in self.valid_crusts:
            if crust in message_lower:
                if not self.order.pizzas:
                    self.order.pizzas.append(Pizza())
                self.order.pizzas[-1].crust = crust
        
        # Extract toppings
        for topping in self.valid_toppings:
            if topping in message_lower:
                if not self.order.pizzas:
                    self.order.pizzas.append(Pizza())
                if topping not in self.order.pizzas[-1].toppings:
                    self.order.pizzas[-1].toppings.append(topping)
        
        # Extract drinks
        drinks_keywords = ["coke", "sprite", "water", "coffee", "tea"]
        for drink in drinks_keywords:
            if drink in message_lower and drink not in self.order.drinks:
                self.order.drinks.append(drink)
        
        # Extract sides
        sides_keywords = ["garlic bread", "wings", "salad", "fries"]
        for side in sides_keywords:
            if side in message_lower and side not in self.order.sides:
                self.order.sides.append(side)
    
    def has_required_items(self) -> bool:
        """
        Interview Learning: Validation logic - what makes an order valid?
        This is a business rule that should be documented.
        """
        return (
            len(self.order.pizzas) > 0 and
            all(pizza.size and pizza.crust for pizza in self.order.pizzas) and
            self.order.delivery_address is not None
        )
    
    def get_summary(self) -> str:
        """Generate human-readable order summary for SMS"""
        summary = "🍕 ORDER CONFIRMATION\n"
        summary += "=" * 30 + "\n"
        
        for i, pizza in enumerate(self.order.pizzas, 1):
            summary += f"Pizza {i}: {pizza.size.upper()} {pizza.crust.upper()}\n"
            if pizza.toppings:
                summary += f"  Toppings: {', '.join(pizza.toppings)}\n"
        
        if self.order.drinks:
            summary += f"Drinks: {', '.join(self.order.drinks)}\n"
        
        if self.order.sides:
            summary += f"Sides: {', '.join(self.order.sides)}\n"
        
        summary += "=" * 30 + "\n"
        summary += "Thanks for your order! Delivery in 30-45 mins."
        
        return summary
