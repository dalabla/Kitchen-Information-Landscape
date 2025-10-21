#!/usr/bin/env python3
"""
Example usage of the POS Image Algorithm
Demonstrates basic workflow from image to instructions
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pos_parser import (
    POSImageProcessor,
    RecipeDatabase,
    TriageEngine,
    InstructionGenerator
)


def demo_with_manual_ticket():
    """
    Demo without actual image - creates a manual ticket
    Useful for testing the system without OCR dependencies
    """
    from pos_parser.image_processor import POSTicket, OrderItem
    from datetime import datetime

    print("=" * 80)
    print("POS IMAGE ALGORITHM - DEMO MODE")
    print("=" * 80)
    print()

    # Initialize system
    print("🔧 Initializing system...")
    recipe_db = RecipeDatabase()
    triage_engine = TriageEngine(recipe_db)
    instructor = InstructionGenerator(recipe_db)
    print("✅ System ready!")
    print()

    # Create sample tickets
    print("📋 Creating sample tickets...")

    # Table 5 - 2 appetizers, 2 entrees
    ticket1 = POSTicket(
        ticket_id="001",
        table_number="5",
        timestamp=datetime.now(),
        server_name="Alex",
        items=[
            OrderItem(
                dish_name="dates",
                quantity=1,
                modifiers=["no bread", "gluten free"],
                course="appetizer"
            ),
            OrderItem(
                dish_name="prawns",
                quantity=1,
                modifiers=[],
                course="appetizer"
            ),
            OrderItem(
                dish_name="porterhouse",
                quantity=1,
                modifiers=["medium rare"],
                course="entree"
            ),
            OrderItem(
                dish_name="fish_curry",
                quantity=1,
                modifiers=["mild spice"],
                course="entree"
            )
        ],
        special_instructions=["VIP table", "birthday - porterhouse"],
        ticket_time=datetime.now()
    )

    # Table 12 - Quick order
    ticket2 = POSTicket(
        ticket_id="002",
        table_number="12",
        timestamp=datetime.now(),
        server_name="Jordan",
        items=[
            OrderItem(
                dish_name="charred_cabbage",
                quantity=2,
                modifiers=["vegan"],
                course="entree"
            )
        ],
        special_instructions=[],
        ticket_time=datetime.now()
    )

    # Add tickets to triage
    print("➕ Adding tickets to triage engine...")
    triage_engine.add_ticket(ticket1)
    triage_engine.add_ticket(ticket2)
    print(f"✅ Processed {len([ticket1, ticket2])} tickets")
    print()

    # Show triage report
    print("=" * 80)
    print("TRIAGE REPORT")
    print("=" * 80)
    report = triage_engine.get_triage_report()

    print(f"\n📊 Overall Status:")
    print(f"   Active Tasks: {report['total_active_tasks']}")
    print(f"   Total Cook Time: {report['total_cook_time_minutes']} minutes")

    if report['bottleneck_stations']:
        print(f"   ⚠️  Bottleneck Stations: {', '.join(report['bottleneck_stations'])}")

    print(f"\n🏪 Station Workloads:")
    for station, workload in report['station_workloads'].items():
        print(f"   {station.upper()}: {workload.task_count} tasks, "
              f"{workload.total_cook_time} min total")

    print(f"\n🔥 Critical Tasks (Top Priority):")
    for i, task in enumerate(report['critical_tasks'], 1):
        print(f"   {i}. Table {task.table_number}: {task.dish_name} "
              f"(Priority: {task.priority_score:.1f})")

    # Show firing sequence for table
    print("\n" + "=" * 80)
    print("FIRING SEQUENCE - TABLE 5")
    print("=" * 80)
    sequence = triage_engine.get_firing_sequence("5")
    for dish, timing, cook_time in sequence:
        if cook_time == 0:
            print(f"\n{dish}")
        else:
            print(f"  └─ {dish}")
            print(f"     {timing} ({cook_time} min)")

    # Generate detailed instructions for highest priority task
    print("\n" + "=" * 80)
    print("DETAILED INSTRUCTIONS - HIGHEST PRIORITY")
    print("=" * 80)

    prioritized_tasks = triage_engine.get_prioritized_task_list()
    if prioritized_tasks:
        top_task = prioritized_tasks[0]
        instructions = instructor.generate_instructions(top_task)

        if instructions:
            formatted = instructor.format_instructions_for_display(instructions)
            print(formatted)

    # Show quick reference cards for all tasks
    print("\n" + "=" * 80)
    print("QUICK REFERENCE CARDS")
    print("=" * 80)

    for i, task in enumerate(prioritized_tasks[:5], 1):  # Top 5
        print(f"\n--- CARD {i} ---")
        quick_ref = instructor.generate_quick_reference(task)
        if quick_ref:
            print(quick_ref)

    # Station summary
    print("\n" + "=" * 80)
    print("STATION SUMMARIES")
    print("=" * 80)

    workloads = triage_engine.get_station_workloads()
    for station, workload in workloads.items():
        summary = instructor.generate_station_summary(station, workload.active_tasks)
        print(f"\n{summary}")


def process_pos_image(image_path: str):
    """
    Process an actual POS image

    Args:
        image_path: Path to POS image file
    """
    print(f"Processing POS image: {image_path}")
    print("=" * 80)

    # Initialize
    recipe_db = RecipeDatabase()
    image_processor = POSImageProcessor()
    triage_engine = TriageEngine(recipe_db)
    instructor = InstructionGenerator(recipe_db)

    # Process image
    print("🔍 Reading and processing image...")
    try:
        ticket = image_processor.process_image(image_path)
        print(f"✅ Successfully parsed ticket #{ticket.ticket_id}")
        print(f"   Table: {ticket.table_number}")
        print(f"   Items: {len(ticket.items)}")
        print()

        # Show parsed items
        print("📋 Parsed Items:")
        for i, item in enumerate(ticket.items, 1):
            mods = f" [{', '.join(item.modifiers)}]" if item.modifiers else ""
            print(f"   {i}. {item.quantity}x {item.dish_name}{mods}")

        if ticket.special_instructions:
            print("\n⚠️  Special Instructions:")
            for instruction in ticket.special_instructions:
                print(f"   - {instruction}")

        # Add to triage
        triage_engine.add_ticket(ticket)

        # Generate instructions
        print("\n" + "=" * 80)
        print("COMPLETE INSTRUCTIONS")
        print("=" * 80 + "\n")

        tasks = triage_engine.get_prioritized_task_list()
        for task in tasks:
            instructions = instructor.generate_instructions(task)
            if instructions:
                formatted = instructor.format_instructions_for_display(instructions)
                print(formatted)

    except Exception as e:
        print(f"❌ Error processing image: {e}")
        print("\nNote: Make sure Tesseract OCR is installed.")
        print("      Run 'tesseract --version' to check.")
        return


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        # Process actual image
        image_path = sys.argv[1]
        if not Path(image_path).exists():
            print(f"Error: File not found: {image_path}")
            sys.exit(1)
        process_pos_image(image_path)
    else:
        # Run demo mode
        print("No image provided - running demo mode with sample data")
        print("(To process an image, run: python example_usage.py <image_path>)")
        print()
        demo_with_manual_ticket()


if __name__ == "__main__":
    main()
