from fastmcp import FastMCP
from PIL import Image
import random
import io
import base64
from typing import Optional

# Initialize FastMCP server
mcp = FastMCP("Image and Number Tools Server")

@mcp.tool()
def rotate_image(
    image_base64: str,
    angle: float,
    expand: bool = True
) -> dict:
    """
    Rotate an image by a specified angle.
    
    Args:
        image_base64: Base64 encoded image string
        angle: Rotation angle in degrees (positive = counter-clockwise)
        expand: If True, expand output image to fit the entire rotated image
    
    Returns:
        dict: Contains rotated image as base64 string and metadata
    
    Example:
        rotate_image(image_base64="iVBORw0KGgo...", angle=90, expand=True)
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(image_base64)
        image = Image.open(io.BytesIO(image_data))
        
        # Get original size
        original_size = image.size
        original_format = image.format or 'PNG'
        
        # Rotate the image
        rotated_image = image.rotate(angle, expand=expand, fillcolor='white')
        
        # Get new size
        new_size = rotated_image.size
        
        # Convert back to base64
        output_buffer = io.BytesIO()
        rotated_image.save(output_buffer, format=original_format)
        output_buffer.seek(0)
        rotated_base64 = base64.b64encode(output_buffer.read()).decode('utf-8')
        
        return {
            "status": "success",
            "rotated_image_base64": rotated_base64,
            "original_size": original_size,
            "new_size": new_size,
            "rotation_angle": angle,
            "format": original_format
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to rotate image"
        }


@mcp.tool()
def random_number_in_range(
    min_value: int,
    max_value: int,
    count: Optional[int] = 1
) -> dict:
    """
    Generate random number(s) within a specified range.
    
    Args:
        min_value: Minimum value (inclusive)
        max_value: Maximum value (inclusive)
        count: Number of random numbers to generate (default: 1)
    
    Returns:
        dict: Contains the random number(s) and range information
    
    Example:
        random_number_in_range(min_value=1, max_value=100, count=1)
        random_number_in_range(min_value=50, max_value=200, count=5)
    """
    try:
        # Validate inputs
        if min_value > max_value:
            return {
                "status": "error",
                "error": "Invalid range",
                "message": f"min_value ({min_value}) cannot be greater than max_value ({max_value})"
            }
        
        if count < 1:
            return {
                "status": "error",
                "error": "Invalid count",
                "message": "count must be at least 1"
            }
        
        if count > 1000:
            return {
                "status": "error",
                "error": "Invalid count",
                "message": "count cannot exceed 1000"
            }
        
        # Generate random number(s)
        if count == 1:
            random_numbers = random.randint(min_value, max_value)
        else:
            random_numbers = [random.randint(min_value, max_value) for _ in range(count)]
        
        return {
            "status": "success",
            "random_number": random_numbers if count == 1 else None,
            "random_numbers": random_numbers if count > 1 else None,
            "count": count,
            "range": {
                "min": min_value,
                "max": max_value
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": "Failed to generate random number"
        }


# Optional: Add a simple health check
@mcp.tool()
def health_check() -> dict:
    """
    Check if the MCP server is running properly.
    
    Returns:
        dict: Server status information
    """
    return {
        "status": "healthy",
        "server": "Image and Number Tools MCP Server",
        "available_tools": [
            "rotate_image",
            "random_number_in_range",
            "health_check"
        ]
    }


# Run the server
if __name__ == "__main__":
    mcp.run()

# Import the toolkit
# orchestrate toolkits add \
#     --kind mcp \
#     --name mcp_test \
#     --description "Test two mcp tools" \
#     --package-root ./api \
#     --command "python main.py" \
#     --tools "*" \
