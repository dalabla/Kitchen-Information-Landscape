# Kitchen Information Landscape

> A comprehensive system for organizing, triaging, and executing kitchen workflows during busy service

## Overview

The Kitchen Information Landscape project provides tools to help culinary teams maintain excellence during high-volume service periods. It combines visual mise en place tracking with intelligent order triage and complete cooking instructions.

## Components

### 1. **Mise en Place Information Landscape** (`Kitchen Information Landscape.html`)

An interactive visual dashboard for tracking back-of-house prep work:
- General prep station tracking
- Dish-specific component checklists
- Equipment verification
- Progress monitoring
- Shared ingredient highlighting

[View the Mise en Place Dashboard](Kitchen%20Information%20Landscape.html)

### 2. **POS Image Algorithm** (New!)

An intelligent system that processes Point of Sale ticket images and generates complete cooking instructions with order triage.

**Key Features:**
- 📸 Upload photos of POS tickets
- 🔍 Automatic OCR and order parsing
- 🎯 Intelligent priority-based triage
- 📋 Complete build instructions with equipment, ingredients, and plating
- ⚡ Helps get out of the weeds during rush

**Quick Start:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run web interface
cd web
python app.py

# Open browser to http://localhost:5000
```

**Documentation:**
- [Complete POS Algorithm Guide](README_POS_ALGORITHM.md) - Full usage documentation
- [Algorithm Technical Summary](ALGORITHM_SUMMARY.md) - Technical deep dive
- [Example Usage](example_usage.py) - Code examples

**What it does:**
1. Takes a photo of your POS ticket
2. Reads the order using OCR
3. Matches dishes to full recipes with:
   - Equipment requirements
   - Ingredient lists with locations
   - Step-by-step cooking instructions
   - Timing and temperature guidance
   - Plating instructions
4. Prioritizes orders intelligently based on:
   - Cook times
   - Ticket age
   - Difficulty
   - Station clustering
5. Shows triage report with bottlenecks and critical tasks

## Project Structure

```
Kitchen-Information-Landscape/
├── Kitchen Information Landscape.html  # Mise en place dashboard
├── pos_parser/                        # POS algorithm modules
│   ├── image_processor.py            # OCR and parsing
│   ├── recipe_database.py            # Recipe management
│   ├── triage_engine.py              # Order prioritization
│   └── instruction_generator.py      # Instruction builder
├── recipes/                           # Recipe database
│   └── recipe_database.json          # Complete dish instructions
├── web/                              # Web interface
│   ├── app.py                        # Flask application
│   └── templates/                    # HTML templates
├── tests/                            # Test suite
├── requirements.txt                  # Python dependencies
├── example_usage.py                  # Usage examples
├── README_POS_ALGORITHM.md          # POS algorithm documentation
└── ALGORITHM_SUMMARY.md             # Technical summary
```

## Use Cases

### During Prep
Use the **Mise en Place Dashboard** to:
- Track prep completion across stations
- Verify all components are ready
- Identify shared ingredients
- Ensure equipment is staged

### During Service
Use the **POS Algorithm** to:
- Parse incoming tickets instantly
- Prioritize orders optimally
- Get step-by-step cooking guidance
- Coordinate multi-course timing
- Identify and resolve bottlenecks

### For Training
- New cooks get complete instructions
- Visual cues for quality control
- Technique notes for proper execution
- Plating guidance for consistency

## Getting Started

### Prerequisites
- Python 3.8+
- Tesseract OCR (for POS image processing)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/dalabla/Kitchen-Information-Landscape.git
cd Kitchen-Information-Landscape
```

2. **Install Tesseract OCR:**
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from: https://github.com/UB-Mannheim/tesseract/wiki
```

3. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the web interface:**
```bash
cd web
python app.py
```

5. **Open your browser:**
```
http://localhost:5000
```

### Quick Test

Run the demo without uploading images:
```bash
python example_usage.py
```

This will show sample output with mock ticket data.

## Example: Processing a POS Ticket

```python
from pos_parser import POSImageProcessor, RecipeDatabase, TriageEngine, InstructionGenerator

# Initialize
recipe_db = RecipeDatabase()
processor = POSImageProcessor()
triage = TriageEngine(recipe_db)
instructor = InstructionGenerator(recipe_db)

# Process POS image
ticket = processor.process_image('pos_ticket.jpg')

# Add to triage
triage.add_ticket(ticket)

# Get prioritized tasks
tasks = triage.get_prioritized_task_list()

# Generate instructions for top priority
instructions = instructor.generate_instructions(tasks[0])
print(instructor.format_instructions_for_display(instructions))
```

## Contributing

To add new recipes:
1. Edit `recipes/recipe_database.json`
2. Add dish name variations to `pos_parser/image_processor.py`
3. Test with sample POS images

## License

This project is part of the Kitchen Information Landscape initiative.

## Support

- [Full Documentation](README_POS_ALGORITHM.md)
- [Technical Details](ALGORITHM_SUMMARY.md)
- [Example Code](example_usage.py)
- [Run Tests](tests/test_basic.py)

---

**Built to help kitchen staff execute at the highest level, even during the busiest services.**
