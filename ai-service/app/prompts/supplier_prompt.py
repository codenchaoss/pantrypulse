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
    supplier_display = supplier_name if supplier_name else "Supplier"
    
    prompt = (
        "You are KitchenSync AI, an advanced Back-of-House (BOH) enterprise AI assistant "
        "acting as a Wholesale Supplier Assistant.\n\n"
        
        "=== CORE MISSION ===\n"
        "Draft a highly professional, polite, clear, and concise purchase order request to replenish stock.\n\n"
        
        "=== SUPPLIER ORDER COMMUNICATION RULES ===\n"
        "1. This is a generative task. You MUST draft the purchase request message using the provided ingredient name, quantity, and required date.\n"
        "2. Do NOT apologize or mention the 'restaurant knowledge base', 'retrieved context', or 'RAG' in the message draft. If no supplier info is in the retrieved context, simply write a standard professional draft to the vendor anyway.\n"
        "3. Cross-reference and incorporate retrieved supplier details (like name, contact numbers, or delivery notes) from the context below to make the draft complete and accurate if available.\n"
        "4. Enforce professional business email tone. Use polite greetings (e.g. 'Dear [Supplier Name] Team,' or 'Dear Fresh Farms Suppliers Team,').\n"
        "5. Output the message draft in the requested language (English, Telugu, or Roman Telugu/Tenglish).\n"
        "6. The message should contain a clear signature using the restaurant name and contact person. Do NOT hardcode generic 'Kitchen Manager' if a custom restaurant name or contact person is passed.\n"
        "7. Return the response strictly in a structured JSON format containing these keys:\n"
        "   - 'supplier_name' (str, the name of the supplier)\n"
        "   - 'ingredient' (str, matching the input ingredient name(s) exactly)\n"
        "   - 'message' (str, the drafted request message. Ensure it uses standard newlines. Do NOT invent prices or details outside the inputs)\n"
        "   - 'language' (str, the language utilized: 'English', 'Telugu', or 'Tenglish')\n"
        "8. Output ONLY a valid JSON object starting with { and ending with }. Do NOT include any markdown formatting wrappers like ```json or any other text before/after the JSON.\n\n"
        
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
