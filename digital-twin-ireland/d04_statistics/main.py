"""
Module d04_statistics: Grid performance metrics and infrastructure statistics
SSI v4.0.2 Digital Twin - Ireland
"""

import os
import json
import hashlib
from datetime import datetime
from typing import Dict, List, Any

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(MODULE_DIR)


def load_config() -> Dict[str, Any]:
    """Load configuration from config.json"""
    config_path = os.path.join(MODULE_DIR, 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def get_irish_counties() -> List[str]:
    """Return list of 26 Irish counties"""
    return [
        "Carlow", "Cavan", "Clare", "Cork", "Donegal", "Dublin",
        "Dun Laoghaire-Rathdown", "Fingal", "Galway", "Kerry",
        "Kildare", "Kilkenny", "Laois", "Leitrim", "Limerick",
        "Longford", "Louth", "Mayo", "Meath", "Monaghan",
        "Offaly", "Roscommon", "Sligo", "South Dublin", "Tipperary",
        "Waterford", "Westmeath", "Wexford", "Wicklow"
    ]


def get_deterministic_hash(county_name: str) -> str:
    """Generate deterministic hash using MD5 for reproducibility"""
    return hashlib.md5(county_name.encode()).hexdigest()


def classify_county_type(county_name: str) -> str:
    """Classify counties as urban, suburban, or rural"""
    urban_counties = {
        "Dublin", "Cork", "Galway", "Limerick", "Waterford",
        "Dun Laoghaire-Rathdown", "Fingal", "South Dublin"
    }

    suburban_counties = {
        "Kildare", "Meath", "Louth", "Wicklow", "Carlow",
        "Kilkenny", "Wexford", "Tipperary", "Laois", "Offaly",
        "Westmeath", "Longford"
    }

    if county_name in urban_counties:
        return "urban"
    elif county_name in suburban_counties:
        return "suburban"
    else:
        return "rural"


def generate_transformer_age(county_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate transformer age statistics for county"""

    county_type = classify_county_type(county_name)
    config_stats = config["statistics"]["transformer_age"]

    # Determine average based on county type
    if county_type == "urban":
        avg_age = config_stats["dublin_average_years"]
        variance = 4  # Urban networks are more uniform
    elif county_type == "suburban":
        avg_age = int((config_stats["dublin_average_years"] + config_stats["national_average_years"]) / 2)
        variance = 6
    else:  # rural
        avg_age = config_stats["rural_average_years"]
        variance = 8  # Greater variance in rural networks

    # Use deterministic hash to generate consistent variation
    county_hash = get_deterministic_hash(county_name)
    hash_value = int(county_hash[:8], 16)
    variation = ((hash_value % 100) / 100.0) * variance - (variance / 2)
    actual_avg = max(15, int(avg_age + variation))

    return {
        "average_age_years": actual_avg,
        "minimum_age_years": max(5, actual_avg - 15),
        "maximum_age_years": min(config_stats["expected_lifespan_years"], actual_avg + 15),
        "expected_lifespan_years": config_stats["expected_lifespan_years"],
        "modernization_rate": round((1 - (actual_avg / config_stats["expected_lifespan_years"])) * 100, 1),
        "county_type": county_type
    }


def generate_failure_rate(county_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate failure rate statistics for county"""

    county_type = classify_county_type(county_name)
    failure_config = config["statistics"]["failure_rate"]

    # Failure rates higher in rural areas (aging infrastructure, weather exposure)
    if county_type == "urban":
        base_rate = failure_config["national_average"] - 0.01
    elif county_type == "suburban":
        base_rate = failure_config["national_average"]
    else:  # rural
        base_rate = failure_config["national_average"] + 0.015

    # Add deterministic variation
    county_hash = get_deterministic_hash(county_name)
    hash_value = int(county_hash[:8], 16)
    variation = ((hash_value % 100) / 100.0) * 0.02 - 0.01

    actual_rate = max(
        failure_config["min_per_asset_per_year"],
        min(
            failure_config["max_per_asset_per_year"],
            base_rate + variation
        )
    )

    return {
        "per_asset_per_year": round(actual_rate, 4),
        "min_range": failure_config["min_per_asset_per_year"],
        "max_range": failure_config["max_per_asset_per_year"],
        "county_type": county_type,
        "trend": "stable"
    }


def generate_smart_meter_deployment(county_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate smart meter deployment statistics for county"""

    county_type = classify_county_type(county_name)
    smartmeter_config = config["statistics"]["smart_meter_deployment"]

    # Deployment rates by county type
    if county_type == "urban":
        deployment_percent = smartmeter_config["urban_percent"]
    elif county_type == "suburban":
        avg = (smartmeter_config["urban_percent"] + smartmeter_config["rural_percent"]) / 2
        deployment_percent = int(avg)
    else:  # rural
        deployment_percent = smartmeter_config["rural_percent"]

    # Add minor variation
    county_hash = get_deterministic_hash(county_name)
    hash_value = int(county_hash[:8], 16)
    variation = ((hash_value % 100) / 100.0) * 4 - 2
    actual_percent = max(30, min(98, int(deployment_percent + variation)))

    return {
        "deployment_percent": actual_percent,
        "customers_remaining": 100 - actual_percent,
        "estimated_customers_with_smart_meters": int(100000 * (actual_percent / 100)),
        "rollout_status": "advanced" if actual_percent > 85 else "in_progress" if actual_percent > 50 else "early_stage",
        "expected_completion_year": 2028
    }


def generate_capex_per_mva(county_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate capex per MVA statistics for county"""

    county_type = classify_county_type(county_name)
    capex_config = config["statistics"]["capex_per_mva"]

    # Capex varies by county type and network density
    if county_type == "urban":
        base_capex = 20000  # More efficient, existing infrastructure
    elif county_type == "suburban":
        base_capex = 25000  # Mixed
    else:  # rural
        base_capex = 32000  # More expensive (lower density, longer lines)

    # Add deterministic variation
    county_hash = get_deterministic_hash(county_name)
    hash_value = int(county_hash[:8], 16)
    variation = ((hash_value % 100) / 100.0) * 10000 - 5000
    actual_capex = max(
        capex_config["min_euros"],
        min(
            capex_config["max_euros"],
            int(base_capex + variation)
        )
    )

    return {
        "euro_per_mva": actual_capex,
        "min_range_euro": capex_config["min_euros"],
        "max_range_euro": capex_config["max_euros"],
        "national_average_euro": capex_config["national_average_euros"],
        "county_type": county_type,
        "expected_3year_capex_million": round((actual_capex / 1000) * 500, 1)  # Assume 500 MVA average
    }


def generate_county_statistics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive statistics for all Irish counties"""

    counties = get_irish_counties()
    statistics = {}

    for county in counties:
        statistics[county] = {
            "transformer_age": generate_transformer_age(county, config),
            "failure_rate": generate_failure_rate(county, config),
            "smart_meter_deployment": generate_smart_meter_deployment(county, config),
            "capex_per_mva": generate_capex_per_mva(county, config),
            "reproducibility_hash": get_deterministic_hash(county)
        }

    return statistics


def generate_summary_statistics(config: Dict[str, Any], county_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Generate national-level summary statistics"""

    avg_transformer_age = sum(
        stats["transformer_age"]["average_age_years"] for stats in county_stats.values()
    ) / len(county_stats)

    avg_failure_rate = sum(
        stats["failure_rate"]["per_asset_per_year"] for stats in county_stats.values()
    ) / len(county_stats)

    avg_smart_meter = sum(
        stats["smart_meter_deployment"]["deployment_percent"] for stats in county_stats.values()
    ) / len(county_stats)

    avg_capex = sum(
        stats["capex_per_mva"]["euro_per_mva"] for stats in county_stats.values()
    ) / len(county_stats)

    # Count modernization status
    high_modernization = sum(
        1 for stats in county_stats.values()
        if stats["transformer_age"]["modernization_rate"] > 50
    )

    advanced_smartmeters = sum(
        1 for stats in county_stats.values()
        if stats["smart_meter_deployment"]["deployment_percent"] > 85
    )

    return {
        "total_counties": len(county_stats),
        "national_average_transformer_age_years": round(avg_transformer_age, 1),
        "national_average_failure_rate": round(avg_failure_rate, 4),
        "national_smart_meter_deployment_percent": round(avg_smart_meter, 1),
        "national_average_capex_per_mva": round(avg_capex, 0),
        "counties_with_high_modernization": high_modernization,
        "counties_with_advanced_smart_meter_deployment": advanced_smartmeters,
        "network_age_distribution": {
            "very_old_avg": sum(1 for s in county_stats.values() if s["transformer_age"]["average_age_years"] > 40),
            "old_avg": sum(1 for s in county_stats.values() if 30 <= s["transformer_age"]["average_age_years"] <= 40),
            "moderate_avg": sum(1 for s in county_stats.values() if 20 <= s["transformer_age"]["average_age_years"] < 30),
            "young_avg": sum(1 for s in county_stats.values() if s["transformer_age"]["average_age_years"] < 20)
        }
    }


def generate_output(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete standardized output"""

    county_stats = generate_county_statistics(config)
    summary = generate_summary_statistics(config, county_stats)

    output = {
        "meta": {
            "module": "d04_statistics",
            "sources": config["sources"],
            "reference_year": config["reference_year"],
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "metrics": config["metrics"],
            "version": "1.0"
        },
        "data": {
            "counties": county_stats
        },
        "summary": summary,
        "quality_metrics": {
            "data_completeness": f"{len(county_stats)} counties with full statistics",
            "expected_transformer_lifespan_years": config["statistics"]["transformer_age"]["expected_lifespan_years"],
            "network_modernization_target": "Replace aging transformers by 2035"
        }
    }

    return output


def main():
    """Main execution function"""

    print("Module d04_statistics: Grid Performance Metrics")
    print("=" * 60)

    # Load configuration
    config = load_config()
    print(f"Loaded configuration from {len(config['sources'])} sources")
    print(f"Reference year: {config['reference_year']}")

    # Generate statistics
    output = generate_output(config)

    # Write output
    output_path = os.path.join(MODULE_DIR, 'output.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)

    # Print summary
    summary = output["summary"]
    print(f"\nStatistics generated for {summary['total_counties']} counties")
    print(f"\nNational Averages:")
    print(f"  Transformer age: {summary['national_average_transformer_age_years']} years")
    print(f"  Failure rate: {summary['national_average_failure_rate']} per asset/year")
    print(f"  Smart meter deployment: {summary['national_smart_meter_deployment_percent']}%")
    print(f"  Capex per MVA: €{summary['national_average_capex_per_mva']:,.0f}")
    print(f"\nNetwork Status:")
    print(f"  High modernization counties: {summary['counties_with_high_modernization']}")
    print(f"  Advanced smart meter deployment: {summary['counties_with_advanced_smart_meter_deployment']}")
    print(f"\nOutput written to: {output_path}")


if __name__ == '__main__':
    main()
