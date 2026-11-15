"""
Crop Knowledge Base - FAO-56 Crop Coefficients and Parameters

Source: FAO Irrigation and Drainage Paper 56
Allen, R.G., Pereira, L.S., Raes, D., Smith, M. (1998)
"""

from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class CropStage:
    """Crop growth stage parameters"""
    name: str
    duration_days: int  # Typical duration
    kc: float  # Crop coefficient

@dataclass
class CropParameters:
    """Complete crop parameter set"""
    name: str
    category: str  # grain, legume, vegetable, cover, etc.
    kc_ini: float  # Initial stage Kc
    kc_mid: float  # Mid-season stage Kc
    kc_end: float  # End-season stage Kc
    stage_initial_days: int
    stage_development_days: int
    stage_mid_days: int
    stage_late_days: int
    rooting_depth: float  # meters
    depletion_fraction: float  # p value (0-1)
    is_nitrogen_fixer: bool = False
    notes: str = ""

# ============================================================================
# CROP DATABASE - FAO-56 Standard Values
# ============================================================================

CROP_DATABASE: Dict[str, CropParameters] = {
    # GRAINS
    "wheat": CropParameters(
        name="Wheat (Winter)",
        category="grain",
        kc_ini=0.30,
        kc_mid=1.15,
        kc_end=0.40,
        stage_initial_days=30,
        stage_development_days=140,
        stage_mid_days=50,
        stage_late_days=30,
        rooting_depth=1.0,
        depletion_fraction=0.55,
        notes="FAO-56 Table 12. Values for winter wheat."
    ),
    
    "corn": CropParameters(
        name="Corn (Maize, Field)",
        category="grain",
        kc_ini=0.30,
        kc_mid=1.20,
        kc_end=0.60,
        stage_initial_days=20,
        stage_development_days=35,
        stage_mid_days=40,
        stage_late_days=30,
        rooting_depth=1.0,
        depletion_fraction=0.55,
        notes="FAO-56 Table 12. Values for grain corn."
    ),
    
    "rice": CropParameters(
        name="Rice",
        category="grain",
        kc_ini=1.05,  # Flooded conditions
        kc_mid=1.20,
        kc_end=0.90,
        stage_initial_days=30,
        stage_development_days=30,
        stage_mid_days=60,
        stage_late_days=30,
        rooting_depth=0.5,
        depletion_fraction=0.20,  # Flooded rice
        notes="FAO-56 Table 12. Flooded rice."
    ),
    
    "sorghum": CropParameters(
        name="Sorghum",
        category="grain",
        kc_ini=0.30,
        kc_mid=1.00,
        kc_end=0.55,
        stage_initial_days=20,
        stage_development_days=35,
        stage_mid_days=40,
        stage_late_days=30,
        rooting_depth=1.0,
        depletion_fraction=0.55,
        notes="FAO-56 Table 12."
    ),
    
    # LEGUMES
    "soybean": CropParameters(
        name="Soybean",
        category="legume",
        kc_ini=0.40,
        kc_mid=1.15,
        kc_end=0.50,
        stage_initial_days=20,
        stage_development_days=30,
        stage_mid_days=60,
        stage_late_days=25,
        rooting_depth=0.8,
        depletion_fraction=0.50,
        is_nitrogen_fixer=True,
        notes="FAO-56 Table 12. Nitrogen fixing legume."
    ),
    
    "dry_beans": CropParameters(
        name="Dry Beans",
        category="legume",
        kc_ini=0.40,
        kc_mid=1.15,
        kc_end=0.35,
        stage_initial_days=20,
        stage_development_days=30,
        stage_mid_days=40,
        stage_late_days=20,
        rooting_depth=0.7,
        depletion_fraction=0.45,
        is_nitrogen_fixer=True,
        notes="FAO-56 Table 12."
    ),
    
    "peas": CropParameters(
        name="Peas",
        category="legume",
        kc_ini=0.50,
        kc_mid=1.15,
        kc_end=0.35,
        stage_initial_days=20,
        stage_development_days=30,
        stage_mid_days=35,
        stage_late_days=15,
        rooting_depth=0.7,
        depletion_fraction=0.45,
        is_nitrogen_fixer=True,
        notes="FAO-56 Table 12."
    ),
    
    "lentils": CropParameters(
        name="Lentils",
        category="legume",
        kc_ini=0.40,
        kc_mid=1.10,
        kc_end=0.30,
        stage_initial_days=20,
        stage_development_days=30,
        stage_mid_days=60,
        stage_late_days=40,
        rooting_depth=0.8,
        depletion_fraction=0.50,
        is_nitrogen_fixer=True,
        notes="FAO-56 Table 12. Nitrogen fixing."
    ),
    
    # VEGETABLES
    "tomato": CropParameters(
        name="Tomato",
        category="vegetable",
        kc_ini=0.60,
        kc_mid=1.15,
        kc_end=0.80,
        stage_initial_days=30,
        stage_development_days=40,
        stage_mid_days=45,
        stage_late_days=30,
        rooting_depth=0.7,
        depletion_fraction=0.40,
        notes="FAO-56 Table 12."
    ),
    
    "potato": CropParameters(
        name="Potato",
        category="vegetable",
        kc_ini=0.50,
        kc_mid=1.15,
        kc_end=0.75,
        stage_initial_days=25,
        stage_development_days=30,
        stage_mid_days=45,
        stage_late_days=30,
        rooting_depth=0.6,
        depletion_fraction=0.35,
        notes="FAO-56 Table 12."
    ),
    
    "onion": CropParameters(
        name="Onion (dry)",
        category="vegetable",
        kc_ini=0.70,
        kc_mid=1.05,
        kc_end=0.75,
        stage_initial_days=15,
        stage_development_days=25,
        stage_mid_days=70,
        stage_late_days=40,
        rooting_depth=0.4,
        depletion_fraction=0.30,
        notes="FAO-56 Table 12."
    ),
    
    "carrot": CropParameters(
        name="Carrot",
        category="vegetable",
        kc_ini=0.70,
        kc_mid=1.05,
        kc_end=0.95,
        stage_initial_days=20,
        stage_development_days=30,
        stage_mid_days=50,
        stage_late_days=20,
        rooting_depth=0.6,
        depletion_fraction=0.35,
        notes="FAO-56 Table 12."
    ),
    
    # COVER CROPS
    "clover": CropParameters(
        name="Clover (cover crop)",
        category="cover",
        kc_ini=0.40,
        kc_mid=0.85,
        kc_end=0.85,
        stage_initial_days=20,
        stage_development_days=60,
        stage_mid_days=90,
        stage_late_days=0,  # Not harvested
        rooting_depth=0.7,
        depletion_fraction=0.40,
        is_nitrogen_fixer=True,
        notes="Cover crop, nitrogen fixing."
    ),
    
    "winter_rye": CropParameters(
        name="Winter Rye (cover)",
        category="cover",
        kc_ini=0.30,
        kc_mid=1.10,
        kc_end=0.40,
        stage_initial_days=30,
        stage_development_days=50,
        stage_mid_days=60,
        stage_late_days=30,
        rooting_depth=1.2,
        depletion_fraction=0.55,
        notes="Cover crop, excellent erosion control."
    ),
    
    "vetch": CropParameters(
        name="Vetch (cover crop)",
        category="cover",
        kc_ini=0.40,
        kc_mid=1.00,
        kc_end=0.90,
        stage_initial_days=20,
        stage_development_days=40,
        stage_mid_days=80,
        stage_late_days=20,
        rooting_depth=0.8,
        depletion_fraction=0.45,
        is_nitrogen_fixer=True,
        notes="Nitrogen-fixing cover crop."
    ),
    
    # OILSEEDS
    "sunflower": CropParameters(
        name="Sunflower",
        category="oilseed",
        kc_ini=0.35,
        kc_mid=1.15,
        kc_end=0.35,
        stage_initial_days=25,
        stage_development_days=35,
        stage_mid_days=45,
        stage_late_days=25,
        rooting_depth=1.0,
        depletion_fraction=0.45,
        notes="FAO-56 Table 12."
    ),
    
    "canola": CropParameters(
        name="Canola (Rapeseed)",
        category="oilseed",
        kc_ini=0.35,
        kc_mid=1.15,
        kc_end=0.35,
        stage_initial_days=20,
        stage_development_days=30,
        stage_mid_days=50,
        stage_late_days=30,
        rooting_depth=1.0,
        depletion_fraction=0.60,
        notes="Similar to other oilseeds."
    ),
    
    # FORAGES
    "alfalfa": CropParameters(
        name="Alfalfa",
        category="forage",
        kc_ini=0.40,
        kc_mid=1.20,
        kc_end=1.15,
        stage_initial_days=10,
        stage_development_days=30,
        stage_mid_days=70,
        stage_late_days=10,
        rooting_depth=1.5,
        depletion_fraction=0.55,
        is_nitrogen_fixer=True,
        notes="FAO-56. Perennial, nitrogen fixing. Multiple cuttings."
    ),
    
    "pasture": CropParameters(
        name="Pasture (mixed grass)",
        category="forage",
        kc_ini=0.40,
        kc_mid=0.85,
        kc_end=0.85,
        stage_initial_days=30,
        stage_development_days=50,
        stage_mid_days=150,
        stage_late_days=0,
        rooting_depth=0.8,
        depletion_fraction=0.60,
        notes="Continuous grazing."
    ),
    
    # COTTON
    "cotton": CropParameters(
        name="Cotton",
        category="fiber",
        kc_ini=0.35,
        kc_mid=1.15,
        kc_end=0.70,
        stage_initial_days=30,
        stage_development_days=50,
        stage_mid_days=55,
        stage_late_days=45,
        rooting_depth=1.2,
        depletion_fraction=0.65,
        notes="FAO-56 Table 12."
    ),
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_crop_params(crop_name: str) -> Optional[CropParameters]:
    """Get crop parameters by name (case-insensitive)"""
    crop_key = crop_name.lower().replace(" ", "_")
    return CROP_DATABASE.get(crop_key)

def list_all_crops() -> List[str]:
    """Get list of all available crop names"""
    return [params.name for params in CROP_DATABASE.values()]

def get_crops_by_category(category: str) -> List[CropParameters]:
    """Get all crops in a category"""
    return [params for params in CROP_DATABASE.values() if params.category == category]

def get_nitrogen_fixers() -> List[CropParameters]:
    """Get all nitrogen-fixing crops"""
    return [params for params in CROP_DATABASE.values() if params.is_nitrogen_fixer]

def calculate_kc(crop_params: CropParameters, days_after_planting: int) -> float:
    """
    Calculate crop coefficient (Kc) for a given day after planting
    
    Uses linear interpolation between growth stages as per FAO-56 methodology
    
    Args:
        crop_params: Crop parameters
        days_after_planting: Days since planting (0 = planting day)
    
    Returns:
        Kc value for the day
    """
    # Growth stage boundaries
    L_ini = crop_params.stage_initial_days
    L_dev = crop_params.stage_development_days
    L_mid = crop_params.stage_mid_days
    L_late = crop_params.stage_late_days
    
    # Stage end days (cumulative)
    end_initial = L_ini
    end_development = L_ini + L_dev
    end_mid = L_ini + L_dev + L_mid
    end_late = L_ini + L_dev + L_mid + L_late
    
    # Determine stage and interpolate
    if days_after_planting < 0:
        return 0.0  # Before planting
    
    elif days_after_planting <= end_initial:
        # Initial stage - constant Kc_ini
        return crop_params.kc_ini
    
    elif days_after_planting <= end_development:
        # Development stage - linear interpolation from Kc_ini to Kc_mid
        progress = (days_after_planting - end_initial) / L_dev
        return crop_params.kc_ini + progress * (crop_params.kc_mid - crop_params.kc_ini)
    
    elif days_after_planting <= end_mid:
        # Mid-season stage - constant Kc_mid
        return crop_params.kc_mid
    
    elif days_after_planting <= end_late:
        # Late season - linear interpolation from Kc_mid to Kc_end
        progress = (days_after_planting - end_mid) / L_late
        return crop_params.kc_mid + progress * (crop_params.kc_end - crop_params.kc_mid)
    
    else:
        # After harvest - assume bare soil or residue
        return 0.3  # Typical residue Kc

def get_total_season_length(crop_params: CropParameters) -> int:
    """Get total growing season length in days"""
    return (crop_params.stage_initial_days + 
            crop_params.stage_development_days +
            crop_params.stage_mid_days + 
            crop_params.stage_late_days)

# ============================================================================
# VALIDATION
# ============================================================================

if __name__ == "__main__":
    # Test crop knowledge base
    print("FieldShift Crop Knowledge Base")
    print(f"Total crops: {len(CROP_DATABASE)}")
    print(f"Nitrogen fixers: {len(get_nitrogen_fixers())}")
    print("\nSample crop: Corn")
    
    corn = get_crop_params("corn")
    if corn:
        print(f"  Kc initial: {corn.kc_ini}")
        print(f"  Kc mid-season: {corn.kc_mid}")
        print(f"  Kc end: {corn.kc_end}")
        print(f"  Total season: {get_total_season_length(corn)} days")
        print(f"  Rooting depth: {corn.rooting_depth}m")
        
        # Test Kc calculation
        print("\n  Sample Kc values:")
        for day in [0, 20, 40, 60, 90, 125]:
            kc = calculate_kc(corn, day)
            print(f"    Day {day}: Kc = {kc:.3f}")
