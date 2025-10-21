"""
Recipe database management
Loads and provides access to recipe data with full build instructions
"""

import json
from typing import Dict, List, Optional, Any
from pathlib import Path
from dataclasses import dataclass


@dataclass
class Recipe:
    """Complete recipe with all build information"""
    id: str
    name: str
    station: str
    cook_time_minutes: int
    difficulty: str
    equipment: List[str]
    ingredients: List[Dict[str, str]]
    build_steps: List[Dict[str, Any]]
    plating: Dict[str, Any]
    timing_notes: str
    common_mods: List[str]
    prep_components: Optional[Dict[str, Any]] = None
    critical_notes: Optional[str] = None


class RecipeDatabase:
    """
    Manages recipe data and provides lookup functionality
    """

    def __init__(self, database_path: Optional[str] = None):
        """
        Initialize recipe database

        Args:
            database_path: Path to recipe JSON file. If None, uses default.
        """
        if database_path is None:
            # Default to recipes directory relative to this file
            base_path = Path(__file__).parent.parent
            database_path = base_path / 'recipes' / 'recipe_database.json'

        self.database_path = Path(database_path)
        self.recipes: Dict[str, Recipe] = {}
        self.priority_factors: Dict[str, float] = {}
        self.station_assignments: Dict[str, List[str]] = {}

        self._load_database()

    def _load_database(self):
        """Load recipe database from JSON file"""
        try:
            with open(self.database_path, 'r') as f:
                data = json.load(f)

            # Load recipes
            for dish_id, recipe_data in data.get('dishes', {}).items():
                self.recipes[dish_id] = Recipe(
                    id=recipe_data['id'],
                    name=recipe_data['name'],
                    station=recipe_data['station'],
                    cook_time_minutes=recipe_data['cook_time_minutes'],
                    difficulty=recipe_data['difficulty'],
                    equipment=recipe_data['equipment'],
                    ingredients=recipe_data['ingredients'],
                    build_steps=recipe_data['build_steps'],
                    plating=recipe_data['plating'],
                    timing_notes=recipe_data['timing_notes'],
                    common_mods=recipe_data['common_mods'],
                    prep_components=recipe_data.get('prep_components'),
                    critical_notes=recipe_data.get('critical_notes')
                )

            # Load priority factors
            self.priority_factors = data.get('priority_factors', {})

            # Load station assignments
            self.station_assignments = data.get('station_assignments', {})

        except FileNotFoundError:
            raise FileNotFoundError(
                f"Recipe database not found at {self.database_path}"
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in recipe database: {e}")

    def get_recipe(self, dish_id: str) -> Optional[Recipe]:
        """
        Get recipe by dish ID

        Args:
            dish_id: Standardized dish identifier

        Returns:
            Recipe object or None if not found
        """
        return self.recipes.get(dish_id)

    def get_all_recipes(self) -> Dict[str, Recipe]:
        """Get all recipes"""
        return self.recipes

    def get_recipes_by_station(self, station: str) -> List[Recipe]:
        """
        Get all recipes for a specific station

        Args:
            station: Station name (e.g., 'hot_apps', 'grill')

        Returns:
            List of recipes for that station
        """
        return [
            recipe for recipe in self.recipes.values()
            if recipe.station == station
        ]

    def get_equipment_list(self, dish_ids: List[str]) -> List[str]:
        """
        Get combined equipment list for multiple dishes

        Args:
            dish_ids: List of dish IDs

        Returns:
            Deduplicated list of required equipment
        """
        equipment_set = set()

        for dish_id in dish_ids:
            recipe = self.get_recipe(dish_id)
            if recipe:
                equipment_set.update(recipe.equipment)

        return sorted(list(equipment_set))

    def get_stations_needed(self, dish_ids: List[str]) -> List[str]:
        """
        Get list of stations needed for dishes

        Args:
            dish_ids: List of dish IDs

        Returns:
            List of station names
        """
        stations = set()

        for dish_id in dish_ids:
            recipe = self.get_recipe(dish_id)
            if recipe:
                stations.add(recipe.station)

        return sorted(list(stations))

    def get_total_cook_time(self, dish_ids: List[str]) -> int:
        """
        Get total cook time if all dishes cooked sequentially

        Args:
            dish_ids: List of dish IDs

        Returns:
            Total minutes
        """
        total = 0

        for dish_id in dish_ids:
            recipe = self.get_recipe(dish_id)
            if recipe:
                total += recipe.cook_time_minutes

        return total

    def get_difficulty_score(self, dish_id: str) -> int:
        """
        Get numeric difficulty score for a dish

        Args:
            dish_id: Dish ID

        Returns:
            Difficulty score (1-5)
        """
        recipe = self.get_recipe(dish_id)
        if not recipe:
            return 0

        difficulty_map = {
            'easy': 1,
            'medium': 2,
            'medium-hard': 3,
            'hard': 4,
            'very-hard': 5
        }

        return difficulty_map.get(recipe.difficulty, 2)

    def search_recipes(self, query: str) -> List[Recipe]:
        """
        Search recipes by name or ingredients

        Args:
            query: Search query

        Returns:
            List of matching recipes
        """
        query_lower = query.lower()
        results = []

        for recipe in self.recipes.values():
            # Check name
            if query_lower in recipe.name.lower():
                results.append(recipe)
                continue

            # Check ingredients
            for ingredient in recipe.ingredients:
                if query_lower in ingredient.get('name', '').lower():
                    results.append(recipe)
                    break

        return results

    def get_prep_component(self, dish_id: str, component_name: str) -> Optional[Dict[str, Any]]:
        """
        Get specific prep component (sub-recipe) for a dish

        Args:
            dish_id: Dish ID
            component_name: Name of prep component

        Returns:
            Prep component data or None
        """
        recipe = self.get_recipe(dish_id)
        if not recipe or not recipe.prep_components:
            return None

        return recipe.prep_components.get(component_name)

    def reload_database(self):
        """Reload database from file (useful for updates)"""
        self.recipes.clear()
        self.priority_factors.clear()
        self.station_assignments.clear()
        self._load_database()
