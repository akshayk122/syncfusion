#!/usr/bin/env python3
"""
JSON to React Converter

This script converts Syncfusion PowerPoint JSON format to React components.
It uses Pydantic for data validation and modeling.
"""

import json
import os
import sys
from typing import List, Optional, Union, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, field_validator


# Pydantic models for Syncfusion PowerPoint JSON structure
class Font(BaseModel):
    """Font properties in Syncfusion format"""
    Color: Optional[str] = "#000000"
    FontName: Optional[str] = "Arial"
    FontSize: Optional[float] = 12
    Bold: Optional[bool] = False
    Italic: Optional[bool] = False


class ListFormat(BaseModel):
    """List format properties in Syncfusion format"""
    NumberStyle: Optional[str] = "AlphaLcPeriod"
    BulletCharacter: Optional[str] = "•"
    Color: Optional[str] = "#000000"
    Size: Optional[int] = 150
    StartValue: Optional[int] = 1
    Type: Optional[str] = "NotDefined"
    FontName: Optional[str] = None


class TextPart(BaseModel):
    """Text part properties in Syncfusion format"""
    Font: Font
    Text: str


class Paragraph(BaseModel):
    """Paragraph properties in Syncfusion format"""
    Text: str
    HorizontalAlignment: Optional[str] = "Left"
    TextParts: List[TextPart]
    ListFormat: Optional[ListFormat] = None
    IndentLevelNumber: Optional[int] = 0
    Font: Optional[Font] = None
    EndParagraphFont: Optional[Font] = None


class TextBody(BaseModel):
    """Text body properties in Syncfusion format"""
    Paragraphs: List[Paragraph]
    Text: Optional[str] = ""
    WrapText: Optional[bool] = False
    AnchorCenter: Optional[bool] = False
    VerticalAlignment: Optional[str] = "Top"
    TextDirection: Optional[str] = "Horizontal"


class FillFormat(BaseModel):
    """Fill format properties"""
    Color: Optional[str] = "transparent"


class LineFormat(BaseModel):
    """Line format properties"""
    Color: Optional[str] = "black"
    Width: Optional[float] = 1
    Style: Optional[str] = "solid"


class SlideItem(BaseModel):
    """Base model for slide items"""
    SlideItemType: Optional[str] = None
    AutoShapeType: Optional[str] = None
    ShapeId: Optional[int] = None
    Left: Optional[float] = 0
    Top: Optional[float] = 0
    Width: Optional[float] = 100
    Height: Optional[float] = 50
    Rotation: Optional[float] = 0
    TextBody: Optional[Union[TextBody, Dict[str, Any]]] = None
    FillFormat: Optional[Union[FillFormat, Dict[str, Any]]] = None
    LineFormat: Optional[Union[LineFormat, Dict[str, Any]]] = None
    ImageData: Optional[Dict[str, Any]] = None
    ShadowFormat: Optional[Dict[str, Any]] = None
    Opacity: Optional[float] = 100
    ZIndex: Optional[int] = 0
    Info: Optional[str] = None
    
    # Allow extra fields to support any future properties in the JSON
    model_config = {
        "extra": "allow"
    }
    
    @field_validator('TextBody', mode='before')
    @classmethod
    def validate_text_body(cls, v):
        if isinstance(v, dict):
            try:
                return TextBody(**v)
            except Exception:
                return v
        return v


def load_json(file_path: str) -> List[SlideItem]:
    """
    Load and parse the JSON file using Pydantic models.
    
    Args:
        file_path: Path to the Syncfusion JSON file
        
    Returns:
        List[SlideItem]: List of slide items
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Handle different JSON structures
        # Some PowerPoint JSONs might have a top-level structure with slides/items
        if isinstance(json_data, dict):
            # Try to find items in common PowerPoint JSON structures
            if "slides" in json_data and isinstance(json_data["slides"], list):
                json_data = json_data["slides"]
            elif "Slides" in json_data and isinstance(json_data["Slides"], list):
                json_data = json_data["Slides"]
            elif "items" in json_data and isinstance(json_data["items"], list):
                json_data = json_data["items"]
            elif "Items" in json_data and isinstance(json_data["Items"], list):
                json_data = json_data["Items"]
            elif "content" in json_data and isinstance(json_data["content"], list):
                json_data = json_data["content"]
            elif "Content" in json_data and isinstance(json_data["Content"], list):
                json_data = json_data["Content"]
            # If we can't find a list structure, wrap the dict in a list
            elif not isinstance(json_data, list):
                json_data = [json_data]
        
        # Ensure we're working with a list
        if not isinstance(json_data, list):
            print("Warning: JSON data is not in expected format. Attempting to convert.")
            json_data = [json_data]
            
        # Parse JSON data using Pydantic models
        slide_items = []
        for item in json_data:
            try:
                # Skip items with circular references
                if isinstance(item, dict) and "Info" in item and "Circular reference detected" in item["Info"]:
                    slide_items.append(SlideItem(Info=item["Info"]))
                    continue
                
                # Handle nested items
                if isinstance(item, dict) and ("items" in item or "Items" in item):
                    nested_items = item.get("items") or item.get("Items") or []
                    for nested_item in nested_items:
                        try:
                            slide_items.append(SlideItem(**nested_item))
                        except Exception as e:
                            print(f"Error parsing nested slide item: {e}")
                            slide_items.append(SlideItem(Info=f"Error parsing nested item: {str(e)}"))
                    continue
                
                slide_items.append(SlideItem(**item))
            except Exception as e:
                print(f"Error parsing slide item: {e}")
                # Add as a basic model with just the info field
                if isinstance(item, dict):
                    slide_items.append(SlideItem(Info=f"Error parsing: {str(e)}"))
        
        return slide_items
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        return []


def generate_react_component_for_item(item: SlideItem) -> str:
    """
    Generate a React component for a given slide item.
    
    Args:
        item: Slide item data
        
    Returns:
        str: React component JSX
    """
    # Skip items with circular references
    if item.Info and "Circular reference detected" in item.Info:
        return ""
    
    # Basic position and style - convert PowerPoint points to pixels (1 pt = 1.33333 px)
    style_props = [
        f"position: 'absolute'",
        f"left: '{item.Left * 1.33333}px'",
        f"top: '{item.Top * 1.33333}px'",
        f"width: '{item.Width * 1.33333}px'",
        f"height: '{item.Height * 1.33333}px'"
    ]
    
    # Add rotation if present
    if item.Rotation and item.Rotation != 0:
        style_props.append(f"transform: 'rotate({item.Rotation}deg)'")
    
    # Process fill format
    if item.FillFormat:
        fill_format = item.FillFormat
        if isinstance(fill_format, dict):
            # Handle dictionary format
            fill_type = fill_format.get("Type")
            
            if fill_type == "Solid" or not fill_type:
                # Solid fill
                if "Color" in fill_format:
                    color = fill_format.get("Color")
                    style_props.append(f"backgroundColor: '{color}'")
            elif fill_type == "Gradient" and "Gradient" in fill_format:
                # Gradient fill - simplified handling
                color = fill_format.get('Color', '#ffffff')
                style_props.append(f"background: 'linear-gradient(90deg, {color}, #e0e0e0)'")
            elif fill_type == "Picture" and "Image" in fill_format:
                # Image fill - simplified handling
                style_props.append("backgroundSize: 'cover'")
                style_props.append("backgroundPosition: 'center'")
        else:
            # Handle model format
            if hasattr(fill_format, 'Color') and fill_format.Color:
                style_props.append(f"backgroundColor: '{fill_format.Color}'")
    
    # Process line format
    if item.LineFormat:
        line_format = item.LineFormat
        if isinstance(line_format, dict):
            # Handle dictionary format
            if "Color" in line_format:
                style_props.append(f"borderColor: '{line_format['Color']}'")
            if "Width" in line_format:
                style_props.append(f"borderWidth: '{line_format['Width'] * 1.33333}px'")
            if "Style" in line_format:
                border_style = line_format["Style"].lower() if isinstance(line_format["Style"], str) else "solid"
                style_props.append(f"borderStyle: '{border_style}'")
        else:
            # Handle model format
            if hasattr(line_format, 'Color') and line_format.Color:
                style_props.append(f"borderColor: '{line_format.Color}'")
            if hasattr(line_format, 'Width') and line_format.Width:
                style_props.append(f"borderWidth: '{line_format.Width * 1.33333}px'")
            if hasattr(line_format, 'Style') and line_format.Style:
                style_props.append(f"borderStyle: '{line_format.Style}'")
    
    # Process shadow format
    if item.ShadowFormat:
        shadow_format = item.ShadowFormat
        if isinstance(shadow_format, dict):
            shadow_color = shadow_format.get("Color", "rgba(0,0,0,0.3)")
            style_props.append(f"boxShadow: '2px 2px 5px {shadow_color}'")
    
    # Combine style properties
    style_str = ",\n        ".join(style_props)
    
    # Process text content if present
    text_content = ""
    if item.TextBody:
        paragraphs = []
        
        # Handle both TextBody model and dictionary
        paragraphs_data = []
        if isinstance(item.TextBody, TextBody) and item.TextBody.Paragraphs:
            paragraphs_data = item.TextBody.Paragraphs
        elif isinstance(item.TextBody, dict) and "Paragraphs" in item.TextBody:
            paragraphs_data = item.TextBody["Paragraphs"]
            
        for para_data in paragraphs_data:
            # Skip empty paragraphs
            if isinstance(para_data, Paragraph):
                if not para_data.Text.strip():
                    continue
                para_text = para_data.Text
                para_parts = para_data.TextParts
                para_alignment = para_data.HorizontalAlignment
                para_indent = para_data.IndentLevelNumber
                para_list_format = para_data.ListFormat
            else:  # Dictionary
                if not para_data.get("Text", "").strip():
                    continue
                para_text = para_data.get("Text", "")
                para_parts = para_data.get("TextParts", [])
                para_alignment = para_data.get("HorizontalAlignment")
                para_indent = para_data.get("IndentLevelNumber")
                para_list_format = para_data.get("ListFormat")
                
            # Process text formatting
            text_parts = []
            
            # Add bullet if needed - only once per paragraph
            prefix = ""
            if para_list_format:
                list_type = para_list_format.Type if isinstance(para_list_format, ListFormat) else para_list_format.get("Type")
                if list_type == "Bulleted":
                    bullet_char = "•"
                    if isinstance(para_list_format, ListFormat):
                        bullet_char = para_list_format.BulletCharacter or "•"
                    else:
                        bullet_char = para_list_format.get("BulletCharacter", "•")
                    prefix = f"{bullet_char} "
            
            for part_data in para_parts:
                if isinstance(part_data, TextPart):
                    font = part_data.Font
                    part_text = part_data.Text
                else:  # Dictionary
                    font_data = part_data.get("Font", {})
                    font = font_data if isinstance(font_data, Font) else font_data
                    part_text = part_data.get("Text", "")
                
                text_style_props = []
                
                # Get font properties, handling both model and dict
                if isinstance(font, Font):
                    # Check background color to determine appropriate text color for contrast
                    bg_color = next((prop.split(":")[1].strip(" '") for prop in style_props if "backgroundColor" in prop), None)
                    
                    # If background is light (#f0f0f0), use dark text
                    if bg_color and bg_color in ['#f0f0f0', '#ffffff', '#FFFFFF']:
                        text_style_props.append("color: '#156082'")
                    # If background is dark blue, use white text
                    elif hasattr(item, '_needs_contrasting_text') and item._needs_contrasting_text:
                        text_style_props.append("color: '#FFFFFF'")
                    elif font.Color:
                        text_style_props.append(f"color: '{font.Color}'")
                    
                    if font.FontName:
                        # Replace Aptos with more widely supported fonts
                        font_name = font.FontName
                        if font_name == 'Aptos':
                            text_style_props.append(f"fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif'")
                        else:
                            text_style_props.append(f"fontFamily: '{font_name}, Arial, sans-serif'")
                    if font.FontSize:
                        text_style_props.append(f"fontSize: '{font.FontSize}px'")
                    if font.Bold:
                        text_style_props.append("fontWeight: 'bold'")
                    if font.Italic:
                        text_style_props.append("fontStyle: 'italic'")
                else:  # Dictionary
                    # Check background color to determine appropriate text color for contrast
                    bg_color = next((prop.split(":")[1].strip(" '") for prop in style_props if "backgroundColor" in prop), None)
                    
                    # If background is light (#f0f0f0), use dark text
                    if bg_color and bg_color in ['#f0f0f0', '#ffffff', '#FFFFFF']:
                        text_style_props.append("color: '#156082'")
                    # If background is dark blue, use white text
                    elif hasattr(item, '_needs_contrasting_text') and item._needs_contrasting_text:
                        text_style_props.append("color: '#FFFFFF'")
                    elif font.get("Color"):
                        color = font.get("Color")
                        text_style_props.append(f"color: '{color}'")
                        
                    if font.get("FontName"):
                        font_name = font.get("FontName")
                        # Replace Aptos with more widely supported fonts
                        if font_name == 'Aptos':
                            text_style_props.append(f"fontFamily: 'Segoe UI, Roboto, Helvetica, Arial, sans-serif'")
                        else:
                            text_style_props.append(f"fontFamily: '{font_name}, Arial, sans-serif'")
                    if font.get("FontSize"):
                        font_size = font.get("FontSize")
                        text_style_props.append(f"fontSize: '{font_size}px'")
                    if font.get("Bold"):
                        text_style_props.append("fontWeight: 'bold'")
                    if font.get("Italic"):
                        text_style_props.append("fontStyle: 'italic'")
                
                text_style_str = ", ".join(text_style_props)
                
                # Add prefix only to the first text part
                current_prefix = prefix if len(text_parts) == 0 else ""
                
                # Create text part with style - using proper JSX style object syntax
                text_style_str = ", ".join(text_style_props)
                if text_style_props:
                    text_part = f"<span style={{{{ {text_style_str} }}}}>{current_prefix}{part_text}</span>"
                else:
                    text_part = f"<span>{current_prefix}{part_text}</span>"
                text_parts.append(text_part)
            
            # Create paragraph with alignment and indentation
            para_style_props = []
            
            # Add text alignment
            if para_alignment:
                alignment = para_alignment.lower() if isinstance(para_alignment, str) else para_alignment
                para_style_props.append(f"textAlign: '{alignment}'")
            
            # Add indentation for list items
            if para_indent and para_indent > 0:
                # Store bullet-indent class separately, not in style props
                if not hasattr(item, '_bullet_indent_class'):
                    item._bullet_indent_class = True
                para_style_props.append(f"marginLeft: '{para_indent * 20}px'")
            
            para_style_str = ", ".join(para_style_props)
            
            if para_style_str:
                paragraph = f"<div style={{{{ {para_style_str} }}}}>{' '.join(text_parts)}</div>"
            else:
                paragraph = f"<div>{' '.join(text_parts)}</div>"
            
            paragraphs.append(paragraph)
        
        text_content = "\n        ".join(paragraphs)
    
    # Process opacity if present
    if item.Opacity is not None and item.Opacity != 100:
        opacity_value = item.Opacity / 100
        style_props.append(f"opacity: {opacity_value}")
    
    # Process z-index if present
    if item.ZIndex is not None:
        style_props.append(f"zIndex: {item.ZIndex}")
        
    # Ensure all shapes have a background color for visibility
    if not any("backgroundColor" in prop for prop in style_props):
        style_props.append("backgroundColor: '#f0f0f0'")
    
    # Process fill color if present
    fill_color = None
    if hasattr(item, 'Fill') and item.Fill is not None:
        if hasattr(item.Fill, 'FillType') and item.Fill.FillType == 'Solid':
            if hasattr(item.Fill, 'SolidFill') and hasattr(item.Fill.SolidFill, 'Color'):
                fill_color = item.Fill.SolidFill.Color
    
    # Determine the component to use based on shape type
    component = "div"
    if item.SlideItemType == "AutoShape":
        # Handle different auto shape types
        if item.AutoShapeType == "RightArrow":
            # Don't add clipPath directly in JSX - we'll handle it in CSS for better browser compatibility
            # Only add background color if not already specified in FillFormat
            if not any("backgroundColor" in prop for prop in style_props):
                style_props.append("backgroundColor: '#e67e22'")
            
            # Add placeholder content for empty arrows to ensure visibility
            if not text_content or text_content == "":
                text_content = "<div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#ffffff' }}>→</div>"
        elif item.AutoShapeType == "LeftArrow":
            # Don't add clipPath directly in JSX - we'll handle it in CSS for better browser compatibility
            if not any("backgroundColor" in prop for prop in style_props):
                style_props.append("backgroundColor: '#3498db'")
            
            # Add placeholder content for empty arrows to ensure visibility
            if not text_content or text_content == "":
                text_content = "<div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#ffffff' }}>←</div>"
        elif item.AutoShapeType == "UpArrow":
            # Don't add clipPath directly in JSX - we'll handle it in CSS for better browser compatibility
            if not any("backgroundColor" in prop for prop in style_props):
                style_props.append("backgroundColor: '#2ecc71'")
            
            # Add placeholder content for empty arrows to ensure visibility
            if not text_content or text_content == "":
                text_content = "<div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#ffffff' }}>↑</div>"
        elif item.AutoShapeType == "DownArrow":
            # Don't add clipPath directly in JSX - we'll handle it in CSS for better browser compatibility
            if not any("backgroundColor" in prop for prop in style_props):
                style_props.append("backgroundColor: '#9b59b6'")
            
            # Add placeholder content for empty arrows to ensure visibility
            if not text_content or text_content == "":
                text_content = "<div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: '#ffffff' }}>↓</div>"
        elif item.AutoShapeType == "Circle" or item.AutoShapeType == "Oval":
            style_props.append("borderRadius: '50%'")
            if not any("backgroundColor" in prop for prop in style_props):
                style_props.append("backgroundColor: '#f0f0f0'")
        elif item.AutoShapeType == "RoundedRectangle":
            style_props.append("borderRadius: '10px'")
        elif item.AutoShapeType == "Diamond":
            # Don't add clipPath directly in JSX - we'll handle it in CSS for better browser compatibility
            style_props.append("backgroundColor: '#f0f0f0'")
        elif item.AutoShapeType == "Triangle":
            # Don't add clipPath directly in JSX - we'll handle it in CSS for better browser compatibility
            style_props.append("backgroundColor: '#f0f0f0'")
        elif item.AutoShapeType == "Pentagon":
            # Don't add clipPath directly in JSX - we'll handle it in CSS for better browser compatibility
            style_props.append("backgroundColor: '#f0f0f0'")
        elif item.AutoShapeType == "Hexagon":
            # Don't add clipPath directly in JSX - we'll handle it in CSS for better browser compatibility
            style_props.append("backgroundColor: '#f0f0f0'")
            
        # Special case for Rectangle with title text - preserve the color from TextBody
        if item.AutoShapeType == "Rectangle" and item.TextBody:
            text_body = item.TextBody
            paragraphs_data = []
            
            if isinstance(text_body, TextBody) and text_body.Paragraphs:
                paragraphs_data = text_body.Paragraphs
            elif isinstance(text_body, dict) and "Paragraphs" in text_body:
                paragraphs_data = text_body["Paragraphs"]
                
            # Check if any paragraph contains text parts with specific color
            for para_data in paragraphs_data:
                text_parts = []
                if isinstance(para_data, Paragraph):
                    text_parts = para_data.TextParts
                elif isinstance(para_data, dict):
                    text_parts = para_data.get("TextParts", [])
                
                for part in text_parts:
                    font = None
                    if isinstance(part, TextPart):
                        font = part.Font
                    elif isinstance(part, dict) and "Font" in part:
                        font = part["Font"]
                    
                    # If font has color #156082 (blue), apply it to the rectangle background
                    # and change text color to white for contrast
                    if font:
                        color = None
                        if isinstance(font, Font) and font.Color == "#156082":
                            color = font.Color
                        elif isinstance(font, dict) and font.get("Color") == "#156082":
                            color = font.get("Color")
                            
                        if color and not any("backgroundColor" in prop for prop in style_props):
                            style_props.append(f"backgroundColor: '{color}'")
                            
                            # Always use white text on dark blue background for contrast
                            if not hasattr(item, '_needs_contrasting_text'):
                                item._needs_contrasting_text = True
    elif item.SlideItemType == "Picture" or (item.SlideItemType == "AutoShape" and item.AutoShapeType == "Picture"):
        # Handle picture elements
        if item.ImageData:
            image_data = item.ImageData
            if isinstance(image_data, dict):
                if "Base64" in image_data:
                    # Use img tag for pictures
                    component = "img"
                    base64_data = image_data.get("Base64", "")
                    style_props.append(f"src: 'data:image/png;base64,{base64_data}'")
                    style_props.append("objectFit: 'cover'")
                elif "ImagePath" in image_data:
                    component = "img"
                    image_path = image_data.get("ImagePath", "")
                    style_props.append(f"src: '{image_path}'")
                    style_props.append("objectFit: 'cover'")
    elif item.SlideItemType == "Chart":
        # For charts, we would need to implement chart rendering
        # This is a placeholder for chart handling
        style_props.append("backgroundColor: '#f0f0f0'")
        text_content = "<div style={{ textAlign: 'center', padding: '20px' }}>Chart Placeholder</div>"
    
    # Update style string after adding shape-specific styles
    style_str = ",\n        ".join(style_props)
    
    # Add any additional attributes from the item that might be useful
    additional_attrs = []
    
    # Add data attributes for shape type and slide item type
    if item.AutoShapeType:
        additional_attrs.append(f'data-shape-type="{item.AutoShapeType}"')
    if item.SlideItemType:
        additional_attrs.append(f'data-slide-item-type="{item.SlideItemType}"')
    
    # Add any other custom properties as data attributes
    for key, value in item.__dict__.items():
        if key not in ['SlideItemType', 'AutoShapeType', 'ShapeId', 'Left', 'Top', 'Width', 'Height', 
                      'Rotation', 'TextBody', 'FillFormat', 'LineFormat', 'ImageData', 'ShadowFormat', 
                      'Opacity', 'ZIndex', 'Info'] and value is not None:
            if isinstance(value, (str, int, float, bool)):
                additional_attrs.append(f'data-{key.lower()}="{value}"')
    
    additional_attrs_str = " ".join(additional_attrs)
    
    # Generate the JSX with proper style syntax
    # Add specific classes for different shape types for better CSS targeting
    shape_class = "syncfusion-shape"
    if item.SlideItemType == "AutoShape":
        shape_class += f" shape-{item.AutoShapeType.lower()}" if item.AutoShapeType else ""
    elif item.SlideItemType == "Picture":
        shape_class += " shape-picture"
    elif item.SlideItemType == "Chart":
        shape_class += " shape-chart"
        
    # Add bullet-indent class if needed (separate from style props)
    if hasattr(item, '_bullet_indent_class') and item._bullet_indent_class:
        shape_class += " bullet-indent"
        
    jsx = f"""
    <{component} 
      id="shape_{item.ShapeId}"
      className="{shape_class}"
      style={{{{ {style_str} }}}}
      {additional_attrs_str}
    >
        {text_content}
    </{component}>"""
    
    return jsx


def convert_json_to_react(slide_items: List[SlideItem], slide_props: Dict[str, Any] = None) -> str:
    """
    Convert Syncfusion PowerPoint JSON to React components.
    
    Args:
        slide_items: List of slide items
        slide_props: Optional slide properties (width, height, background, etc.)
        
    Returns:
        str: Complete React component code
    """
    if not slide_props:
        # Default slide size for PowerPoint is 720x540 points
        # Convert to pixels (1 pt = 1.33333 px)
        slide_props = {
            "width": 960,  # 720 * 1.33333
            "height": 720,  # 540 * 1.33333
            "background": "#ffffff"
        }
    
    # Generate components for each slide item
    components = []
    for item in slide_items:
        component = generate_react_component_for_item(item)
        if component:
            components.append(component)
    
    # Create the React component
    component_jsx = "\n".join(components)
    
    # Create the React component file with proper CSS imports and styling
    react_component = f"""import React from 'react';
import './SyncfusionSlide.css';

/**
 * SyncfusionSlide - A React component that renders a PowerPoint slide
 * converted from Syncfusion JSON format.
 * 
 * The component preserves the visual properties of the PowerPoint elements including:
 * - Position (Left, Top, Width, Height)
 * - Formatting (Fill, LineFormat)
 * - Text content with formatting
 * - Rotation
 * - Shape types
 */
export const SyncfusionSlide = () => {{
  return (
    <div 
      className="syncfusion-slide"
      style={{{{
        position: 'relative',
        width: '{slide_props['width']}px',
        height: '{slide_props['height']}px',
        backgroundColor: '{slide_props['background']}',
        overflow: 'hidden',
        boxSizing: 'border-box',
        fontFamily: 'Arial, sans-serif'
      }}}}
    >
{component_jsx}
    </div>
  );
}};

// CSS file (SyncfusionSlide.css) should include:
// .syncfusion-slide {{
//   border: 1px solid #ccc;
//   box-shadow: 0 2px 5px rgba(0,0,0,0.1);
// }}
// .syncfusion-shape {{
//   box-sizing: border-box;
// }}

export default SyncfusionSlide;
"""
    
    return react_component


def main():
    """Main function to execute the conversion."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Convert Syncfusion PowerPoint JSON to React components')
    parser.add_argument('--input', '-i', type=str, help='Input JSON file path', required=True)
    parser.add_argument('--output', '-o', type=str, help='Output React component file path', required=True)
    parser.add_argument('--css', '-c', type=str, help='Output CSS file path', default=None)
    
    args = parser.parse_args()
    
    # Load JSON data
    slide_items = load_json(args.input)
    
    if not slide_items:
        print(f"Error: No valid slide items found in {args.input}")
        sys.exit(1)
        
    # Convert to React
    react_component = convert_json_to_react(slide_items)
    
    # Write to output file
    try:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(react_component)
        print(f"Successfully converted {args.input} to {args.output}")
        
        # Generate CSS file if specified
        if args.css:
            css_content = """/* Main slide container */
.syncfusion-slide {
  border: 1px solid #ccc;
  box-shadow: 0 2px 5px rgba(0,0,0,0.1);
  margin: 0 auto;
  position: relative;
}

/* Base shape styling */
.syncfusion-shape {
  box-sizing: border-box;
  overflow: hidden;
}

/* Ensure text is visible with proper contrast */
.syncfusion-shape div {
  margin: 0;
  padding: 4px;
}

/* Indented bullet points */
.bullet-indent {
  text-align: left;
  margin-left: 20px !important;
  padding-left: 10px !important;
}

/* Web fonts fallback */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

/* Empty shapes need to be visible */
.syncfusion-shape:empty {
  min-height: 20px;
  min-width: 20px;
}

/* Specific shape type styling */
.shape-rectangle {
  border-radius: 0;
}

.shape-roundedrectangle {
  border-radius: 10px;
}

.shape-circle, .shape-oval {
  border-radius: 50%;
}

/* Shape clipPaths for modern browsers */
.shape-rightarrow {
  clip-path: polygon(0 25%, 75% 25%, 75% 0, 100% 50%, 75% 100%, 75% 75%, 0 75%);
}

.shape-leftarrow {
  clip-path: polygon(25% 0%, 25% 20%, 100% 20%, 100% 80%, 25% 80%, 25% 100%, 0% 50%);
}

.shape-uparrow {
  clip-path: polygon(20% 25%, 0% 25%, 50% 0%, 100% 25%, 80% 25%, 80% 100%, 20% 100%);
}

.shape-downarrow {
  clip-path: polygon(20% 0%, 20% 75%, 0% 75%, 50% 100%, 100% 75%, 80% 75%, 80% 0%);
}

.shape-diamond {
  clip-path: polygon(50% 0%, 100% 50%, 50% 100%, 0% 50%);
}

.shape-triangle {
  clip-path: polygon(50% 0%, 100% 100%, 0% 100%);
}

.shape-pentagon {
  clip-path: polygon(50% 0%, 100% 38%, 82% 100%, 18% 100%, 0% 38%);
}

.shape-hexagon {
  clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
}

/* Fallback for clipPath in older browsers */
@supports not (clip-path: polygon(0 0)) {
  .shape-rightarrow, .shape-leftarrow, .shape-uparrow, .shape-downarrow, 
  .shape-diamond, .shape-triangle, .shape-pentagon, .shape-hexagon {
    position: relative;
  }
  
  .shape-rightarrow::after, .shape-leftarrow::after, .shape-uparrow::after, 
  .shape-downarrow::after, .shape-diamond::after, .shape-triangle::after, 
  .shape-pentagon::after, .shape-hexagon::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
  }
  
  .shape-rightarrow::after {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 50'%3E%3Cpolygon points='0,10 75,10 75,0 100,25 75,50 75,40 0,40' fill='%23e67e22'/%3E%3C/svg%3E");
  }
  
  .shape-leftarrow::after {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 50'%3E%3Cpolygon points='25,0 25,10 100,10 100,40 25,40 25,50 0,25' fill='%233498db'/%3E%3C/svg%3E");
  }
  
  .shape-uparrow::after {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 50 100'%3E%3Cpolygon points='10,25 0,25 25,0 50,25 40,25 40,100 10,100' fill='%232ecc71'/%3E%3C/svg%3E");
  }
  
  .shape-downarrow::after {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 50 100'%3E%3Cpolygon points='10,0 10,75 0,75 25,100 50,75 40,75 40,0' fill='%239b59b6'/%3E%3C/svg%3E");
  }
}
"""
            with open(args.css, 'w', encoding='utf-8') as f:
                f.write(css_content)
            print(f"Generated CSS file: {args.css}")
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()