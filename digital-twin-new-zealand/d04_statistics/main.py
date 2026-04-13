"""
Module d04_statistics: Grid performance metrics and infrastructure statistics
SSI v4.0.2 Digital Twin - New Zealand
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


def get_nz_regions() -> List[str]:
    """Return list of 16 NZ regions"""
    return [
        "Northland", "Auckland", "Waikato", "Bay of Plenty",
        "Gisborne", "Hawke's Bay", "Taranaki", "Manawatu-Whanganui",
        "Wellington", "Tasman", "Nelson", "Marlborough",
        "West Coast", "Canterbury", "Otago", "Southland"
    ]


def get_deterministic_hash(region_name: str) -> str:
    """Generate deterministic hash using MD5 for reproducibility"""
    return hashlib.md5(region_name.encode()).hexdigest()


def classify_region_type(region_name: str) -> str:
    """Classify regions as urban, suburban, or rural"""
    urban_regions = {
        "Auckland", "Wellington", "Canterbury"
    }

    suburban_regions = {
        "Waikato", "Bay of Plenty", "Otago", "Hawke's Bay"
    }

    if region_name in urban_regions:
        return "urban"
    elif region_name in suburban_regions:
        return "suburban"
    else:
        return "rural"


def generate_transformer_age(region_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate transformer age statistics for region"""

    region_type = classify_region_type(region_name)
    config_stats = config["statistics"]["transformer_age"]

    # Determine average based on region type
    if region_type == "urban":
        # Auckland ~18-25yr, Canterbury (post-2011 quake) ~20-30yr
        avg_age = config_stats["auckland_average_years"]
        variance = 5
    elif region_type == "suburban":
        avg_age = int((config_stats["auckland_average_years"] + config_stats["national_average_years"]) / 2)
        variance = 7
    else:  # rural
        avg_age = config_stats["rural_average_years"]
        variance = 10

    # Use deterministic hash for consistent variation
    region_hash = get_deterministic_hash(region_name)
    hash_value = int(region_hash[:8], 16)
    variation = ((hash_value % 100) / 100.0) * variance - (variance / 2)
    actual_avg = max(10, int(avg_age + variation))

    return {
        "average_age_years": actual_avg,
        "minimum_age_years": max(3, actual_avg - 12),
        "maximum_age_years": min(config_stats["expected_lifespan_years"], actual_avg + 18),
        "expected_lifespan_years": config_stats["expected_lifespan_years"],
        "modernization_rate": round((1 - (actual_avg / config_stats["expected_lifespan_years"])) * 100, 1),
        "region_type": region_type
    }


def generate_failure_rate(region_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate failure rate statistics for region"""

    region_type = classify_region_type(region_name)
    failure_config = config["statistics"]["failure_rate"]

    # Failure rates higher in rural areas (aging infrastructure, weather exposure, seismic)
    if region_type == "urban":
        base_rate = failure_config["national_average"] - 0.008
    elif region_type == "suburban":
        base_rate = failure_config["national_average"]
    else:  # rural
        base_rate = failure_config["national_average"] + 0.020

    # Add deterministic variation
    region_hash = get_deterministic_hash(region_name)
    hash_value = int(region_hash[:8], 16)
    variation = ((hash_value % 100) / 100.0) * 0.025 - 0.012

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
        "region_type": region_type,
        "trend": "stable"
    }


def generate_smart_meter_deployment(region_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate smart meter deployment statistics for region"""

    region_type = classify_region_type(region_name)
    smartmeter_config = config["statistics"]["smart_meter_deployment"]

    # Deployment rates by region type
    if region_type == "urban":
        deployment_percent = smartmeter_config["urban_percent"]
    elif region_type == "suburban":
        avg = (smartmeter_config["urban_percent"] + smartmeter_config["rural_percent"]) / 2
        deployment_percent = int(avg)
    else:  # rural
        deployment_percent = smartmeter_config["rural_percent"]

    # Add minor variation
    region_hash = get_deterministic_hash(region_name)
    hash_value = int(region_hash[:8], 16)
    variation = ((hash_value % 100) / 100.0) * 5 - 2.5
    actual_percent = max(35, min(96, int(deployment_percent + variation)))

    return {
        "deployment_percent": actual_percent,
        "customers_remaining": 100 - actual_percent,
        "estimated_customers_with_smart_meters": int(120000 * (actual_percent / 100)),
        "rollout_status": "advanced" if actual_percent > 88 else "in_progress" if actual_percent > 60 else "early_stage",
        "expected_completion_year": 2030
    }


def generate_capex_per_mva(region_name: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate capex per MVA statistics for region (NZD)"""

    region_type = classify_region_type(region_name)
    capex_config = config["statistics"]["capex_per_mva"]

    # Capex varies by region type and network density
    if region_type == "urban":
        base_capex = 28000  # Urban areas: existing infrastructure
    elif region_type == "suburban":
        base_capex = 35000  # Mixed density
    else:  # rural
        base_capex = 48000  # Rural areas more expensive (lower density, seismic resilience)

    # Add deterministic variation
    region_hash = get_deterministic_hash(region_name)
    hash_value = int(region_hash[:8], 16)
    variation = ((hash_value % 100) / 100.0) * 12000 - 6000
    actual_capex = max(
        capex_config["min_nzd"],
        min(
            capex_config["max_nzd"],
            int(base_capex + variation)
        )
    )

    return {
        "nzd_per_mva": actual_capex,
        "min_range_nzd": capex_config["min_nzd"],
        "max_range_nzd": capex_config["max_nzd"],
        "national_average_nzd": capex_config["national_average_nzd"],
        "region_type": region_type,
        "expected_3year_capex_million_nzd": round((actual_capex / 1000) * 450, 1)
    }


def generate_region_statistics(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate comprehensive statistics for all NZ regions"""

    regions = get_nz_regions()
    statistics = {}

    for region in regions:
        statistics[region] = {
            "transformer_age": generate_transformer_age(region, config),
            "failure_rate": generate_failure_rate(region, config),
            "smart_meter_deployment": generate_smart_meter_deployment(region, config),
            "capex_per_mva": generate_capex_per_mva(region, config),
            "reproducibility_hash": get_deterministic_hash(region)
        }

    return statistics


def generate_summary_statistics(config: Dict[str, Any], region_stats: Dict[str, Any]) -> Dict[str, Any]:
    """Generate national-level summary statistics"""

    avg_transformer_age = sum(
        stats["transformer_age"]["average_age_years"] for stats in region_stats.values()
    ) / len(region_stats)

    avg_failure_rate = sum(
        stats["failure_rate"]["per_asset_per_year"] for stats in region_stats.values()
    ) / len(region_stats)

    avg_smart_meter = sum(
        stats["smart_meter_deployment"]["deployment_percent"] for stats in region_stats.values()
    ) / len(region_stats)

    avg_capex = sum(
        stats["capex_per_mva"]["nzd_per_mva"] for stats in region_stats.values()
    ) / len(region_stats)

    # Count modernization status
    high_modernization = sum(
        1 for stats in region_stats.values()
        if stats["transformer_age"]["modernization_rate"] > 55
    )

    advanced_smartmeters = sum(
        1 for stats in region_stats.values()
        if stats["smart_meter_deployment"]["deployment_percent"] > 88
    )

    return {
        "total_regions": len(region_stats),
        "national_average_transformer_age_years": round(avg_transformer_age, 1),
        "national_average_failure_rate": round(avg_failure_rate, 4),
        "national_smart_meter_deployment_percent": round(avg_smart_meter, 1),
        "national_average_capex_per_mva_nzd": round(avg_capex, 0),
        "regions_with_high_modernization": high_modernization,
        "regions_with_advanced_smart_meter_deployment": advanced_smartmeters,
        "network_age_distribution": {
            "very_old_avg": sum(1 for s in region_stats.values() if s["transformer_age"]["average_age_years"] > 45),
            "old_avg": sum(1 for s in region_stats.values() if 30 <= s["transformer_age"]["average_age_years"] <= 45),
            "moderate_avg": sum(1 for s in region_stats.values() if 20 <= s["transformer_age"]["average_age_years"] < 30),
            "young_avg": sum(1 for s in region_stats.values() if s["transformer_age"]["average_age_years"] < 20)
        }
    }


def generate_output(config: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete standardized output"""

    region_stats = generate_region_statistics(config)
    summary = generate_summary_statistics(config, region_stats)

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
            "regions": region_stats
        },
        "summary": summary,
        "quality_metrics": {
            "data_completeness": f"{len(region_stats)} regions with full statistics",
            "expected_transformer_lifespan_years": config["statistics"]["transformer_age"]["expected_lifespan_years"],
            "network_modernization_target": "Replace aging transformers by 2037",
            "seismic_resilience_focus": "High priority for South Island and Wellington networks"
        }
    }

    return output


def main():
    """Main execution function"""

    print("Module d04_statistics: Grid Performance Metrics - New Zealand")
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
    print(f"\nStatistics generated for {summary['total_regions']} regions")
    print(f"\nNational Averages:")
    print(f"  Transformer age: {summary['national_average_transformer_age_years']} years")
    print(f"  Failure rate: {summary['national_average_failure_rate']} per asset/year")
    print(f"  Smart meter deployment: {summary['national_smart_meter_deployment_percent']}%")
    print(f"  Capex per MVA: NZ${summary['national_average_capex_per_mva_nzd']:,.0f}")
    print(f"\nNetwork Status:")
    print(f"  High modernization regions: {summary['regions_with_high_modernization']}")
    print(f"  Advanced smart meter deployment: {summary['regions_with_advanced_smart_meter_deployment']}")
    print(f"\nOutput written to: {output_path}")


if __name__ == '__main__':
    main()
