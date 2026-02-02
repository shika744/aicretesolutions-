#!/usr/bin/env python3
"""
Simple script to create a logo placeholder for AIcrete
"""

from PIL import Image, ImageDraw, ImageFont
import io

def create_aicrete_logo():
    """Create a simple AIcrete logo"""
    # Create a new image with white background
    width, height = 400, 150
    image = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(image)
    
    # Draw a simple border
    border_color = '#1f77b4'  # Blue color
    draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=3)
    
    # Add company name (we'll use default font since we don't know what's available)
    try:
        # Try to use a larger font if available
        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Calculate text position to center it
    text = "AIcrete"
    text_width = draw.textlength(text, font=font)
    text_height = 20  # Approximate height
    
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2 - 20
    
    # Draw the main text
    draw.text((text_x, text_y), text, fill=border_color, font=font)
    
    # Add subtitle
    subtitle = "Concrete Solutions"
    subtitle_width = draw.textlength(subtitle, font=font)
    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = text_y + 30
    
    draw.text((subtitle_x, subtitle_y), subtitle, fill='#666666', font=font)
    
    # Add decorative elements
    draw.text((50, 40), "🏗️", font=font)
    draw.text((width-80, 40), "🧠", font=font)
    
    return image

if __name__ == "__main__":
    logo = create_aicrete_logo()
    logo.save("aicrete_logo.png")
    print("Logo created successfully!")
