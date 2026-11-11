# size_matcher.py - FIX THE PATH
import json
import os

class SizeMatcher:
    def __init__(self, size_chart_path=None):
        if size_chart_path is None:
            # Get the correct path relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            size_chart_path = os.path.join(current_dir, 'assets', 'shoe_size_chart.json')
        
        try:
            with open(size_chart_path, 'r') as f:
                self.size_chart = json.load(f)
            print(f"Size chart loaded successfully from: {size_chart_path}")
        except FileNotFoundError:
            print(f"Size chart not found at: {size_chart_path}")
            # Create empty chart as fallback
            self.size_chart = {"unisex": {"EU": {}}}
        except Exception as e:
            print(f"Error loading size chart: {e}")
            self.size_chart = {"unisex": {"EU": {}}}

    def recommend_size(self, foot_length_cm):
        """Return the closest matching EU size and its US/UK equivalents."""
        sizes = self.size_chart.get("unisex", {}).get("EU", {})
        if not sizes:
            return "Unavailable"

        ordered_sizes = sorted(sizes.items(), key=lambda item: float(item[0]))
        for eu_size, details in ordered_sizes:
            length = details.get("foot_length", {})
            if length.get("min", float("-inf")) <= foot_length_cm <= length.get("max", float("inf")):
                return f"EU {eu_size} (US {details.get('US', '-')}, UK {details.get('UK', '-')})"

        closest_size, closest_details = min(
            ordered_sizes,
            key=lambda item: min(
                abs(foot_length_cm - item[1]["foot_length"]["min"]),
                abs(foot_length_cm - item[1]["foot_length"]["max"]),
            ),
        )
        return (
            f"EU {closest_size} (US {closest_details.get('US', '-')}, "
            f"UK {closest_details.get('UK', '-')})"
        )