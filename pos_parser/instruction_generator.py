"""
Instruction generator for complete cooking workflows
Generates step-by-step instructions with equipment, techniques, and plating
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass

from .recipe_database import RecipeDatabase, Recipe
from .triage_engine import CookingTask


@dataclass
class CompleteInstructions:
    """
    Complete cooking instructions for a dish
    """
    ticket_id: str
    table_number: str
    dish_name: str
    station: str
    total_time_minutes: int

    # Pre-service prep
    equipment_needed: List[str]
    ingredients_needed: List[Dict[str, str]]
    prep_components: Optional[Dict[str, Any]]

    # Cooking process
    build_steps: List[Dict[str, Any]]

    # Finishing
    plating_instructions: List[str]
    plating_description: str
    presentation_notes: str

    # Important info
    timing_notes: str
    critical_notes: Optional[str]
    modifiers: List[str]
    common_mods: List[str]

    # Quick reference
    difficulty: str
    priority_level: str  # "CRITICAL", "HIGH", "NORMAL"


class InstructionGenerator:
    """
    Generates complete, step-by-step cooking instructions
    Designed to help cooks execute dishes perfectly during busy service
    """

    def __init__(self, recipe_db: RecipeDatabase):
        """
        Initialize instruction generator

        Args:
            recipe_db: RecipeDatabase instance
        """
        self.recipe_db = recipe_db

    def generate_instructions(
        self,
        task: CookingTask,
        include_prep_components: bool = True
    ) -> Optional[CompleteInstructions]:
        """
        Generate complete instructions for a cooking task

        Args:
            task: CookingTask to generate instructions for
            include_prep_components: Include sub-recipe details

        Returns:
            CompleteInstructions object or None if recipe not found
        """
        recipe = self.recipe_db.get_recipe(task.dish_id)

        if not recipe:
            return None

        # Determine priority level based on priority score
        if task.priority_score >= 15:
            priority = "CRITICAL"
        elif task.priority_score >= 10:
            priority = "HIGH"
        else:
            priority = "NORMAL"

        return CompleteInstructions(
            ticket_id=task.ticket_id,
            table_number=task.table_number,
            dish_name=recipe.name,
            station=recipe.station,
            total_time_minutes=recipe.cook_time_minutes,
            equipment_needed=recipe.equipment,
            ingredients_needed=recipe.ingredients,
            prep_components=recipe.prep_components if include_prep_components else None,
            build_steps=recipe.build_steps,
            plating_instructions=recipe.plating['steps'],
            plating_description=recipe.plating['description'],
            presentation_notes=recipe.plating['presentation_notes'],
            timing_notes=recipe.timing_notes,
            critical_notes=recipe.critical_notes,
            modifiers=task.modifiers,
            common_mods=recipe.common_mods,
            difficulty=recipe.difficulty,
            priority_level=priority
        )

    def format_instructions_for_display(
        self,
        instructions: CompleteInstructions
    ) -> str:
        """
        Format instructions as readable text for kitchen display

        Args:
            instructions: CompleteInstructions object

        Returns:
            Formatted text ready for display
        """
        output = []

        # Header
        output.append("=" * 80)
        output.append(f"TABLE {instructions.table_number} - TICKET #{instructions.ticket_id}")
        output.append(f"{instructions.dish_name.upper()}")
        output.append(f"Station: {instructions.station.upper()} | "
                     f"Time: {instructions.total_time_minutes} min | "
                     f"Difficulty: {instructions.difficulty.upper()} | "
                     f"PRIORITY: {instructions.priority_level}")
        output.append("=" * 80)
        output.append("")

        # Critical notes (if any)
        if instructions.critical_notes:
            output.append("⚠️  CRITICAL NOTES ⚠️")
            output.append(instructions.critical_notes)
            output.append("")

        # Modifiers (if any)
        if instructions.modifiers:
            output.append("🔧 MODIFICATIONS FOR THIS ORDER:")
            for mod in instructions.modifiers:
                output.append(f"  • {mod}")
            output.append("")

        # Equipment
        output.append("🔨 EQUIPMENT NEEDED:")
        for equipment in instructions.equipment_needed:
            output.append(f"  □ {equipment}")
        output.append("")

        # Ingredients
        output.append("📦 INGREDIENTS & LOCATION:")
        for ingredient in instructions.ingredients_needed:
            name = ingredient['name']
            qty = ingredient.get('quantity', '')
            location = ingredient.get('location', '')
            output.append(f"  □ {name} ({qty}) - {location}")
        output.append("")

        # Prep components (sub-recipes)
        if instructions.prep_components:
            output.append("📝 PREP COMPONENTS (if not already done):")
            for comp_name, comp_data in instructions.prep_components.items():
                output.append(f"\n  {comp_data['name'].upper()}:")
                output.append(f"  Tools: {comp_data['tools']}")
                output.append(f"  Ingredients: {', '.join(comp_data['ingredients'])}")
                output.append("  Method:")
                for i, step in enumerate(comp_data['method'], 1):
                    output.append(f"    {i}. {step}")
                if 'storage' in comp_data:
                    output.append(f"  Storage: {comp_data['storage']}")
            output.append("")

        # Timing notes
        output.append("⏰ TIMING:")
        output.append(f"  {instructions.timing_notes}")
        output.append("")

        # Build steps
        output.append("👨‍🍳 COOKING STEPS:")
        for step in instructions.build_steps:
            step_num = step['step']
            action = step['action']
            time = step.get('time', '')
            temp = step.get('temp', '')
            technique = step.get('technique', '')
            visual_cue = step.get('visual_cue', '')
            critical = step.get('critical', False)

            marker = "⚠️" if critical else "  "
            output.append(f"{marker}STEP {step_num}: {action}")

            if time:
                output.append(f"     Time: {time}")
            if temp:
                output.append(f"     Heat: {temp}")
            if technique:
                output.append(f"     Technique: {technique}")
            if visual_cue:
                output.append(f"     Visual Cue: {visual_cue}")
            if 'note' in step:
                output.append(f"     Note: {step['note']}")

            output.append("")

        # Plating
        output.append("🍽️  PLATING:")
        output.append(f"  {instructions.plating_description}")
        output.append("")
        for i, plating_step in enumerate(instructions.plating_instructions, 1):
            output.append(f"  {i}. {plating_step}")
        output.append("")
        output.append(f"  💡 Presentation: {instructions.presentation_notes}")
        output.append("")

        # Common mods reference
        if instructions.common_mods:
            output.append("📋 COMMON MODIFICATIONS (for reference):")
            for mod in instructions.common_mods:
                output.append(f"  • {mod}")
            output.append("")

        output.append("=" * 80)
        output.append("")

        return "\n".join(output)

    def generate_quick_reference(
        self,
        task: CookingTask
    ) -> Optional[str]:
        """
        Generate quick reference card for a dish (abbreviated version)

        Args:
            task: CookingTask

        Returns:
            Quick reference text
        """
        recipe = self.recipe_db.get_recipe(task.dish_id)

        if not recipe:
            return None

        output = []
        output.append(f"╔══ {recipe.name.upper()} ══╗")
        output.append(f"Table: {task.table_number} | "
                     f"Time: {recipe.cook_time_minutes}min | "
                     f"Station: {recipe.station}")

        if task.modifiers:
            output.append(f"Mods: {', '.join(task.modifiers)}")

        output.append("\nKey Steps:")
        for i, step in enumerate(recipe.build_steps[:5], 1):  # First 5 steps
            output.append(f"{i}. {step['action']} ({step.get('time', 'varies')})")

        output.append(f"\n⏰ {recipe.timing_notes}")

        if recipe.critical_notes:
            output.append(f"⚠️  {recipe.critical_notes}")

        output.append("╚" + "═" * (len(recipe.name) + 8) + "╝")

        return "\n".join(output)

    def generate_station_summary(
        self,
        station: str,
        tasks: List[CookingTask]
    ) -> str:
        """
        Generate summary of all tasks for a specific station

        Args:
            station: Station name
            tasks: List of tasks for that station

        Returns:
            Formatted station summary
        """
        output = []
        output.append("=" * 80)
        output.append(f"{station.upper()} STATION - {len(tasks)} ACTIVE ORDERS")
        output.append("=" * 80)
        output.append("")

        # Get unique equipment needed for all tasks
        all_equipment = set()
        for task in tasks:
            recipe = self.recipe_db.get_recipe(task.dish_id)
            if recipe:
                all_equipment.update(recipe.equipment)

        output.append("🔨 EQUIPMENT NEEDED FOR ALL ORDERS:")
        for equipment in sorted(all_equipment):
            output.append(f"  □ {equipment}")
        output.append("")

        # List all tasks
        output.append("📋 TASKS (in priority order):")
        for i, task in enumerate(tasks, 1):
            recipe = self.recipe_db.get_recipe(task.dish_id)
            if recipe:
                mods = f" [{', '.join(task.modifiers)}]" if task.modifiers else ""
                output.append(
                    f"  {i}. Table {task.table_number}: "
                    f"{recipe.name} ({recipe.cook_time_minutes}min){mods}"
                )

        output.append("")
        output.append("=" * 80)

        return "\n".join(output)

    def generate_batch_instructions(
        self,
        tasks: List[CookingTask]
    ) -> List[CompleteInstructions]:
        """
        Generate instructions for multiple tasks

        Args:
            tasks: List of CookingTask objects

        Returns:
            List of CompleteInstructions
        """
        instructions_list = []

        for task in tasks:
            instructions = self.generate_instructions(task)
            if instructions:
                instructions_list.append(instructions)

        return instructions_list

    def export_instructions_to_dict(
        self,
        instructions: CompleteInstructions
    ) -> Dict[str, Any]:
        """
        Export instructions as dictionary (for JSON/API responses)

        Args:
            instructions: CompleteInstructions object

        Returns:
            Dictionary representation
        """
        return {
            'ticket_id': instructions.ticket_id,
            'table_number': instructions.table_number,
            'dish_name': instructions.dish_name,
            'station': instructions.station,
            'total_time_minutes': instructions.total_time_minutes,
            'equipment_needed': instructions.equipment_needed,
            'ingredients_needed': instructions.ingredients_needed,
            'prep_components': instructions.prep_components,
            'build_steps': instructions.build_steps,
            'plating': {
                'description': instructions.plating_description,
                'steps': instructions.plating_instructions,
                'presentation_notes': instructions.presentation_notes
            },
            'timing_notes': instructions.timing_notes,
            'critical_notes': instructions.critical_notes,
            'modifiers': instructions.modifiers,
            'common_mods': instructions.common_mods,
            'difficulty': instructions.difficulty,
            'priority_level': instructions.priority_level
        }
