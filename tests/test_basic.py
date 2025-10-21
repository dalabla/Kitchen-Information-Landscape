"""
Basic tests for POS Image Algorithm
Run with: pytest tests/test_basic.py
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pos_parser import (
    RecipeDatabase,
    TriageEngine,
    InstructionGenerator
)
from pos_parser.image_processor import POSTicket, OrderItem


@pytest.fixture
def recipe_db():
    """Fixture for recipe database"""
    return RecipeDatabase()


@pytest.fixture
def triage_engine(recipe_db):
    """Fixture for triage engine"""
    return TriageEngine(recipe_db)


@pytest.fixture
def instructor(recipe_db):
    """Fixture for instruction generator"""
    return InstructionGenerator(recipe_db)


@pytest.fixture
def sample_ticket():
    """Fixture for sample POS ticket"""
    return POSTicket(
        ticket_id="TEST001",
        table_number="42",
        timestamp=datetime.now(),
        server_name="Test Server",
        items=[
            OrderItem(
                dish_name="dates",
                quantity=1,
                modifiers=[],
                course="appetizer"
            ),
            OrderItem(
                dish_name="fish_curry",
                quantity=1,
                modifiers=["no onions"],
                course="entree"
            )
        ],
        special_instructions=[],
        ticket_time=datetime.now()
    )


class TestRecipeDatabase:
    """Test recipe database functionality"""

    def test_database_loads(self, recipe_db):
        """Test that database loads successfully"""
        assert len(recipe_db.get_all_recipes()) > 0

    def test_get_recipe(self, recipe_db):
        """Test retrieving a specific recipe"""
        recipe = recipe_db.get_recipe("dates")
        assert recipe is not None
        assert recipe.name == "Dates"
        assert len(recipe.equipment) > 0
        assert len(recipe.ingredients) > 0
        assert len(recipe.build_steps) > 0

    def test_get_nonexistent_recipe(self, recipe_db):
        """Test retrieving a non-existent recipe"""
        recipe = recipe_db.get_recipe("nonexistent_dish")
        assert recipe is None

    def test_get_equipment_list(self, recipe_db):
        """Test getting combined equipment list"""
        equipment = recipe_db.get_equipment_list(["dates", "fish_curry"])
        assert len(equipment) > 0
        assert isinstance(equipment, list)

    def test_get_stations_needed(self, recipe_db):
        """Test getting stations needed"""
        stations = recipe_db.get_stations_needed(["dates", "porterhouse"])
        assert "hot_apps" in stations
        assert "grill" in stations

    def test_difficulty_score(self, recipe_db):
        """Test difficulty scoring"""
        score_easy = recipe_db.get_difficulty_score("dates")
        score_hard = recipe_db.get_difficulty_score("porterhouse")
        assert score_hard > score_easy


class TestTriageEngine:
    """Test triage engine functionality"""

    def test_add_ticket(self, triage_engine, sample_ticket):
        """Test adding a ticket"""
        initial_count = len(triage_engine.cooking_tasks)
        triage_engine.add_ticket(sample_ticket)
        # Should create tasks for each item
        assert len(triage_engine.cooking_tasks) > initial_count

    def test_priority_calculation(self, triage_engine, sample_ticket):
        """Test priority score calculation"""
        triage_engine.add_ticket(sample_ticket)
        triage_engine.calculate_priority_scores()

        for task in triage_engine.cooking_tasks:
            assert task.priority_score > 0

    def test_prioritized_task_list(self, triage_engine, sample_ticket):
        """Test getting prioritized task list"""
        triage_engine.add_ticket(sample_ticket)
        tasks = triage_engine.get_prioritized_task_list()

        assert len(tasks) > 0
        # Check that tasks are sorted by priority
        for i in range(len(tasks) - 1):
            assert tasks[i].priority_score >= tasks[i + 1].priority_score

    def test_station_workloads(self, triage_engine, sample_ticket):
        """Test station workload calculation"""
        triage_engine.add_ticket(sample_ticket)
        workloads = triage_engine.get_station_workloads()

        assert len(workloads) > 0
        for station, workload in workloads.items():
            assert workload.task_count > 0
            assert workload.total_cook_time > 0

    def test_triage_report(self, triage_engine, sample_ticket):
        """Test triage report generation"""
        triage_engine.add_ticket(sample_ticket)
        report = triage_engine.get_triage_report()

        assert 'total_active_tasks' in report
        assert 'total_cook_time_minutes' in report
        assert 'critical_tasks' in report
        assert 'station_workloads' in report
        assert report['total_active_tasks'] > 0

    def test_firing_sequence(self, triage_engine, sample_ticket):
        """Test firing sequence generation"""
        triage_engine.add_ticket(sample_ticket)
        sequence = triage_engine.get_firing_sequence("42")

        assert len(sequence) > 0


class TestInstructionGenerator:
    """Test instruction generator functionality"""

    def test_generate_instructions(self, instructor, triage_engine, sample_ticket):
        """Test instruction generation"""
        triage_engine.add_ticket(sample_ticket)
        tasks = triage_engine.get_prioritized_task_list()

        assert len(tasks) > 0

        instructions = instructor.generate_instructions(tasks[0])
        assert instructions is not None
        assert instructions.dish_name
        assert len(instructions.equipment_needed) > 0
        assert len(instructions.ingredients_needed) > 0
        assert len(instructions.build_steps) > 0
        assert len(instructions.plating_instructions) > 0

    def test_format_instructions(self, instructor, triage_engine, sample_ticket):
        """Test instruction formatting"""
        triage_engine.add_ticket(sample_ticket)
        tasks = triage_engine.get_prioritized_task_list()
        instructions = instructor.generate_instructions(tasks[0])

        formatted = instructor.format_instructions_for_display(instructions)
        assert len(formatted) > 0
        assert "EQUIPMENT NEEDED" in formatted
        assert "COOKING STEPS" in formatted
        assert "PLATING" in formatted

    def test_quick_reference(self, instructor, triage_engine, sample_ticket):
        """Test quick reference generation"""
        triage_engine.add_ticket(sample_ticket)
        tasks = triage_engine.get_prioritized_task_list()

        quick_ref = instructor.generate_quick_reference(tasks[0])
        assert quick_ref is not None
        assert len(quick_ref) > 0

    def test_station_summary(self, instructor, triage_engine, sample_ticket):
        """Test station summary generation"""
        triage_engine.add_ticket(sample_ticket)
        workloads = triage_engine.get_station_workloads()

        for station, workload in workloads.items():
            summary = instructor.generate_station_summary(station, workload.active_tasks)
            assert summary is not None
            assert station.upper() in summary

    def test_export_to_dict(self, instructor, triage_engine, sample_ticket):
        """Test exporting instructions to dictionary"""
        triage_engine.add_ticket(sample_ticket)
        tasks = triage_engine.get_prioritized_task_list()
        instructions = instructor.generate_instructions(tasks[0])

        exported = instructor.export_instructions_to_dict(instructions)
        assert isinstance(exported, dict)
        assert 'dish_name' in exported
        assert 'equipment_needed' in exported
        assert 'build_steps' in exported
        assert 'plating' in exported


class TestImageProcessor:
    """Test image processor functionality"""

    def test_standardize_dish_name(self):
        """Test dish name standardization"""
        from pos_parser.image_processor import POSImageProcessor

        processor = POSImageProcessor()

        # Test various input formats
        assert processor.standardize_dish_name("dates w/ ciabatta") == "dates"
        assert processor.standardize_dish_name("Fish Curry") == "fish_curry"
        assert processor.standardize_dish_name("PRAWNS") == "prawns"
        assert processor.standardize_dish_name("charred cabbage") == "charred_cabbage"
        assert processor.standardize_dish_name("short rib") == "short_rib_radish_hummus"
        assert processor.standardize_dish_name("Porterhouse") == "porterhouse"

    def test_extract_modifiers(self):
        """Test modifier extraction"""
        from pos_parser.image_processor import POSImageProcessor

        processor = POSImageProcessor()

        modifiers = processor.extract_modifiers("dates - no bread, gluten free")
        assert len(modifiers) > 0

        modifiers = processor.extract_modifiers("steak medium rare")
        assert len(modifiers) > 0


class TestIntegration:
    """Integration tests for complete workflow"""

    def test_complete_workflow(self, recipe_db):
        """Test complete workflow from ticket to instructions"""
        # Create components
        triage = TriageEngine(recipe_db)
        instructor = InstructionGenerator(recipe_db)

        # Create ticket
        ticket = POSTicket(
            ticket_id="INT001",
            table_number="99",
            timestamp=datetime.now(),
            server_name="Integration Test",
            items=[
                OrderItem(
                    dish_name="porterhouse",
                    quantity=1,
                    modifiers=["medium rare"],
                    course="entree"
                )
            ],
            special_instructions=["VIP"],
            ticket_time=datetime.now()
        )

        # Process through system
        triage.add_ticket(ticket)
        tasks = triage.get_prioritized_task_list()
        assert len(tasks) > 0

        # Generate instructions
        instructions = instructor.generate_instructions(tasks[0])
        assert instructions is not None

        # Format
        formatted = instructor.format_instructions_for_display(instructions)
        assert "PORTERHOUSE" in formatted

        # Get report
        report = triage.get_triage_report()
        assert report['total_active_tasks'] == 1

    def test_multiple_tickets(self, recipe_db):
        """Test handling multiple tickets"""
        triage = TriageEngine(recipe_db)

        # Add multiple tickets
        for i in range(3):
            ticket = POSTicket(
                ticket_id=f"MULTI{i}",
                table_number=str(10 + i),
                timestamp=datetime.now(),
                server_name="Test",
                items=[
                    OrderItem(
                        dish_name="dates",
                        quantity=1,
                        modifiers=[],
                        course="appetizer"
                    )
                ],
                special_instructions=[],
                ticket_time=datetime.now()
            )
            triage.add_ticket(ticket)

        # Check that all tasks are tracked
        tasks = triage.get_prioritized_task_list()
        assert len(tasks) == 3

        report = triage.get_triage_report()
        assert report['total_active_tasks'] == 3


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
