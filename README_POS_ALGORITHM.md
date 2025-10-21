# POS Image Algorithm - Kitchen Information Landscape

## 🎯 Overview

This algorithm processes Point of Sale (POS) ticket images and generates complete cooking instructions with equipment requirements, build steps, and plating details. It's designed to help kitchen staff get out of the weeds during busy service by providing intelligent order triage and step-by-step guidance.

## 🚀 Key Features

### 1. **Image Processing & OCR**
- Upload photos of POS tickets from any system
- Advanced image preprocessing for better OCR accuracy
- Intelligent parsing of order items, modifiers, and special instructions
- Handles various POS formats and layouts

### 2. **Complete Build Instructions**
- **Equipment Lists**: All tools needed for each dish
- **Ingredient Lists**: With quantities and storage locations
- **Step-by-Step Cooking**: Detailed instructions with:
  - Timing for each step
  - Temperature settings
  - Technique notes
  - Visual cues for doneness
- **Plating Instructions**: Exact plating steps with presentation notes
- **Sub-Recipes**: Instructions for prep components (e.g., crispy onions)

### 3. **Intelligent Order Triage**
- **Priority Scoring**: Automatically prioritizes orders based on:
  - Cook time (longer items fire first)
  - Ticket age (older tickets get priority)
  - Dish difficulty
  - Station clustering (batch similar items)
  - Course ordering (apps before entrees)

- **Station Workload Tracking**: Monitor capacity across stations
- **Bottleneck Detection**: Identifies overwhelmed stations
- **Firing Sequence**: Optimal timing for multi-course tables

### 4. **Kitchen Triage Mode**
When things get backed up:
- See all active orders prioritized
- Identify critical tasks requiring immediate attention
- Balance workload across stations
- Get quick reference cards for each dish
- Track progress and mark items complete

## 📋 System Architecture

```
┌─────────────────┐
│  POS Image      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Image Processor │ ← OCR + Preprocessing
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Parsed Ticket  │ (Table, Items, Mods, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Recipe Database │ ← Match to full recipes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Triage Engine   │ ← Calculate priorities
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Instruction   │ ← Generate complete instructions
│    Generator    │
└─────────────────┘
```

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- Tesseract OCR (for image processing)

### Install Tesseract

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

### Install Python Dependencies
```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Option 1: Web Interface (Recommended)

1. **Start the web server:**
```bash
cd web
python app.py
```

2. **Open browser to:** `http://localhost:5000`

3. **Upload a POS image:**
   - Drag and drop or click to upload
   - System will process and display complete instructions
   - See triage information and priority levels

### Option 2: Python API

```python
from pos_parser import (
    POSImageProcessor,
    RecipeDatabase,
    TriageEngine,
    InstructionGenerator
)

# Initialize components
recipe_db = RecipeDatabase()
image_processor = POSImageProcessor()
triage_engine = TriageEngine(recipe_db)
instruction_generator = InstructionGenerator(recipe_db)

# Process a POS image
ticket = image_processor.process_image('path/to/pos_image.jpg')

# Add to triage system
triage_engine.add_ticket(ticket)

# Get prioritized task list
tasks = triage_engine.get_prioritized_task_list()

# Generate instructions for highest priority task
if tasks:
    top_task = tasks[0]
    instructions = instruction_generator.generate_instructions(top_task)

    # Display formatted instructions
    formatted = instruction_generator.format_instructions_for_display(instructions)
    print(formatted)

# Get triage report
report = triage_engine.get_triage_report()
print(f"Active tasks: {report['total_active_tasks']}")
print(f"Bottleneck stations: {report['bottleneck_stations']}")
```

### Option 3: Command Line

```python
# example_usage.py
from pos_parser import POSImageProcessor, RecipeDatabase, TriageEngine, InstructionGenerator

def process_pos_ticket(image_path):
    # Setup
    recipe_db = RecipeDatabase()
    processor = POSImageProcessor()
    triage = TriageEngine(recipe_db)
    instructor = InstructionGenerator(recipe_db)

    # Process
    ticket = processor.process_image(image_path)
    triage.add_ticket(ticket)

    # Get instructions for all items
    tasks = triage.get_prioritized_task_list()
    for task in tasks:
        instructions = instructor.generate_instructions(task)
        print(instructor.format_instructions_for_display(instructions))
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        process_pos_ticket(sys.argv[1])
    else:
        print("Usage: python example_usage.py <path_to_pos_image>")
```

Run:
```bash
python example_usage.py pos_ticket.jpg
```

## 📖 Example Output

```
================================================================================
TABLE 42 - TICKET #1234
PORTERHOUSE STEAK
Station: GRILL | Time: 18 min | Difficulty: HARD | PRIORITY: CRITICAL
================================================================================

⚠️  CRITICAL NOTES ⚠️
THIS IS THE PRESTIGE DISH. Perfect execution required. Must rest full time.
Slice properly against grain. Don't serve over medium unless requested.

🔨 EQUIPMENT NEEDED:
  □ Charcoal grill or plancha
  □ Meat thermometer
  □ Tongs
  □ Basting brush
  □ Cutting board
  □ Sharp slicing knife
  □ Serving platter

📦 INGREDIENTS & LOCATION:
  □ Porterhouse steak (24 oz) - meat lowboy
  □ Ground green peppercorn (1 tsp) - spice mise
  □ Tomato coriander sauce (2 oz) - sauce station
  □ Black lime powder (pinch) - spice mise
  □ Labneh (2 oz) - cold station
  □ Peppercorn butter (2 oz) - butter mise
  □ Confit garlic cloves (6 pieces) - lowboy

⏰ TIMING:
  Fire early - needs 30 min room temp + 18 min cook + 8-10 min rest.
  Total 56 min from fire to pass.

👨‍🍳 COOKING STEPS:
⚠️STEP 1: Remove steak from lowboy 30 min before cooking
     Time: 30 min
     Note: Room temperature steak cooks evenly

  STEP 2: Season generously with salt and green peppercorn
     Time: 1 min
     Technique: Press seasoning into meat

  STEP 3: Ensure grill is at proper temp (500-600°F)
     Heat: 500-600°F

⚠️STEP 4: Place steak on hottest part of grill
     Time: 4 min
     Technique: Don't move it - let it sear
     Visual Cue: Good crust forming

[... etc ...]

🍽️  PLATING:
  Classic steakhouse presentation with Middle Eastern accents

  1. Slice steak by cutting meat off both sides of bone
  2. Slice strip and tenderloin against grain into 1/2 inch slices
  3. Reconstruct steak on platter with bone in center
  4. Spoon labneh on one side of plate
  5. Drizzle tomato coriander sauce on other side
  6. Arrange confit garlic cloves around steak
  7. Dust entire plate with black lime powder
  8. Pour any resting juices over sliced meat
  9. Top with any remaining peppercorn butter

  💡 Presentation: Dramatic presentation. Meat should glisten.
     Perfect medium-rare throughout. Bone adds theater.
================================================================================
```

## 🎨 Recipe Database Structure

Recipes are stored in `recipes/recipe_database.json`. Each dish includes:

- **Basic Info**: Name, station, cook time, difficulty
- **Equipment**: All tools needed
- **Ingredients**: With quantities and locations
- **Build Steps**: Detailed cooking instructions
- **Plating**: Step-by-step plating guide
- **Timing Notes**: When to fire, how to coordinate
- **Common Mods**: Typical modifications
- **Critical Notes**: Important warnings
- **Prep Components**: Sub-recipes (e.g., sauces, garnishes)

### Adding New Recipes

Edit `recipes/recipe_database.json`:

```json
{
  "dishes": {
    "your_dish_id": {
      "id": "your_dish_id",
      "name": "Your Dish Name",
      "station": "hot_entrees",
      "cook_time_minutes": 15,
      "difficulty": "medium",
      "equipment": ["pan", "spatula"],
      "ingredients": [
        {"name": "ingredient", "quantity": "1 oz", "location": "lowboy"}
      ],
      "build_steps": [
        {
          "step": 1,
          "action": "Heat pan",
          "time": "2 min",
          "temp": "medium-high"
        }
      ],
      "plating": {
        "description": "How to plate",
        "steps": ["Step 1", "Step 2"],
        "presentation_notes": "Final notes"
      },
      "timing_notes": "When to fire",
      "common_mods": ["mod 1", "mod 2"],
      "critical_notes": "Important warnings"
    }
  }
}
```

## 🧪 Triage Algorithm Details

### Priority Calculation

Priority score = (cook_time × 0.4) + (ticket_age × 0.25) + (difficulty × 0.15) + (station_clustering × 0.2) + course_bonus

**Factors:**
1. **Cook Time (40%)**: Longer dishes fire first
2. **Ticket Age (25%)**: Older tickets get priority
3. **Difficulty (15%)**: Harder dishes get more buffer
4. **Station Clustering (20%)**: Batch same-station items
5. **Course Bonus**: Apps get +10, entrees get +5

### Firing Sequence Logic

For multi-course tables:
1. Fire all appetizers immediately
2. For entrees:
   - Identify longest cooking item
   - Fire that item first
   - Stagger other items based on cook time difference
   - Goal: All entrees finish simultaneously

Example:
- Porterhouse (18 min) - Fire NOW
- Fish Curry (12 min) - Fire in 6 minutes
- Charred Cabbage (10 min) - Fire in 8 minutes

## 🔧 Configuration

### OCR Settings

In `pos_parser/image_processor.py`:

```python
processor = POSImageProcessor(
    tesseract_config='--oem 3 --psm 6'
)
# --oem 3: Default OCR engine
# --psm 6: Assume uniform block of text
# Adjust --psm for different ticket layouts:
#   --psm 4: Single column of text
#   --psm 11: Sparse text
```

### Priority Weights

In `recipes/recipe_database.json`:

```json
{
  "priority_factors": {
    "cook_time_weight": 0.4,
    "station_clustering": 0.2,
    "difficulty_weight": 0.15,
    "ticket_time_weight": 0.25
  }
}
```

Adjust these to change how orders are prioritized.

## 📱 Integration Ideas

### 1. Kitchen Display System (KDS)
Integrate with existing KDS to show instructions alongside orders

### 2. Mobile App
Build a mobile app for expo or sous chefs to manage triage on iPad

### 3. Print Station
Auto-print instructions at each station when orders fire

### 4. Voice Assistant
"Alexa, what are the steps for table 42's fish curry?"

### 5. Training Mode
Use for training new cooks - step-by-step guidance

## 🐛 Troubleshooting

### OCR Not Working
- Ensure Tesseract is installed: `tesseract --version`
- Try adjusting image preprocessing in `image_processor.py`
- Increase image resolution before uploading

### Dishes Not Recognized
- Check `DISH_NAME_MAPPING` in `image_processor.py`
- Add your POS's specific dish name patterns

### Instructions Not Generating
- Verify dish ID exists in `recipes/recipe_database.json`
- Check console for error messages

## 🎓 Use Cases

### 1. **Busy Service (Getting Out of the Weeds)**
When orders pile up:
- Upload all pending tickets
- System shows priority order
- Critical tasks highlighted
- Bottleneck stations identified

### 2. **Training New Cooks**
- New cook gets a ticket
- System shows complete instructions
- They can reference each step
- Learn proper technique and plating

### 3. **Expo/Pass Coordination**
- See firing sequence for tables
- Know when to call for items
- Coordinate multi-course timing

### 4. **Station Coverage**
- Regular cook calls out
- Replacement unfamiliar with dishes
- Step-by-step guidance ensures consistency

## 🤝 Contributing

To add dishes to the database:
1. Create entry in `recipes/recipe_database.json`
2. Add name variations to `DISH_NAME_MAPPING` in `image_processor.py`
3. Test with sample POS image
4. Document any special requirements

## 📄 License

This project is part of the Kitchen Information Landscape initiative.

## 🙏 Acknowledgments

Built to help kitchen staff execute at the highest level, even during the busiest services. From cooks to cooks.

---

**Questions? Issues?**
- Check the troubleshooting section
- Review example usage
- Test with sample images first
