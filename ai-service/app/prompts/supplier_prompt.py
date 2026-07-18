from typing import Optional
from app.prompts.system_prompt import build_system_prompt

def build_supplier_prompt(
    supplier_name: Optional[str], 
    ingredient: str, 
    required_quantity: str, 
    required_date: str, 
    context: str,
    restaurant_name: Optional[str] = "KitchenSync Bistro",
    contact_person: Optional[str] = "Kitchen Manager",
    supplier_email: Optional[str] = None,
    supplier_phone: Optional[str] = None,
    urgency_level: Optional[str] = "Normal",
    language_preference: Optional[str] = "English"
) -> str:
    """
    Constructs the prompt for drafting supplier purchase request messages.
    """
    system_rules = build_system_prompt()
    supplier_display = supplier_name if supplier_name else "Dear Supplier"
    
    prompt = (
        f"{system_rules}\n\n"
        "=== SUPPLIER ORDER COMMUNICATION RULES ===\n"
        "1. Draft a highly professional, polite, clear, and concise purchase request message to replenish stock.\n"
        "2. Query and cross-reference supplier names and details ONLY from the retrieved knowledge context provided below if available.\n"
        "3. Incorporate the sender's restaurant name, contact person name, supplier contact email/phone, and urgency level if provided.\n"
        "4. Output the message draft in the requested language (English, Telugu, or Roman Telugu/Tenglish).\n"
        "5. The message should contain a clear signature using the restaurant name and contact person. Do NOT hardcode generic 'Kitchen Manager' if a custom restaurant name or contact person is passed.\n"
        "6. Return the response strictly in a structured JSON format containing these keys:\n"
        "   - 'supplier_name' (str, the name of the supplier)\n"
        "   - 'ingredient' (str, matching the input ingredient name(s) exactly)\n"
        "   - 'message' (str, the drafted request message. Ensure it uses standard newlines. Do NOT invent prices or details outside the inputs)\n"
        "   - 'language' (str, the language utilized: 'English', 'Telugu', or 'Tenglish')\n"
        "7. Output ONLY a valid JSON object starting with { and ending with }. Do NOT include any markdown formatting wrappers like ```json or any other text before/after the JSON.\n\n"
        
        "=== RETRIEVED SUPPLIERS KNOWLEDGE ===\n"
        f"{context}\n\n"
        
        "=== REPLENISHMENT REQUIREMENTS ===\n"
        f"- Supplier Name: {supplier_display}\n"
        f"- Supplier Email: {supplier_email if supplier_email else 'N/A'}\n"
        f"- Supplier Phone: {supplier_phone if supplier_phone else 'N/A'}\n"
        f"- Restaurant Name: {restaurant_name}\n"
        f"- Contact/Sender: {contact_person}\n"
        f"- Urgency Level: {urgency_level}\n"
        f"- Ingredient(s): {ingredient}\n"
        f"- Required Quantity: {required_quantity}\n"
        f"- Required Date: {required_date}\n"
        f"- Language Preference: {language_preference}\n\n"
        
        "Structured JSON Supplier Purchase Request:"
    )
    return prompt
