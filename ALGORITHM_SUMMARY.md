# POS Image Algorithm - Technical Summary

## Algorithm Overview

This system transforms Point of Sale (POS) ticket images into actionable cooking instructions with intelligent order prioritization. It's designed to help kitchen staff maintain quality during high-volume service periods.

## Core Algorithm Components

### 1. Image Processing Pipeline

**Input:** Photo of POS ticket
**Output:** Structured order data

**Process Flow:**
```
Raw Image → Preprocessing → OCR → Text Parsing → Structured Data
```

**Preprocessing Steps:**
1. **Grayscale Conversion** - Simplify image data
2. **Adaptive Thresholding** - Improve text contrast
3. **Noise Reduction** - Remove artifacts
4. **Contrast Enhancement** - Sharpen text boundaries
5. **Sharpening** - Improve edge definition

**OCR Configuration:**
- Engine: Tesseract with custom config
- Mode: Uniform block text detection
- Enhanced for thermal printer output

**Text Parsing Logic:**
```python
for each line in OCR_text:
    if matches_header_pattern:
        extract(ticket_id, table_number, server, timestamp)
    elif matches_item_pattern:
        extract(dish_name, quantity, modifiers)
        standardize_dish_name()
        add_to_order_items()
    elif matches_instruction_pattern:
        add_to_special_instructions()
```

**Dish Name Standardization:**
- Regex-based pattern matching
- Handles POS variations (abbreviations, spacing, etc.)
- Maps to canonical dish IDs

### 2. Recipe Database Architecture

**Data Structure:**
```
Recipe {
    id: string
    metadata: {name, station, cook_time, difficulty}
    equipment: [string]
    ingredients: [{name, quantity, location}]
    build_steps: [{step, action, time, temp, technique, visual_cues}]
    plating: {description, steps, presentation_notes}
    prep_components: {sub_recipes}
    timing_notes: string
    critical_notes: string
}
```

**Key Features:**
- Hierarchical organization (dishes → sub-recipes → steps)
- Location-based ingredient tracking
- Equipment requirements per dish
- Visual cues for quality control
- Common modification patterns

### 3. Order Triage Algorithm

**Objective:** Optimize cooking sequence to minimize wait times and prevent bottlenecks

**Priority Score Calculation:**

```
priority_score =
    (cook_time × 0.4) +           // Longer items fire first
    (ticket_age × 0.25) +         // Older tickets prioritized
    (difficulty × 0.15) +         // Complex dishes get buffer
    (station_clustering × 0.2) +  // Batch same-station work
    course_bonus                   // Apps before entrees
```

**Weighting Rationale:**
- **Cook Time (40%)**: Primary factor - longest items start first to coordinate finish times
- **Ticket Age (25%)**: Prevents customer wait time creep
- **Difficulty (15%)**: Harder dishes need mental space
- **Station Clustering (20%)**: Efficiency through batching
- **Course Bonus**: Fixed +10 for apps, +5 for entrees

**Station Clustering Algorithm:**
```python
def calculate_station_clustering(task):
    same_station_tasks = count_active_tasks_at_station(task.station)
    bonus = min(same_station_tasks × 0.5, 5.0)  # Cap at 5 points
    return bonus
```

Benefits:
- Reduces context switching
- Allows parallel prep
- Optimizes workspace usage

**Bottleneck Detection:**
```python
def detect_bottlenecks(station_workloads):
    bottlenecks = []
    for station, workload in station_workloads:
        if workload.total_time > 30 or workload.task_count > 5:
            bottlenecks.append(station)
    return bottlenecks
```

Thresholds:
- Time: > 30 minutes of queued work
- Volume: > 5 active tasks

### 4. Firing Sequence Algorithm

**Goal:** Coordinate multi-course timing so all dishes arrive together

**For Single Table:**

```python
def calculate_firing_sequence(table_items):
    # Separate by course
    apps = filter(items, course='appetizer')
    entrees = filter(items, course='entree')

    sequence = []

    # Apps fire immediately
    for app in apps:
        sequence.append((app, fire_time='ASAP'))

    # Find longest cooking entree
    longest = max(entrees, key=lambda x: x.cook_time)

    # Stagger other entrees relative to longest
    for entree in entrees:
        if entree == longest:
            fire_time = 0  # Fire now
        else:
            delay = longest.cook_time - entree.cook_time
            fire_time = delay

        sequence.append((entree, fire_time))

    return sequence
```

**Example:**
```
Table 42:
├─ Apps (Fire Now)
│  ├─ Dates (8 min) → Fire immediately
│  └─ Prawns (6 min) → Fire immediately
│
└─ Entrees (Fire on Call)
   ├─ Porterhouse (18 min) → Fire NOW (longest)
   ├─ Fish Curry (12 min) → Fire in 6 min
   └─ Charred Cabbage (10 min) → Fire in 8 min

Result: All entrees finish simultaneously at 18 min mark
```

### 5. Instruction Generation Algorithm

**Process:**

```
Task + Recipe → Complete Instructions

Components Generated:
1. Header (table, priority, timing)
2. Critical warnings
3. Modifiers (customer requests)
4. Equipment checklist
5. Ingredient checklist (with locations)
6. Sub-recipe instructions (if needed)
7. Step-by-step cooking
8. Plating instructions
9. Presentation notes
10. Common modification reference
```

**Priority Level Assignment:**
```python
if priority_score >= 15:
    level = "CRITICAL"
elif priority_score >= 10:
    level = "HIGH"
else:
    level = "NORMAL"
```

**Instruction Format:**
```
Each cooking step includes:
- Sequential numbering
- Action description
- Time duration
- Temperature setting
- Technique notes
- Visual cues (doneness indicators)
- Critical flags (must-not-skip steps)
```

### 6. Real-Time Triage Engine

**State Management:**
```python
class TriageEngine:
    active_tickets: List[POSTicket]
    cooking_tasks: List[CookingTask]
    completed_tasks: Set[task_id]

    def update():
        # Recalculate priorities
        # Detect bottlenecks
        # Generate recommendations
```

**Update Cycle:**
1. New ticket arrives → Parse → Create tasks
2. Calculate priorities for all active tasks
3. Check station workloads
4. Identify bottlenecks
5. Generate triage report
6. Update task list

**Workload Calculation:**
```python
for station in stations:
    workload = {
        'active_tasks': count_tasks(station),
        'total_time': sum(task.cook_time for task in tasks),
        'complexity': sum(difficulty_score(task) for task in tasks)
    }
```

## Algorithm Performance Characteristics

### Time Complexity

- **Image Processing**: O(n) where n = image pixels
- **OCR**: O(m) where m = text characters
- **Priority Calculation**: O(k) where k = active tasks
- **Sorting Tasks**: O(k log k)
- **Instruction Generation**: O(1) per task

**Overall**: O(n + m + k log k) - scales linearly with tickets

### Space Complexity

- **Recipe Database**: O(r) where r = number of recipes (constant)
- **Active Tasks**: O(k) where k = active tasks
- **Instructions**: O(k × i) where i = instruction size per task

### Scalability Considerations

**Current Capacity:**
- Recipe Database: Unlimited (JSON-based)
- Concurrent Tickets: 50+ tickets
- Active Tasks: 200+ tasks
- Response Time: < 2 seconds per ticket

**Optimization Opportunities:**
- Database caching for frequent recipes
- Parallel OCR processing
- Priority score caching with invalidation
- Incremental triage updates

## Edge Cases & Handling

### 1. Unknown Dishes
```python
if not recognized(dish_name):
    log_warning(dish_name)
    skip_task()  # Don't generate invalid instructions
```

### 2. Poor Image Quality
```python
if ocr_confidence < threshold:
    apply_additional_preprocessing()
    retry_ocr()
    if still_fails:
        return error_with_suggestions()
```

### 3. Station Overload
```python
if station_workload > critical_threshold:
    flag_as_bottleneck()
    suggest_task_redistribution()
    highlight_in_triage_report()
```

### 4. Conflicting Modifiers
```python
if has_conflicting_mods(task):
    flag_for_review()
    include_both_in_instructions()
    alert_expo()
```

## Integration Points

### Input Sources
- Direct image upload (web interface)
- File system watch (auto-process new images)
- API endpoint (integration with other systems)
- Manual ticket creation (testing/backup)

### Output Formats
- Web UI (formatted HTML)
- Plain text (kitchen printers)
- JSON (API responses)
- PDF (documentation/training)

### Extension Points
- Custom dish name mappings
- Restaurant-specific priority weights
- Additional recipe fields
- Custom triage rules
- Integration with KDS systems

## Data Flow Diagram

```
┌─────────────┐
│ POS Ticket  │
│   (Image)   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Preprocessing   │ ─► Enhance image quality
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│      OCR        │ ─► Extract text
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Text Parsing   │ ─► Structure data
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   POSTicket     │ ─► ticket_id, table, items[], mods[]
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Recipe Lookup   │ ─► Match items to full recipes
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Create Tasks   │ ─► One task per dish instance
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Calculate     │ ─► Priority scores for all tasks
│   Priorities    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sort & Triage  │ ─► Optimal cooking order
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Generate      │ ─► Complete instructions per task
│  Instructions   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Display      │ ─► Web UI / Print / API
└─────────────────┘
```

## Success Metrics

The algorithm is successful when it:

1. **Accurately parses** 95%+ of POS tickets
2. **Correctly prioritizes** tasks to minimize overall wait time
3. **Prevents bottlenecks** through early detection
4. **Provides complete** instructions (equipment, ingredients, steps, plating)
5. **Scales efficiently** to handle rush periods (50+ tickets)
6. **Maintains quality** through detailed technique guidance

## Future Enhancements

1. **Machine Learning OCR** - Train on restaurant-specific POS formats
2. **Dynamic Priority Weights** - Learn optimal weights from historical data
3. **Predictive Analytics** - Forecast busy periods, pre-fire items
4. **Voice Interface** - "Alexa, what's next for the grill?"
5. **Computer Vision** - Photo-based quality control for plating
6. **Real-time Updates** - Live ticket feed integration
7. **Mobile App** - Station-specific view for cooks
8. **Analytics Dashboard** - Track execution times, bottlenecks, trends

---

**Version:** 1.0.0
**Last Updated:** 2025-10-21
**Author:** Kitchen Information Landscape Team
