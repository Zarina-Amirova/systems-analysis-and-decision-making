import json
import numpy as np
from typing import List, Tuple, Dict, Any

def parse_json_config(json_str: str) -> Dict[str, List[Dict[str, Any]]]:
    return json.loads(json_str)

def membership_function(x: float, points: List[Tuple[float, float]]) -> float:
    if not points:
        return 0.0
    
    sorted_pts = sorted(points, key=lambda p: p[0])
    x_vals = np.array([p[0] for p in sorted_pts])
    mu_vals = np.array([p[1] for p in sorted_pts])
    
    if x <= x_vals[0]:
        return mu_vals[0]
    if x >= x_vals[-1]:
        return mu_vals[-1]
    
    idx = np.searchsorted(x_vals, x) - 1
    if idx >= len(x_vals) - 1:
        return mu_vals[-1]
    
    x1, x2 = x_vals[idx], x_vals[idx + 1]
    mu1, mu2 = mu_vals[idx], mu_vals[idx + 1]
    
    if x2 == x1:
        return (mu1 + mu2) / 2
    return mu1 + (mu2 - mu1) * (x - x1) / (x2 - x1)

def fuzzify_input(temp: float, temp_terms: List[Dict[str, Any]]) -> Dict[str, float]:
    degrees = {}
    for term in temp_terms:
        degrees[term['id']] = membership_function(temp, term['points'])
    return degrees

def get_universe_bounds(terms: List[Dict[str, Any]]) -> Tuple[float, float]:
    all_x = []
    for term in terms:
        all_x.extend([p[0] for p in term['points']])
    return min(all_x), max(all_x)

def infer_rules(temp_degrees: Dict[str, float], rules: List[List[str]], 
                heat_terms: List[Dict[str, Any]]) -> np.ndarray:
    min_u, max_u = get_universe_bounds(heat_terms)
    u = np.linspace(min_u, max_u, 1001)
    agg_mu = np.zeros_like(u)
    
    for rule in rules:
        if len(rule) != 2:
            continue
        antec, conseq = rule
        alpha = temp_degrees.get(antec, 0.0)
        
        if alpha == 0:
            continue
            
        output_term = next((t for t in heat_terms if t['id'] == conseq), None)
        if not output_term:
            continue
            
        term_mu = np.array([membership_function(val, output_term['points']) for val in u])
        clipped_mu = np.minimum(alpha, term_mu)
        agg_mu = np.maximum(agg_mu, clipped_mu)
    
    return agg_mu

def defuzzify_center_of_area(mu_values: np.ndarray, u_values: np.ndarray) -> float:
    nonzero = mu_values > 1e-10
    if not np.any(nonzero):
        return 0.0
    
    numerator = np.trapz(u_values[nonzero] * mu_values[nonzero], u_values[nonzero])
    denominator = np.trapz(mu_values[nonzero], u_values[nonzero])
    
    return numerator / denominator if denominator > 0 else 0.0

def main(temp_config: str, heat_config: str, rules_config: str, current_temp: float) -> float:
  
    temp_data = parse_json_config(temp_config)
    heat_data = parse_json_config(heat_config)
    rules_data = json.loads(rules_config)
    
    temperature_sets = temp_data['температура']
    heating_sets = heat_data['нагрев']
    
    input_fuzzy = fuzzify_input(current_temp, temperature_sets)
    aggregated_output = infer_rules(input_fuzzy, rules_data, heating_sets)
    min_bound, max_bound = get_universe_bounds(heating_sets)
    control_grid = np.linspace(min_bound, max_bound, 1001)
    
    optimal_heating = defuzzify_center_of_area(aggregated_output, control_grid)
    return float(optimal_heating)

if __name__ == "__main__":
    with open('ivinput.json', 'r', encoding='utf-8') as f:
        temp_json = f.read()
    with open('lvoutput.json', 'r', encoding='utf-8') as f:
        heat_json = f.read()
    with open('rules.json', 'r', encoding='utf-8') as f:
        rules_json = f.read()
    
    result = main(temp_json, heat_json, rules_json, 19.0)
    print(f"Оптимальный нагрев: {result:.3f}")
