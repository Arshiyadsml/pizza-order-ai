# 🎓 Interview Learning Guide

This document breaks down key concepts and interview questions for each component.

## 1. Conversation Management (conversation_engine.py)

### Key Concept: Conversation History
```python
self.conversation_history = [
    {"role": "user", "content": "I want a large pizza"},
    {"role": "assistant", "content": "Great! What toppings..."},
    {"role": "user", "content": "pepperoni and mushroom"}
]
```

**Why?** LLMs are stateless - they have no memory of previous messages. We must send the entire history.

### Interview Questions:

**Q1: Why send full conversation history instead of just the last message?**
- A: Because GPT needs context. It doesn't remember previous turns. Without history, it won't know what "it" refers to.
- Follow-up: What's the tradeoff? (Cost - more tokens = more expensive)

**Q2: What happens if conversation gets very long?**
- A: Token limit is hit. GPT-3.5 has 4K tokens, GPT-4 has 8K-32K
- Solution: Implement conversation summarization or pruning old messages
- Code hint: Keep only recent N messages

**Q3: Why use temperature=0.7?**
- A: Temperature controls randomness (0=deterministic, 1=creative)
- For ordering: We want some personality (0.7) but not too creative (avoid weird suggestions)
- Interview tip: Explain the tradeoff for your use case

**Q4: How would you handle API rate limits?**
- A: Implement exponential backoff, queuing, or use Twilio/external queue

---

## 2. Order Extraction (order_manager.py)

### Key Concept: NLP Parsing

This is a simplified version of what real systems do:
- **Real world**: Use spacy, transformers, or OpenAI function calling
- **This version**: Simple string matching in a list

### Interview Questions:

**Q1: Why not just ask GPT to extract order data?**
- A: We do! But we also extract ourselves for redundancy
- Real approach: Use OpenAI function calling (structured outputs)
- Benefit: Guaranteed JSON format, reliable parsing

**Q2: What's wrong with current extraction?**
- A: 
  - Case sensitive issues (pepperoni vs Pepperoni)
  - Doesn't handle "no mushrooms" (negation)
  - Can't handle custom toppings not in list
  - No quantity parsing (2 large pizzas)
- Fix: Use regex, NER models, or ask user to confirm

**Q3: How would you improve accuracy?**
- A1: Use OpenAI function calling:
  ```python
  functions=[{
      "name": "extract_order",
      "parameters": {
          "type": "object",
          "properties": {
              "size": {"type": "string"},
              "toppings": {"type": "array"}
          }
      }
  }]
  ```
- A2: Implement confirmation step: "You want large pepperoni, right?"

**Q4: How would you handle ambiguity?**
- A: Always ask for confirmation when unsure

---

## 3. Third-Party Integration (sms_service.py)

### Key Concept: Graceful Failure

```python
try:
    response = self.client.messages.create(...)
    return True
except Exception as e:
    logger.error(...)
    return False
```

### Interview Questions:

**Q1: What if Twilio API is down?**
- A: Order still created, SMS fails, but system continues
- Better: Implement retry logic with exponential backoff
- Best: Use a message queue (Redis, RabbitMQ) to retry later

**Q2: How would you add retry logic?**
```python
import time
def send_with_retry(self, phone, message, max_retries=3):
    for attempt in range(max_retries):
        try:
            return self.send_confirmation(phone, message)
        except Exception as e:
            wait_time = 2 ** attempt  # exponential backoff
            time.sleep(wait_time)
    logger.error("Failed after retries")
    return False
```

**Q3: What happens if customer phone number is invalid?**
- A: Twilio validates, but we should too
- Use regex: `^\+?1?\d{9,15}$`

**Q4: How do you handle PII (personally identifiable info)?**
- A: 
  - Don't log full phone numbers
  - Mask in logs: +1***5678
  - Use encryption for storage
  - GDPR/CCPA compliance

---

## 4. System Design Questions

### Q: How would you handle 1000 concurrent orders?

**Current problems:**
- Single process, blocking I/O
- No database
- No order persistence

**Solution architecture:**
```
Load Balancer
    ↓
[API Server] ←→ Redis (session store)
    ↓
[Order Queue] (RabbitMQ/Kafka)
    ↓
[Worker Pool] (process orders async)
    ↓
[Database] (PostgreSQL)
    ↓
[SMS Queue] (send async)
```

**Code changes needed:**
1. Make conversation_engine async
2. Store session in Redis
3. Add background job workers
4. Implement database ORM (SQLAlchemy)

### Q: How would you prevent duplicate orders?

**Solution:** Idempotency key
```python
order_id = hashlib.md5(f"{phone}_{timestamp}".encode()).hexdigest()
# Check if order_id exists in DB before creating
```

### Q: How would you track order status?

**Solution:** Add status field
```python
class Order:
    status: str  # "pending" → "confirmed" → "preparing" → "out_for_delivery" → "delivered"
    timestamps: dict  # track when each status changed
```

### Q: How would you implement user authentication?

**Solution:**
1. Phone number verification (send code via SMS)
2. JWT tokens for API
3. Store order history per user

### Q: How would you monitor this in production?

**Solution:**
1. Logging: Track all conversations
2. Metrics: Success rate, avg response time, cost
3. Alerts: API down, high error rate
4. Dashboards: Order volume, revenue

---

## 5. Interview Cheat Sheet

### When asked "Design a pizza ordering system":

**Step 1: Clarify Requirements**
- How many orders/second?
- Real-time vs batch?
- Geographic regions?
- Languages supported?

**Step 2: Propose Architecture**
- Frontend (web/app/WhatsApp)
- API Gateway
- Conversation Service
- Order Service
- Payment Service
- Notification Service

**Step 3: Discuss Tradeoffs**
- Consistency vs Availability (CAP theorem)
- Monolith vs Microservices
- SQL vs NoSQL

**Step 4: Address Scale**
- Database indexing
- Caching strategy (Redis)
- Load balancing
- Async processing

**Step 5: Production Concerns**
- Error handling
- Monitoring & logging
- Security (PII, encryption)
- Compliance (GDPR, PCI-DSS)

---

## 6. Real-World Improvements

### Use OpenAI Function Calling (Better!)

Instead of manual extraction:
```python
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[...],
    functions=[{
        "name": "create_order",
        "parameters": {
            "type": "object",
            "properties": {
                "size": {"enum": ["small", "medium", "large"]},
                "toppings": {"type": "array", "items": {"type": "string"}},
                "quantity": {"type": "integer"}
            },
            "required": ["size", "quantity"]
        }
    }]
)
```

### Add Multi-Language Support

```python
system_prompt = self._build_system_prompt(language="es")  # Spanish
```

### Implement Persistent Sessions

```python
# Store in Redis
redis.set(f"order:{user_phone}", json.dumps(order_state), ex=3600)
order_state = redis.get(f"order:{user_phone}")
```

### Add Payment Processing

```python
from stripe import Stripe
stripe.Charge.create(amount=total_cents, currency="usd", token=token)
```

---

## 7. Books & Resources for Deeper Learning

- **System Design**: "Designing Data-Intensive Applications" by Martin Kleppmann
- **LLMs**: "Build a Large Language Model (From Scratch)" by Sebastian Raschka
- **APIs**: "Designing Web APIs" by Brenda Jin
- **Code Quality**: "Clean Code" by Robert C. Martin

---

Good luck with your interviews! 🚀