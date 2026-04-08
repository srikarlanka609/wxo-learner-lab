import os
from typing import Optional, List, Dict

from dotenv import load_dotenv
from ibm_watsonx_orchestrate.agent_builder.tools import tool, ToolPermission
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------
# --------------------------------------- WATSONX AI --------------------------------------
# -----------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------



@tool(
    name="recommend_best_product",
    description="""
    Uses AI to recommend the single best product to purchase from a search result.
    
    This tool takes product search results and uses watsonx.ai to recommend the top choice
    with a clear explanation of why it's the best option.
    
    IMPORTANT: Use this AFTER calling search_product tool.
    Pass the 'products' list from search_product output to this tool.
    
    Args:
        products (List[Dict]): List of product dictionaries from search_product tool
        budget (Optional[str]): Maximum budget in dollars (e.g., "200", "1000")
        priority (Optional[str]): What matters most - "price", "stock", "profit", "quality", "balanced"
    
    Returns:
        dict: Single best product recommendation with explanation
    
    Example:
        search_result = search_product(by="category", key="Peripherals")
        recommendation = recommend_best_product(products=search_result['products'], budget="100", priority="price")
    """,
    permission=ToolPermission.ADMIN
)
def recommend_best_product(
    products: List[Dict],
    budget: Optional[str] = None,
    priority: Optional[str] = "balanced"
) -> dict:
    """
    Uses watsonx.ai to recommend the single best product from search results.
    
    Args:
        products (List[Dict]): List of product dictionaries
        budget (Optional[str]): Maximum budget
        priority (Optional[str]): Priority factor
    
    Returns:
        dict: {'status': 200, 'recommendation': {...}, 'explanation': '...'}
    """
    
    load_dotenv()
    
    # Get configuration
    api_key = os.getenv("API_KEY")
    watsonx_url = os.getenv("WATSONX_AI_URL")
    model_id = os.getenv("WATSONX_AI_MODEL")
    project_id = os.getenv("WATSONX_AI_PROJECT_ID")
    space_id = os.getenv("WATSONX_AI_SPACE_ID")
    
    try:
        # Validate inputs
        if not products or not isinstance(products, list) or len(products) == 0:
            return {
                "status": 400,
                "error": "Bad Request",
                "message": "products must be a non-empty list",
                "outward": "No products provided. Please search for products first using search_product tool."
            }
        
        # Validate configuration
        if not all([api_key, watsonx_url, model_id]):
            return {
                "status": 400,
                "error": "Configuration Error",
                "message": "Missing API_KEY, WATSONX_AI_URL, or WATSONX_AI_MODEL",
                "outward": "Recommendation service is not configured. Please contact support."
            }
        
        if not project_id and not space_id:
            return {
                "status": 400,
                "error": "Configuration Error",
                "message": "Missing WATSONX_AI_PROJECT_ID or WATSONX_AI_SPACE_ID",
                "outward": "Recommendation service is not configured. Please contact support."
            }
        
        # Filter by budget if provided
        original_count = len(products)
        if budget:
            try:
                budget_float = float(budget)
                products = [p for p in products if float(p.get('price', 0)) <= budget_float]
                
                if not products:
                    return {
                        "status": 404,
                        "error": "No Products in Budget",
                        "message": f"No products under ${budget}",
                        "outward": f"No products found within budget of ${budget}. Try increasing your budget."
                    }
            except (ValueError, TypeError) as e:
                return {
                    "status": 400,
                    "error": "Invalid Budget",
                    "message": f"Budget error: {str(e)}",
                    "outward": "Invalid budget value. Please provide a number."
                }
        
        # Limit to top 10 for processing
        products_to_evaluate = products[:10]
        
        # Build simple product list
        products_text = []
        for i, p in enumerate(products_to_evaluate, 1):
            try:
                profit_pct = float(p.get('profit_margin', 0)) * 100
                products_text.append(
                    f"{i}. {p.get('name')} - "
                    f"${p.get('price')} | "
                    f"Stock: {p.get('stock_qty')} | "
                    f"Profit: {profit_pct:.0f}% | "
                    f"Supplier: {p.get('supplier')}"
                )
            except Exception:
                continue
        
        if not products_text:
            return {
                "status": 400,
                "error": "Invalid Data",
                "message": "Could not parse product data",
                "outward": "Product data appears malformed. Please try searching again."
            }
        
        products_context = "\n".join(products_text)
        
        # Build priority text
        priority_map = {
            "price": "Focus on the lowest price option that still has good stock.",
            "stock": "Focus on highest stock availability to ensure reliable purchase.",
            "profit": "Focus on best profit margin while keeping price reasonable.",
            "quality": "Focus on supplier reputation and balanced metrics.",
            "balanced": "Balance all factors: price, stock, profit, and supplier."
        }
        priority_instruction = priority_map.get(priority.lower(), priority_map["balanced"])
        budget_note = f"Maximum budget: ${budget}" if budget else "No budget limit"
        
        # Simple, flexible prompt
        prompt = f"""You are a product recommendation expert. Pick the single best product from this list and explain why.

PRODUCTS:
{products_context}

INSTRUCTIONS:
- {priority_instruction}
- {budget_note}
- Consider: price value, stock availability, profit margin (20-40% is healthy), and supplier

FORMAT YOUR RESPONSE LIKE THIS:
Best Product: [Product Name]
Price: $[XX.XX]
Why: [2-3 sentences explaining why this is the best choice based on the criteria]

Now recommend the best product:"""
        
        # Initialize watsonx.ai
        try:
            credentials = Credentials(url=watsonx_url, api_key=api_key)
            
            model_params = {
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 300,
                GenParams.MIN_NEW_TOKENS: 50,
                GenParams.TEMPERATURE: 0.5,
                GenParams.STOP_SEQUENCES: ["\n\nPRODUCTS:", "FORMAT YOUR"]
            }
            
            if project_id:
                model = ModelInference(
                    model_id=model_id,
                    credentials=credentials,
                    project_id=project_id,
                    params=model_params
                )
            else:
                model = ModelInference(
                    model_id=model_id,
                    credentials=credentials,
                    space_id=space_id,
                    params=model_params
                )
        except Exception as e:
            return {
                "status": 500,
                "error": "Model Initialization Failed",
                "message": str(e),
                "outward": "Unable to connect to AI service. Please try again later."
            }
        
        # Call AI
        try:
            response = model.generate_text(prompt=prompt)
            if not response or len(response.strip()) == 0:
                return {
                    "status": 500,
                    "error": "Empty Response",
                    "message": "AI returned empty response",
                    "outward": "No recommendation generated. Please try again."
                }
        except Exception as e:
            return {
                "status": 500,
                "error": "AI Call Failed",
                "message": str(e),
                "outward": "AI recommendation failed. Please try again."
            }
        
        # Parse response (flexible, no strict JSON)
        response = response.strip()
        
        # Try to extract product name and reason
        product_name = "Unknown Product"
        price = "N/A"
        explanation = response
        
        # Simple parsing
        lines = response.split('\n')
        for line in lines:
            if line.startswith("Best Product:"):
                product_name = line.replace("Best Product:", "").strip()
            elif line.startswith("Price:"):
                price = line.replace("Price:", "").strip()
            elif line.startswith("Why:"):
                explanation = line.replace("Why:", "").strip()
        
        # Return success
        return {
            "status": 200,
            "budget": budget if budget else "No limit",
            "priority": priority,
            "total_products_found": original_count,
            "products_evaluated": len(products_to_evaluate),
            "recommendation": {
                "product_name": product_name,
                "price": price,
                "explanation": explanation
            },
            "full_response": response
        }
    
    except Exception as e:
        # Better error reporting
        import traceback
        return {
            "status": 500,
            "error": "Unexpected Error",
            "message": f"{type(e).__name__}: {str(e)}",
            "traceback": traceback.format_exc(),
            "outward": f"An error occurred: {str(e)}"
        }


# Testing
if __name__ == "__main__":
    load_dotenv()
    
    print("Testing Simplified Product Recommendation Tool")
    print("=" * 80)
    
    # Display config
    api_key = os.getenv("API_KEY")
    watsonx_url = os.getenv("WATSONX_AI_URL")
    model_id = os.getenv("WATSONX_AI_MODEL")
    project_id = os.getenv("WATSONX_AI_PROJECT_ID")
    
    print(f"URL: {watsonx_url}")
    print(f"Model: {model_id}")
    print(f"Project: {project_id or 'NOT SET'}")
    print(f"API Key: {'*' * 20 if api_key else 'NOT SET'}")
    print("=" * 80)
    
    # Mock products
    mock_products = [
        {
            "name": "TechGear Pro Mouse",
            "sku": "TGM-MSE-001",
            "price": "49.99",
            "stock_qty": "145",
            "profit_margin": "0.35",
            "supplier": "Williams Ltd"
        },
        {
            "name": "TypeMaster Keyboard",
            "sku": "TYPE-KEY-010",
            "price": "149.99",
            "stock_qty": "78",
            "profit_margin": "0.36",
            "supplier": "Hoffman and Sons"
        },
        {
            "name": "MechType RGB Keyboard",
            "sku": "MECH-KEY-018",
            "price": "89.99",
            "stock_qty": "92",
            "profit_margin": "0.37",
            "supplier": "Johnson Ramos"
        },
        {
            "name": "PrecisionClick Gaming Mouse",
            "sku": "PREC-MSE-020",
            "price": "39.99",
            "stock_qty": "285",
            "profit_margin": "0.48",
            "supplier": "Fowler Rosario"
        }
    ]
    
    # Test cases
    tests = [
        {"name": "Budget Price Focus", "products": mock_products, "budget": "100", "priority": "price"},
        {"name": "No Budget Balanced", "products": mock_products, "budget": None, "priority": "balanced"},
        {"name": "Profit Focus", "products": mock_products, "budget": "200", "priority": "profit"}
    ]
    
    for i, test in enumerate(tests, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}: {test['name']}")
        print(f"Budget: ${test['budget']}" if test['budget'] else "Budget: No limit")
        print(f"Priority: {test['priority']}")
        print("-" * 80)
        
        result = recommend_best_product(
            products=test['products'],
            budget=test['budget'],
            priority=test['priority']
        )
        
        if result["status"] == 200:
            print(f"✅ Status: {result['status']}")
            print(f"\n🏆 RECOMMENDATION:")
            print(f"   Product: {result['recommendation']['product_name']}")
            print(f"   Price: {result['recommendation']['price']}")
            print(f"\n💡 Why: {result['recommendation']['explanation']}")
            print(f"\nProducts Evaluated: {result['products_evaluated']} of {result['total_products_found']}")
        else:
            print(f"❌ Status: {result['status']}")
            print(f"Error: {result.get('error')}")
            print(f"Message: {result.get('message')}")
            if 'traceback' in result:
                print(f"\nTraceback:\n{result['traceback']}")
        
        print("=" * 80)


# orchestrate tools import -f tools/watsonx_ai_call.py -k python
