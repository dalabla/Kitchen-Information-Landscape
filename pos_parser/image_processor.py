"""
Image processor for POS ticket OCR and parsing
Handles image preprocessing, text extraction, and order parsing
"""

import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import cv2
import numpy as np


@dataclass
class OrderItem:
    """Represents a single item from a POS ticket"""
    dish_name: str
    quantity: int
    modifiers: List[str]
    seat_number: Optional[int] = None
    course: Optional[str] = None  # appetizer, entree, dessert
    fire_time: Optional[str] = None  # "ASAP", "on_call", "after_apps"


@dataclass
class POSTicket:
    """Represents a complete POS ticket"""
    ticket_id: str
    table_number: str
    timestamp: datetime
    server_name: Optional[str]
    items: List[OrderItem]
    special_instructions: List[str]
    ticket_time: datetime  # When ticket was printed


class POSImageProcessor:
    """
    Processes POS images and extracts order information
    """

    # Common POS dish name variations to standardize
    DISH_NAME_MAPPING = {
        # Dates variations
        r'dates?\s*w[/.]?\s*ciabatta': 'dates',
        r'date\s*app': 'dates',
        r'stuffed\s*dates': 'dates',

        # Fish curry variations
        r'fish\s*curry': 'fish_curry',
        r'black\s*cod\s*curry': 'fish_curry',
        r'cod\s*w[/.]?\s*curry': 'fish_curry',

        # Prawns variations
        r'prawns?': 'prawns',
        r'shrimp\s*app': 'prawns',
        r'head[-\s]*on\s*prawns?': 'prawns',

        # Charred cabbage variations
        r'charred\s*cabbage': 'charred_cabbage',
        r'cabbage': 'charred_cabbage',
        r'roasted\s*cabbage': 'charred_cabbage',

        # Short rib variations
        r'short\s*rib': 'short_rib_radish_hummus',
        r'sr\s*[/.]?\s*hummus': 'short_rib_radish_hummus',
        r'beef\s*hummus': 'short_rib_radish_hummus',

        # Porterhouse variations
        r'porterhouse': 'porterhouse',
        r'p[-\s]*house': 'porterhouse',
        r'porter\s*steak': 'porterhouse',
        r'24\s*oz\s*steak': 'porterhouse',
    }

    # Modifier keywords
    MODIFIER_KEYWORDS = [
        'no', 'add', 'extra', 'sub', 'allergy', 'gf', 'gluten free',
        'vegan', 'vegetarian', 'rare', 'mr', 'medium rare', 'medium',
        'medium well', 'well done', 'spicy', 'mild', 'on side'
    ]

    def __init__(self, tesseract_config: str = '--oem 3 --psm 6'):
        """
        Initialize the POS image processor

        Args:
            tesseract_config: Tesseract OCR configuration
                --oem 3: Default OCR engine
                --psm 6: Assume uniform block of text
        """
        self.tesseract_config = tesseract_config

    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy

        Args:
            image_path: Path to POS image

        Returns:
            Preprocessed image as numpy array
        """
        # Read image
        img = cv2.imread(image_path)

        if img is None:
            raise ValueError(f"Could not read image from {image_path}")

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding for better text contrast
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)

        # Increase contrast
        pil_img = Image.fromarray(denoised)
        enhancer = ImageEnhance.Contrast(pil_img)
        enhanced = enhancer.enhance(2.0)

        # Sharpen
        sharpened = enhanced.filter(ImageFilter.SHARPEN)

        return np.array(sharpened)

    def extract_text(self, image_path: str) -> str:
        """
        Extract text from POS image using OCR

        Args:
            image_path: Path to POS image

        Returns:
            Extracted text
        """
        # Preprocess image
        processed = self.preprocess_image(image_path)

        # Perform OCR
        text = pytesseract.image_to_string(
            processed,
            config=self.tesseract_config
        )

        return text

    def parse_ticket_header(self, text: str) -> Tuple[str, str, Optional[str], datetime]:
        """
        Parse ticket header information

        Args:
            text: Raw OCR text

        Returns:
            Tuple of (ticket_id, table_number, server_name, timestamp)
        """
        lines = text.split('\n')

        ticket_id = None
        table_number = None
        server_name = None
        timestamp = datetime.now()

        for line in lines[:10]:  # Check first 10 lines for header info
            line = line.strip()

            # Extract ticket number
            ticket_match = re.search(r'(?:ticket|check|order)[\s#:]*(\d+)', line, re.IGNORECASE)
            if ticket_match and not ticket_id:
                ticket_id = ticket_match.group(1)

            # Extract table number
            table_match = re.search(r'(?:table|tbl|t)[\s#:]*(\d+[a-z]?)', line, re.IGNORECASE)
            if table_match and not table_number:
                table_number = table_match.group(1)

            # Extract server name
            server_match = re.search(r'(?:server|svr|srvr)[\s:]*([a-z]+)', line, re.IGNORECASE)
            if server_match and not server_name:
                server_name = server_match.group(1)

            # Extract timestamp
            time_match = re.search(r'(\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)', line, re.IGNORECASE)
            if time_match:
                try:
                    time_str = time_match.group(1)
                    timestamp = datetime.strptime(time_str, '%I:%M %p')
                except:
                    pass

        # Generate defaults if not found
        if not ticket_id:
            ticket_id = f"T{datetime.now().strftime('%H%M%S')}"
        if not table_number:
            table_number = "UNKNOWN"

        return ticket_id, table_number, server_name, timestamp

    def extract_modifiers(self, item_line: str) -> List[str]:
        """
        Extract modifiers from an item line

        Args:
            item_line: Line of text with potential modifiers

        Returns:
            List of modifiers
        """
        modifiers = []
        lower_line = item_line.lower()

        for keyword in self.MODIFIER_KEYWORDS:
            if keyword in lower_line:
                # Extract the modifier phrase
                pattern = rf'({keyword}[^,\n]*)'
                matches = re.findall(pattern, lower_line, re.IGNORECASE)
                modifiers.extend(matches)

        return [m.strip() for m in modifiers if m.strip()]

    def standardize_dish_name(self, raw_name: str) -> Optional[str]:
        """
        Standardize dish name from various POS formats

        Args:
            raw_name: Raw dish name from POS

        Returns:
            Standardized dish ID or None if not recognized
        """
        raw_lower = raw_name.lower().strip()

        for pattern, dish_id in self.DISH_NAME_MAPPING.items():
            if re.search(pattern, raw_lower):
                return dish_id

        return None

    def parse_order_items(self, text: str) -> List[OrderItem]:
        """
        Parse individual order items from ticket text

        Args:
            text: Raw OCR text

        Returns:
            List of OrderItem objects
        """
        items = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 3:
                continue

            # Look for quantity prefix (1x, 2 , etc.)
            quantity = 1
            qty_match = re.match(r'^(\d+)\s*[xX\-\*]?\s*', line)
            if qty_match:
                quantity = int(qty_match.group(1))
                line = line[qty_match.end():].strip()

            # Try to identify dish
            dish_id = self.standardize_dish_name(line)

            if dish_id:
                # Extract modifiers from this line and next few lines
                modifier_text = line
                for j in range(i+1, min(i+4, len(lines))):
                    next_line = lines[j].strip()
                    # If next line looks like a modifier (starts with -, *, or modifier keyword)
                    if next_line and (next_line.startswith(('-', '*', '+')) or
                                     any(kw in next_line.lower() for kw in self.MODIFIER_KEYWORDS)):
                        modifier_text += ' ' + next_line
                    elif self.standardize_dish_name(next_line):
                        # Hit next item, stop
                        break

                modifiers = self.extract_modifiers(modifier_text)

                # Determine course
                course = self._determine_course(dish_id, modifiers)

                # Extract seat number if present
                seat_match = re.search(r'seat\s*(\d+)', line, re.IGNORECASE)
                seat_number = int(seat_match.group(1)) if seat_match else None

                items.append(OrderItem(
                    dish_name=dish_id,
                    quantity=quantity,
                    modifiers=modifiers,
                    seat_number=seat_number,
                    course=course
                ))

        return items

    def _determine_course(self, dish_id: str, modifiers: List[str]) -> str:
        """Determine course type for dish"""
        appetizers = ['dates', 'prawns']
        entrees = ['fish_curry', 'charred_cabbage', 'short_rib_radish_hummus', 'porterhouse']

        if dish_id in appetizers:
            return 'appetizer'
        elif dish_id in entrees:
            return 'entree'

        return 'unknown'

    def extract_special_instructions(self, text: str) -> List[str]:
        """
        Extract special instructions from ticket

        Args:
            text: Raw OCR text

        Returns:
            List of special instructions
        """
        instructions = []
        lines = text.split('\n')

        # Look for common instruction markers
        instruction_markers = [
            'note:', 'notes:', 'special:', '*', 'allergy:',
            'important:', 'rush', 'vip', 'birthday', 'anniversary'
        ]

        for line in lines:
            line = line.strip()
            lower_line = line.lower()

            for marker in instruction_markers:
                if marker in lower_line:
                    instructions.append(line)
                    break

        return instructions

    def process_image(self, image_path: str) -> POSTicket:
        """
        Main processing function: convert POS image to structured ticket

        Args:
            image_path: Path to POS image file

        Returns:
            POSTicket object with all parsed information
        """
        # Extract text
        text = self.extract_text(image_path)

        # Parse header
        ticket_id, table_number, server_name, timestamp = self.parse_ticket_header(text)

        # Parse items
        items = self.parse_order_items(text)

        # Extract special instructions
        special_instructions = self.extract_special_instructions(text)

        return POSTicket(
            ticket_id=ticket_id,
            table_number=table_number,
            timestamp=timestamp,
            server_name=server_name,
            items=items,
            special_instructions=special_instructions,
            ticket_time=datetime.now()
        )

    def process_multiple_images(self, image_paths: List[str]) -> List[POSTicket]:
        """
        Process multiple POS images

        Args:
            image_paths: List of paths to POS images

        Returns:
            List of POSTicket objects
        """
        tickets = []
        for path in image_paths:
            try:
                ticket = self.process_image(path)
                tickets.append(ticket)
            except Exception as e:
                print(f"Error processing {path}: {e}")

        return tickets
