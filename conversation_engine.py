"""
Conversation Engine for Pizza Ordering AI
Key Learning: How to maintain conversation state with LLMs
"""

from openai import OpenAI
from order_manager import OrderManager
from sms_service import SMSService
import json

class PizzaOrderingAssistant:
    def __init__(self, openai_api_key: str, twilio_account_sid: str, 
                 twilio_auth_token: str, twilio_phone: str):
        """
        Initialize the pizza ordering assistant.
        
        Interview Note: Explain constructor pattern and dependency injection
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.order_manager = OrderManager()
        self.sms_service = SMSService(twilio_account_sid, twilio_auth_token, twilio_phone)
        
        # Conversation history for context management
        # Interview Note: Why do we need this? LLMs have no memory of past messages
        self.conversation_history = []
        
        self.model = "gpt-3.5-turbo"
        self.system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """
        Build the system prompt that defines the AI's behavior.
        
        Interview Learning: Good prompts are crucial for LLM performance.
        Key elements: Role, Task, Constraints, Format
        """
        return """
You are a friendly pizza shop employee taking orders over text. Your job is to:

1. GREET the customer warmly
2. ASK about their preferred:
   - Pizza size (Small, Medium, Large, Extra Large)
   - Crust type (Thin, Regular, Thick, Stuffed)
   - Toppings (list 3-4 popular options, allow custom)
   - Quantity of pizzas
3. UPSELL items:
   - Drinks (Coke, Sprite, Water, etc.)
   - Sides (Garlic Bread, Wings, Salad)
   - Dessert (Brownies, Cookie)
4. CONFIRM the complete order with total items
5. ASK for delivery address confirmation

Be conversational, friendly, and natural. Don't be robotic.
When you have all information, say "READY_TO_CONFIRM" at the end of your message."""
    
    def process_message(self, user_message: str) -> str:
        """
        Process user message and generate AI response.
        
        Interview Learning: This is a classic multi-turn conversation pattern.
        Key concept: Maintain history to provide context to the LLM.
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Extract order details from the conversation
        # Interview Note: This is order extraction - a key NLP task
        self.order_manager.extract_from_message(user_message)
        
        # Call OpenAI API with full conversation history
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_prompt},
                *self.conversation_history
            ],
            temperature=0.7,  # Interview Q: Why 0.7 and not 0 or 1? Explain creativity vs accuracy tradeoff
            max_tokens=150
        )
        
        assistant_message = response.choices[0].message.content
        
        # Add assistant response to history
        self.conversation_history.append({
            "role": "assistant",
            "content": assistant_message
        })
        
        return assistant_message
    
    def is_order_complete(self) -> bool:
        """
        Check if we have enough information to complete the order.
        
        Interview Learning: State validation is critical in production systems.
        """
        return self.order_manager.has_required_items()
    
    def send_sms_confirmation(self, phone_number: str) -> bool:
        """
        Send order confirmation via SMS.
        
        Interview Note: Always handle third-party API failures gracefully.
        """
        order_summary = self.order_manager.get_summary()
        return self.sms_service.send_confirmation(phone_number, order_summary)