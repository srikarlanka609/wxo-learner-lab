import sqlite3
import os
from typing import Optional, List, Dict, Any, Tuple
from ibm_watsonx_orchestrate.agent_builder.tools import tool


class CustomerDBManager:
    """Manager class for customer database operations"""
    
    def __init__(self, db_name: str = "customers.db"):
        """Initialize database connection"""
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Construct the full path to the database file
        self.db_name = os.path.join(script_dir, db_name)
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Connect to the database"""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def get_customer(self, customer_id: int) -> Optional[Tuple]:
        """
        Get a customer by ID
        
        Args:
            customer_id: ID of the customer
        
        Returns:
            Tuple containing customer data or None if not found
        """
        self.connect()
        
        self.cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
        customer = self.cursor.fetchone()
        
        self.close()
        return customer
    
    def get_all_customers(self) -> List[Tuple]:
        """
        Get all customers from the database
        
        Returns:
            List of tuples containing customer data
        """
        self.connect()
        
        self.cursor.execute("SELECT * FROM customers")
        customers = self.cursor.fetchall()
        
        self.close()
        return customers


@tool(description="Query customer information from the database by customer ID or name")
def get_customer_info(customer_id: Optional[int] = None, customer_name: Optional[str] = None) -> str:
    """
    Retrieve customer information including credit card details.
    
    Args:
        customer_id: The ID of the customer to retrieve (optional)
        customer_name: The name of the customer to search for (optional)
    
    Returns:
        A formatted string with customer information
    """
    db_manager = CustomerDBManager("customers.db")
    
    try:
        if customer_id is not None:
            # Get customer by ID
            customer = db_manager.get_customer(customer_id)
            if customer:
                return format_customer_info(customer)
            else:
                return f"No customer found with ID: {customer_id}"
        
        elif customer_name is not None:
            # Search for customer by name
            db_manager.connect()
            db_manager.cursor.execute(
                "SELECT * FROM customers WHERE customer_name LIKE ?", 
                (f"%{customer_name}%",)
            )
            customers = db_manager.cursor.fetchall()
            db_manager.close()
            
            if not customers:
                return f"No customers found matching name: {customer_name}"
            
            if len(customers) == 1:
                return format_customer_info(customers[0])
            else:
                # Multiple matches found
                result = f"Found {len(customers)} customers matching '{customer_name}':\n\n"
                for customer in customers:
                    result += format_customer_info(customer) + "\n---\n"
                return result
        
        else:
            return "Please provide either customer_id or customer_name to search."
    
    except Exception as e:
        return f"Error retrieving customer information: {str(e)}"


@tool(description="List all customers in the database")
def list_all_customers() -> str:
    """
    Retrieve a list of all customers in the database.
    
    Returns:
        A formatted string with all customer information
    """
    db_manager = CustomerDBManager("customers.db")
    
    try:
        customers = db_manager.get_all_customers()
        
        if not customers:
            return "No customers found in the database."
        
        result = f"Total customers: {len(customers)}\n\n"
        for customer in customers:
            result += format_customer_info(customer) + "\n---\n"
        
        return result
    
    except Exception as e:
        return f"Error retrieving customers: {str(e)}"


@tool(description="Get customer credit card information by customer ID")
def get_customer_credit_card(customer_id: int) -> str:
    """
    Retrieve only the credit card information for a specific customer.
    
    Args:
        customer_id: The ID of the customer
    
    Returns:
        A formatted string with credit card details
    """
    db_manager = CustomerDBManager("customers.db")
    
    try:
        customer = db_manager.get_customer(customer_id)
        
        if not customer:
            return f"No customer found with ID: {customer_id}"
        
        customer_name = customer[1]
        card_number = customer[3] if customer[3] else "No card on file"
        card_expiry = customer[4] if customer[4] else "N/A"
        
        return (f"Customer: {customer_name}\n"
                f"Credit Card Number: {card_number}\n"
                f"Expiry Date: {card_expiry}")
    
    except Exception as e:
        return f"Error retrieving credit card information: {str(e)}"


def format_customer_info(customer: tuple) -> str:
    """
    Format customer information as a readable string.
    
    Args:
        customer: Tuple containing (id, name, email, card_number, card_expiry)
    
    Returns:
        Formatted string with customer details
    """
    customer_id, name, email, card_number, card_expiry = customer
    
    card_display = card_number if card_number else "No card on file"
    expiry_display = card_expiry if card_expiry else "N/A"
    
    return (f"Customer ID: {customer_id}\n"
            f"Name: {name}\n"
            f"Email: {email}\n"
            f"Credit Card: {card_display}\n"
            f"Expiry: {expiry_display}")




# orchestrate tools import -k python \
#   -f customer_query_tool_package/customer_query_tool.py \
#   -p customer_query_tool_package
