"""
Pattern analyzer for extracting style preferences from user choices.
Analyzes correlation between property values and user selections.
"""
import json
from typing import Dict, List, Tuple, Any
from collections import defaultdict


def analyze_territory_mapping(comparison_results: List[dict]) -> Dict[str, float]:
    """
    Analyze territory mapping phase results to find patterns.

    Returns confidence scores for each property-value combination based on
    correlation between property values and user choices.

    Supports both:
    - Legacy single-choice mode (choice field)
    - Multi-question mode (question_responses field)

    Args:
        comparison_results: List of comparison result dicts with:
            - option_a_styles: JSON string of styles
            - option_b_styles: JSON string of styles
            - choice: "a", "b", or "none" (legacy)
            - question_responses: JSON string of per-property answers (multi-question)

    Returns:
        Dict mapping "property_value" to confidence score (0.0 to 1.0)
    """
    # Track votes for each property-value combination
    property_votes = defaultdict(lambda: {"chosen": 0, "rejected": 0, "neutral": 0})

    for result in comparison_results:
        try:
            option_a = json.loads(result.get("option_a_styles", "{}"))
            option_b = json.loads(result.get("option_b_styles", "{}"))
        except json.JSONDecodeError:
            continue

        # Check for multi-question responses first
        question_responses = result.get("question_responses")
        if question_responses:
            try:
                responses = json.loads(question_responses) if isinstance(question_responses, str) else question_responses
                # Process each question response individually
                for response in responses:
                    prop = response.get("property")
                    choice = response.get("choice")

                    if not prop or choice == "none":
                        continue

                    # Get the values for this property
                    value_a = option_a.get(prop)
                    value_b = option_b.get(prop)

                    if choice == "a" and value_a is not None:
                        key = f"{prop}={value_a}"
                        property_votes[key]["chosen"] += 1
                        if value_b is not None:
                            key_b = f"{prop}={value_b}"
                            property_votes[key_b]["rejected"] += 1
                    elif choice == "b" and value_b is not None:
                        key = f"{prop}={value_b}"
                        property_votes[key]["chosen"] += 1
                        if value_a is not None:
                            key_a = f"{prop}={value_a}"
                            property_votes[key_a]["rejected"] += 1

            except (json.JSONDecodeError, TypeError):
                # Fall back to legacy mode
                pass
        else:
            # Legacy single-choice mode
            if result.get("choice") == "none":
                continue

            chosen_styles = option_a if result["choice"] == "a" else option_b
            rejected_styles = option_b if result["choice"] == "a" else option_a

            # Record votes for each property-value in chosen option
            for prop, value in chosen_styles.items():
                key = f"{prop}={value}"
                property_votes[key]["chosen"] += 1

            # Record rejections for each property-value in rejected option
            for prop, value in rejected_styles.items():
                key = f"{prop}={value}"
                property_votes[key]["rejected"] += 1

    # Calculate confidence scores
    confidence_scores = {}
    for key, votes in property_votes.items():
        total = votes["chosen"] + votes["rejected"]
        if total > 0:
            # Confidence = (chosen - rejected) / total, normalized to 0-1
            raw_score = (votes["chosen"] - votes["rejected"]) / total
            confidence_scores[key] = (raw_score + 1) / 2  # Normalize from [-1,1] to [0,1]

    return confidence_scores


def identify_high_signal_properties(
    confidence_scores: Dict[str, float],
    threshold: float = 0.65
) -> List[Tuple[str, str, float]]:
    """
    Identify properties with high confidence scores.

    Returns list of (property, value, confidence) tuples for properties
    that show strong user preference (above threshold).
    """
    high_signal = []
    for key, confidence in confidence_scores.items():
        if "=" in key:
            prop, value = key.split("=", 1)
            if confidence >= threshold or confidence <= (1 - threshold):
                high_signal.append((prop, value, confidence))

    # Sort by deviation from 0.5 (strongest preferences first)
    high_signal.sort(key=lambda x: abs(x[2] - 0.5), reverse=True)
    return high_signal


def identify_uncertain_properties(
    confidence_scores: Dict[str, float],
    min_threshold: float = 0.4,
    max_threshold: float = 0.6
) -> List[str]:
    """
    Identify properties where user preference is unclear.
    These should be tested in dimension isolation phase.
    """
    uncertain = set()
    for key, confidence in confidence_scores.items():
        if min_threshold <= confidence <= max_threshold:
            if "=" in key:
                prop = key.split("=")[0]
                uncertain.add(prop)

    return list(uncertain)


def calculate_session_confidence(
    comparison_results: List[dict],
    num_properties: int = 10
) -> float:
    """
    Calculate overall session confidence based on how many properties
    have strong signals vs uncertain signals.
    """
    if not comparison_results:
        return 0.0

    confidence_scores = analyze_territory_mapping(comparison_results)
    high_signal = identify_high_signal_properties(confidence_scores, threshold=0.65)
    uncertain = identify_uncertain_properties(confidence_scores)

    # Base confidence on proportion of high-signal properties
    high_signal_properties = set(item[0] for item in high_signal)
    uncertain_count = len(set(uncertain) - high_signal_properties)

    # Score: high signal properties give positive, uncertain gives negative
    score = len(high_signal_properties) / max(num_properties, 1)
    penalty = uncertain_count / max(num_properties, 1) * 0.3

    return max(0.0, min(1.0, score - penalty))


def should_transition_to_dimension_isolation(
    comparison_count: int,
    comparison_results: List[dict]
) -> bool:
    """
    Determine if session should transition from territory mapping
    to dimension isolation.

    Transition after 10-15 comparisons when sufficient patterns detected.
    """
    if comparison_count < 10:
        return False

    if comparison_count >= 15:
        return True

    # Check if we have strong signals for enough properties
    confidence_scores = analyze_territory_mapping(comparison_results)
    high_signal = identify_high_signal_properties(confidence_scores, threshold=0.6)

    # Transition if we have at least 5 high-signal properties
    return len(set(item[0] for item in high_signal)) >= 5


def get_property_to_test(
    comparison_results: List[dict],
    tested_properties: List[str]
) -> Tuple[str, Dict[str, Any]]:
    """
    Get the next property to test in dimension isolation.
    Prioritizes uncertain properties that haven't been tested.

    Returns (property_name, base_styles) for the test.
    """
    confidence_scores = analyze_territory_mapping(comparison_results)
    uncertain = identify_uncertain_properties(confidence_scores)

    # Filter out already tested properties
    untested_uncertain = [p for p in uncertain if p not in tested_properties]

    if untested_uncertain:
        property_to_test = untested_uncertain[0]
    elif uncertain:
        property_to_test = uncertain[0]
    else:
        # Fall back to any property
        all_props = set()
        for key in confidence_scores.keys():
            if "=" in key:
                all_props.add(key.split("=")[0])
        untested = [p for p in all_props if p not in tested_properties]
        property_to_test = untested[0] if untested else "border_radius"

    # Get base styles from the most common chosen styles
    base_styles = _get_base_styles_from_results(comparison_results)

    return property_to_test, base_styles


def _get_base_styles_from_results(comparison_results: List[dict]) -> Dict[str, Any]:
    """
    Extract base styles from comparison results.
    Uses the most commonly chosen values for each property.
    """
    property_votes = defaultdict(lambda: defaultdict(int))

    for result in comparison_results:
        if result.get("choice") == "none":
            continue

        try:
            chosen = "option_a_styles" if result["choice"] == "a" else "option_b_styles"
            styles = json.loads(result.get(chosen, "{}"))
        except json.JSONDecodeError:
            continue

        for prop, value in styles.items():
            property_votes[prop][str(value)] += 1

    # Get most common value for each property
    base_styles = {}
    for prop, votes in property_votes.items():
        if votes:
            most_common = max(votes.items(), key=lambda x: x[1])
            # Try to convert back to original type
            value = most_common[0]
            try:
                if value.isdigit():
                    value = int(value)
                elif value.replace(".", "").isdigit():
                    value = float(value)
                elif value.lower() == "true":
                    value = True
                elif value.lower() == "false":
                    value = False
            except (ValueError, AttributeError):
                pass
            base_styles[prop] = value

    return base_styles


def aggregate_property_preferences(comparison_results: List[dict]) -> Dict[str, Dict]:
    """
    Aggregate all property preferences into a structured format.

    Returns dict with property names as keys and preference data as values:
    {
        "property_name": {
            "preferred_values": ["value1", "value2"],
            "rejected_values": ["value3"],
            "confidence": 0.85
        }
    }
    """
    confidence_scores = analyze_territory_mapping(comparison_results)

    # Group by property
    property_data = defaultdict(lambda: {"preferred": [], "rejected": [], "scores": []})

    for key, confidence in confidence_scores.items():
        if "=" in key:
            prop, value = key.split("=", 1)
            property_data[prop]["scores"].append((value, confidence))

            if confidence >= 0.65:
                property_data[prop]["preferred"].append(value)
            elif confidence <= 0.35:
                property_data[prop]["rejected"].append(value)

    # Calculate overall confidence per property
    result = {}
    for prop, data in property_data.items():
        scores = [s[1] for s in data["scores"]]
        avg_deviation = sum(abs(s - 0.5) for s in scores) / len(scores) if scores else 0

        result[prop] = {
            "preferred_values": data["preferred"],
            "rejected_values": data["rejected"],
            "confidence": min(1.0, avg_deviation * 2)  # Scale deviation to confidence
        }

    return result
