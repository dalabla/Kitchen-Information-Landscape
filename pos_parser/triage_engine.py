"""
Triage engine for prioritizing orders during busy service
Helps get cooks out of the weeds by intelligently ordering tasks
"""

from typing import List, Dict, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from collections import defaultdict

from .image_processor import POSTicket, OrderItem
from .recipe_database import RecipeDatabase, Recipe


@dataclass
class CookingTask:
    """Represents a single cooking task with priority"""
    ticket_id: str
    table_number: str
    dish_id: str
    dish_name: str
    quantity: int
    modifiers: List[str]
    station: str
    cook_time_minutes: int
    difficulty: str
    course: str
    ticket_time: datetime
    priority_score: float = 0.0
    fire_time: str = "ASAP"  # ASAP, on_call, timed
    estimated_completion: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)  # Other tasks that must complete first


@dataclass
class StationWorkload:
    """Tracks workload for a specific station"""
    station: str
    active_tasks: List[CookingTask]
    total_cook_time: int  # minutes
    task_count: int
    complexity_score: float


class TriageEngine:
    """
    Intelligent order triage system for busy service
    Prioritizes tasks to help kitchen get out of the weeds
    """

    def __init__(self, recipe_db: RecipeDatabase):
        """
        Initialize triage engine

        Args:
            recipe_db: RecipeDatabase instance
        """
        self.recipe_db = recipe_db
        self.active_tickets: List[POSTicket] = []
        self.cooking_tasks: List[CookingTask] = []
        self.completed_tasks: Set[str] = set()

    def add_ticket(self, ticket: POSTicket):
        """
        Add a new ticket to the triage system

        Args:
            ticket: POSTicket from image processor
        """
        self.active_tickets.append(ticket)
        self._create_tasks_from_ticket(ticket)

    def add_multiple_tickets(self, tickets: List[POSTicket]):
        """Add multiple tickets at once"""
        for ticket in tickets:
            self.add_ticket(ticket)

    def _create_tasks_from_ticket(self, ticket: POSTicket):
        """
        Convert ticket items into cooking tasks

        Args:
            ticket: POSTicket object
        """
        for item in ticket.items:
            recipe = self.recipe_db.get_recipe(item.dish_name)

            if not recipe:
                print(f"Warning: Recipe not found for {item.dish_name}")
                continue

            # Create task for each quantity
            for qty in range(item.quantity):
                task = CookingTask(
                    ticket_id=ticket.ticket_id,
                    table_number=ticket.table_number,
                    dish_id=item.dish_name,
                    dish_name=recipe.name,
                    quantity=1,  # Split into individual tasks
                    modifiers=item.modifiers,
                    station=recipe.station,
                    cook_time_minutes=recipe.cook_time_minutes,
                    difficulty=recipe.difficulty,
                    course=item.course,
                    ticket_time=ticket.ticket_time
                )

                self.cooking_tasks.append(task)

    def calculate_priority_scores(self):
        """
        Calculate priority scores for all active tasks
        Uses multiple factors to determine optimal cooking order
        """
        now = datetime.now()
        factors = self.recipe_db.priority_factors

        for task in self.cooking_tasks:
            if self._is_task_complete(task):
                continue

            # Factor 1: Cook time (longer items fire first)
            cook_time_score = task.cook_time_minutes * factors.get('cook_time_weight', 0.4)

            # Factor 2: Ticket age (older tickets get priority)
            ticket_age_minutes = (now - task.ticket_time).total_seconds() / 60
            time_weight = factors.get('ticket_time_weight', 0.25)
            ticket_age_score = min(ticket_age_minutes * time_weight, 20)  # Cap at 20

            # Factor 3: Difficulty (harder dishes get more time)
            difficulty_map = {'easy': 1, 'medium': 2, 'medium-hard': 3, 'hard': 4}
            difficulty_value = difficulty_map.get(task.difficulty, 2)
            difficulty_score = difficulty_value * factors.get('difficulty_weight', 0.15)

            # Factor 4: Station clustering (group same-station tasks)
            station_score = self._calculate_station_clustering_score(task)
            station_score *= factors.get('station_clustering', 0.2)

            # Factor 5: Course ordering (apps before entrees)
            course_score = 10 if task.course == 'appetizer' else 5

            # Total priority score
            task.priority_score = (
                cook_time_score +
                ticket_age_score +
                difficulty_score +
                station_score +
                course_score
            )

            # Estimate completion time
            task.estimated_completion = now + timedelta(minutes=task.cook_time_minutes)

    def _calculate_station_clustering_score(self, task: CookingTask) -> float:
        """
        Calculate bonus score for station clustering
        Rewards tasks that can be batched at same station
        """
        same_station_count = sum(
            1 for t in self.cooking_tasks
            if t.station == task.station and not self._is_task_complete(t)
        )

        return min(same_station_count * 0.5, 5.0)  # Cap at 5 points

    def get_prioritized_task_list(self) -> List[CookingTask]:
        """
        Get tasks sorted by priority

        Returns:
            List of CookingTask objects sorted by priority (highest first)
        """
        self.calculate_priority_scores()

        # Filter out completed tasks
        active_tasks = [
            task for task in self.cooking_tasks
            if not self._is_task_complete(task)
        ]

        # Sort by priority (descending) and then by course (apps first)
        sorted_tasks = sorted(
            active_tasks,
            key=lambda t: (-t.priority_score, t.course == 'entree')
        )

        return sorted_tasks

    def get_station_workloads(self) -> Dict[str, StationWorkload]:
        """
        Get current workload breakdown by station

        Returns:
            Dictionary mapping station name to StationWorkload
        """
        workloads = {}
        station_tasks = defaultdict(list)

        # Group tasks by station
        for task in self.cooking_tasks:
            if not self._is_task_complete(task):
                station_tasks[task.station].append(task)

        # Calculate workload for each station
        for station, tasks in station_tasks.items():
            total_time = sum(t.cook_time_minutes for t in tasks)
            complexity = sum(
                self.recipe_db.get_difficulty_score(t.dish_id)
                for t in tasks
            )

            workloads[station] = StationWorkload(
                station=station,
                active_tasks=tasks,
                total_cook_time=total_time,
                task_count=len(tasks),
                complexity_score=complexity
            )

        return workloads

    def get_next_task_for_station(self, station: str) -> Optional[CookingTask]:
        """
        Get the next highest priority task for a specific station

        Args:
            station: Station name

        Returns:
            Next CookingTask for that station or None
        """
        station_tasks = [
            task for task in self.get_prioritized_task_list()
            if task.station == station
        ]

        return station_tasks[0] if station_tasks else None

    def get_triage_report(self) -> Dict[str, any]:
        """
        Generate comprehensive triage report

        Returns:
            Dictionary with triage information
        """
        prioritized = self.get_prioritized_task_list()
        workloads = self.get_station_workloads()

        # Identify critical tasks (oldest, hardest, or bottlenecks)
        critical_tasks = [
            task for task in prioritized[:5]  # Top 5 priorities
        ]

        # Calculate total remaining work
        total_time = sum(t.cook_time_minutes for t in prioritized)

        # Identify potential bottlenecks
        bottlenecks = [
            station for station, workload in workloads.items()
            if workload.total_cook_time > 30 or workload.task_count > 5
        ]

        return {
            'total_active_tasks': len(prioritized),
            'total_cook_time_minutes': total_time,
            'critical_tasks': critical_tasks,
            'station_workloads': workloads,
            'bottleneck_stations': bottlenecks,
            'prioritized_tasks': prioritized
        }

    def get_firing_sequence(self, table_number: str) -> List[Tuple[str, str, int]]:
        """
        Get optimal firing sequence for a specific table

        Args:
            table_number: Table number

        Returns:
            List of tuples: (dish_name, fire_time, minutes_before_service)
        """
        table_tasks = [
            task for task in self.cooking_tasks
            if task.table_number == table_number and not self._is_task_complete(task)
        ]

        if not table_tasks:
            return []

        # Group by course
        apps = [t for t in table_tasks if t.course == 'appetizer']
        entrees = [t for t in table_tasks if t.course == 'entree']

        sequence = []

        # Apps fire first
        if apps:
            sequence.append(("APPETIZERS", "Fire Now", 0))
            for app in apps:
                sequence.append((app.dish_name, "ASAP", app.cook_time_minutes))

        # Entrees fire on call or after apps
        if entrees:
            # Find longest cooking entree
            longest_entree = max(entrees, key=lambda t: t.cook_time_minutes)

            sequence.append(("ENTREES", "Fire on call", 0))
            sequence.append((
                longest_entree.dish_name + " (FIRE FIRST)",
                "Fire now - longest cook",
                longest_entree.cook_time_minutes
            ))

            for entree in entrees:
                if entree != longest_entree:
                    time_diff = longest_entree.cook_time_minutes - entree.cook_time_minutes
                    sequence.append((
                        entree.dish_name,
                        f"Fire {time_diff} min after longest",
                        entree.cook_time_minutes
                    ))

        return sequence

    def mark_task_complete(self, task: CookingTask):
        """Mark a task as completed"""
        task_key = f"{task.ticket_id}-{task.dish_id}"
        self.completed_tasks.add(task_key)

    def _is_task_complete(self, task: CookingTask) -> bool:
        """Check if task is completed"""
        task_key = f"{task.ticket_id}-{task.dish_id}"
        return task_key in self.completed_tasks

    def clear_completed_tasks(self):
        """Remove completed tasks from active list"""
        self.cooking_tasks = [
            task for task in self.cooking_tasks
            if not self._is_task_complete(task)
        ]
