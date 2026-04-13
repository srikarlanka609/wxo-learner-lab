import re
from typing import Optional, Tuple
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.agent_builder.tools.types import (
    PythonToolKind,
    PluginContext,
    AgentPreInvokePayload,
    AgentPreInvokeResult,
    AgentPostInvokePayload,
    AgentPostInvokeResult,
    TextContent,
    Message
)


def detect_complete_credit_card(text: str) -> Tuple[bool, Optional[str]]:
    """
    Detects if the text contains a complete credit card number (13-19 digits).
    
    Args:
        text (str): The input text to check
    
    Returns:
        Tuple[bool, Optional[str]]: (has_complete_cc, detected_cc_format)
    """
    if not text:
        return False, None
    
    # Pattern to match credit card numbers in various formats
    cc_patterns = [
        # Format: 1234-5678-9012-3456 (with hyphens)
        r'\b(\d{4})-(\d{4})-(\d{4})-(\d{4})\b',
        # Format: 1234 5678 9012 3456 (with spaces)
        r'\b(\d{4})\s(\d{4})\s(\d{4})\s(\d{4})\b',
        # Format: 1234567890123456 (no separators, 13-19 digits)
        r'\b(\d{13,19})\b'
    ]
    
    for pattern in cc_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            full_match = match.group(0)
            # Extract only digits from the match
            digits_only = re.sub(r'\D', '', full_match)
            
            # Check if it's a valid credit card length (13-19 digits)
            if 13 <= len(digits_only) <= 19:
                return True, full_match
    
    return False, None


def mask_credit_card(text: str, mask_char: str = '*') -> str:
    """
    Finds and masks all credit card numbers in the given text.
    Keeps only the last 4 digits visible.
    
    Args:
        text (str): The input text containing potential credit card numbers
        mask_char (str): Character to use for masking (default: '*')
    
    Returns:
        str: Text with credit card numbers masked
    """
    if not text:
        return text
    
    # Pattern to match credit card numbers in various formats
    # Matches 13-19 digit numbers with optional spaces or hyphens
    # Common formats: 1234-5678-9012-3456, 1234 5678 9012 3456, 1234567890123456
    cc_patterns = [
        # Format: 1234-5678-9012-3456 (with hyphens)
        r'\b(\d{4})-(\d{4})-(\d{4})-(\d{4})\b',
        # Format: 1234 5678 9012 3456 (with spaces)
        r'\b(\d{4})\s(\d{4})\s(\d{4})\s(\d{4})\b',
        # Format: 1234567890123456 (no separators, 16 digits)
        r'\b(\d{13,19})\b'
    ]
    
    masked_text = text
    
    for pattern in cc_patterns:
        def mask_match(match):
            """Mask the credit card number, keeping last 4 digits"""
            full_match = match.group(0)
            
            # Extract only digits from the match
            digits_only = re.sub(r'\D', '', full_match)
            
            # Only process if it looks like a valid credit card (13-19 digits)
            if len(digits_only) < 13 or len(digits_only) > 19:
                return full_match
            
            # Keep last 4 digits, mask the rest
            last_four = digits_only[-4:]
            masked_digits = mask_char * (len(digits_only) - 4) + last_four
            
            # Preserve the original format (hyphens or spaces)
            if '-' in full_match:
                # Format with hyphens: ****-****-****-1234
                return f"{mask_char*4}-{mask_char*4}-{mask_char*4}-{last_four}"
            elif ' ' in full_match:
                # Format with spaces: **** **** **** 1234
                return f"{mask_char*4} {mask_char*4} {mask_char*4} {last_four}"
            else:
                # No separator format: ************1234
                return masked_digits
        
        masked_text = re.sub(pattern, mask_match, masked_text)
    
    return masked_text


@tool(description="Credit card security pre-invoke plugin - rejects complete credit card numbers",
      kind=PythonToolKind.AGENTPREINVOKE)
def credit_card_masking_pre_invoke(
    plugin_context: PluginContext,
    agent_pre_invoke_payload: AgentPreInvokePayload
) -> AgentPreInvokeResult:
    """
    Pre-invoke plugin that detects and rejects complete credit card numbers.
    If a complete credit card is detected, the request is blocked and a security
    message is returned. The credit card number is NOT sent to the LLM.
    
    Detects various credit card formats:
    - 1234-5678-9012-3456
    - 1234 5678 9012 3456
    - 1234567890123456
    
    Security behavior:
    - If complete CC detected: Stops processing, returns security warning
    - If only last 4 digits: Allows processing normally
    """
    result = AgentPreInvokeResult()
    
    # Validate payload
    if (agent_pre_invoke_payload is None or
        agent_pre_invoke_payload.messages is None or
        len(agent_pre_invoke_payload.messages) == 0):
        result.continue_processing = False
        return result
    
    # Check all messages for complete credit card numbers
    for msg in agent_pre_invoke_payload.messages:
        content = getattr(msg, "content", None)
        
        if content is None or not hasattr(content, "text") or content.text is None:
            continue
        
        # Detect if there's a complete credit card number
        has_complete_cc, detected_cc = detect_complete_credit_card(content.text)
        
        if has_complete_cc:
            # SECURITY: Block the request - credit card number is NOT sent to the LLM
            # Replace the user's message with a security warning
            security_message = (
                "⚠️ SECURITY WARNING: Entering complete credit card information is unsafe. "
                "For your security, please only provide the last 4 digits of your credit card "
                "along with your name. Complete credit card numbers cannot be processed through this system."
            )
            
            # Modify the payload to replace user message with security warning
            modified_payload = agent_pre_invoke_payload.copy(deep=True)
            
            # Replace the message content with the security warning
            for i, msg in enumerate(modified_payload.messages):
                msg_content = getattr(msg, "content", None)
                if msg_content and hasattr(msg_content, "text") and msg_content.text:
                    # Replace with security warning - credit card is NOT sent to LLM
                    new_content = TextContent(type="text", text=security_message)
                    modified_payload.messages[i] = Message(role=msg.role, content=new_content)
            
            # Stop processing - return modified payload with warning
            result.continue_processing = False
            result.modified_payload = modified_payload
            
            return result
    
    # No complete credit cards detected - allow normal processing
    result.continue_processing = True
    result.modified_payload = agent_pre_invoke_payload
    
    return result


@tool(description="Credit card masking post-invoke plugin - masks credit cards in agent responses", 
      kind=PythonToolKind.AGENTPOSTINVOKE)
def credit_card_masking_post_invoke(
    plugin_context: PluginContext, 
    agent_post_invoke_payload: AgentPostInvokePayload
) -> AgentPostInvokeResult:
    """
    Post-invoke plugin that masks credit card numbers in agent responses.
    Masks all but the last 4 digits of any credit card number found.
    
    Supports various credit card formats:
    - 1234-5678-9012-3456
    - 1234 5678 9012 3456
    - 1234567890123456
    """
    result = AgentPostInvokeResult()
    
    # Validate payload
    if (agent_post_invoke_payload is None or 
        agent_post_invoke_payload.messages is None or 
        len(agent_post_invoke_payload.messages) == 0):
        result.continue_processing = False
        return result
    
    # Process each message in the payload
    modified_payload = agent_post_invoke_payload.copy(deep=True)
    
    for i, msg in enumerate(modified_payload.messages):
        content = getattr(msg, "content", None)
        
        if content is None or not hasattr(content, "text") or content.text is None:
            continue
        
        # Mask credit card numbers in the message text
        masked_text = mask_credit_card(content.text)
        
        # Create new content with masked text
        new_content = TextContent(type="text", text=masked_text)
        modified_payload.messages[i] = Message(role=msg.role, content=new_content)
    
    result.continue_processing = True
    result.modified_payload = modified_payload
    
    return result



# orchestrate tools import -k python -f "tools/credit_card_masking_plugin.py" -r "tools/requirements.txt"
