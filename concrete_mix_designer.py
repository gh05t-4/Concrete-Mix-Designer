#!/usr/bin/env python3

# IS 456:2000 Table 5 | "Exposure condition": [Minimum cement content in kg/m^3, Maximum water to cement ratio] 
is456_t5 = { "Mild": [300, 0.55], "Moderate": [300, 0.50], "Severe": [320, 0.45], "Very Severe": [340, 0.45], "Extreme": [360, 0.40] }

# IS 10262:2009 Table 1 | "Grade": Assumed Standard Deviation
is10262_t1 = { "M1": 3.5, "M2": 4.0, "M3_5": 5.0 }

# IS 10262:2009 Table 2 | "Nominal Maximum Size Of Aggregate in mm": Maximum Water content in kg
is10262_t2 = { "10": 208, "20": 186, "40": 165 }

# IS 10262:2009 Table 3 | "Nominal Maximum Size Of Aggregate in mm": (vol of coarse aggregates)[Zone 4, Zone 3, Zone 2, Zone 1]
is10262_t3 = { "10": [0.50, 0.48, 0.46, 0.44], "20": [0.66, 0.64, 0.62, 0.60], "40": [0.75, 0.73, 0.71, 0.69] }

def target_strength_calculation(grade):
    """Target Strength for Mix Propotioning"""
    if grade == "M 10" or grade == "M 15":
        g = "M1"
    elif grade == "M 20" or grade == "M 25":
        g = "M2"
    else:
        g = "M3_5"
    
    for x, s in is10262_t1.items():
        if x == g:
            sd = s
    
    return int(grade.replace("M ",'')) + (1.65 * sd)

def water_cement_ratio_calculation(exposure):
    """Selection Of Water Cement Ratio"""
    exp = exposure.capitalize()
    for x, v in is456_t5.items():
        if x == exp:
            wcr = v[1]
    return wcr

def water_content_calculation(slump, soa, toa, chem_ad):
    """Selection Of Water Content"""
    # Factor for convertion of water content of 50 mm slump to required slump
    n = (int(slump) - 50) / 25
    for x, v in is10262_t2.items():
        if x == soa:
            water_content = v
    if toa == "sub-angular":
        water_content -= 10
    elif toa == "gravel":
        water_content -= 20
    elif toa == "rounded gravel":
        water_content -= 25
    
    if int(slump) > 50:
        water_content += (0.03 * n * water_content)

    if chem_ad == "Super Plasticizer":
        water_content -= water_content * 0.2
    elif chem_ad == "Plasticizer":
        water_content -= water_content * 0.1

    return water_content

def cement_content_calculation(exposure, wcr, wc):
    """Calculation Of Cement Content"""
    exp = exposure.capitalize()
    for x, v in is456_t5.items():
        if x == exp:
            min_cc = v[0]
    
    cement_content = wc/wcr

    if cement_content < min_cc:
        cement_content = min_cc
    
    return cement_content

def fly_cement_content_calculation(exposure, wcr, wc):
    """Calculation Of Cement Content"""
    exp = exposure.capitalize()
    for x, v in is456_t5.items():
        if x == exp:
            min_cc = v[0]
    
    cement_content = wc/wcr
    temp = cement_content

    if cement_content < min_cc:
        cement_content = min_cc
        temp = cement_content

    cement_content *= 1.10

    new_water_cement_ratio = wc/cement_content

    flyash_content = cement_content * 0.3

    cement_content -= flyash_content

    cement_saved = temp - cement_content

    return cement_content, flyash_content, cement_saved, new_water_cement_ratio

def vol_of_CAnFA_calculation(zone, soa, wcr, pumping):
    """Proportion Of Volume Of Coarse Aggregate And Fine Aggregate Content"""
    if zone == "Zone 4":
        i = 0
    elif zone == "Zone 3":
        i = 1
    elif zone == "Zone 2":
        i = 2
    elif zone == "Zone 1":
        i = 3
    
    for x, v in is10262_t3.items():
        if x == soa:
            vol_CA = v[i]
    
    if wcr > 0.5:
        vol_CA -= 0.01*((wcr - 0.5)/0.05)
    else:
        vol_CA += 0.01*((0.5 - wcr)/0.05)

    if pumping == True:
        vol_CA *= 0.9

    vol_FA = 1 - vol_CA

    return vol_CA, vol_FA

def fly_vol_of_CAnFA_calculation(zone, soa, wcr, pumping):
    """Proportion Of Volume Of Coarse Aggregate And Fine Aggregate Content"""
    if zone == "Zone 4":
        i = 0
    elif zone == "Zone 3":
        i = 1
    elif zone == "Zone 2":
        i = 2
    elif zone == "Zone 1":
        i = 3
    
    for x, v in is10262_t3.items():
        if x == soa:
            vol_CA = v[i]
    
    if wcr > 0.5:
        vol_CA -= 0.01*((wcr - 0.5)/0.05)
    else:
        vol_CA += 0.01*((0.5 - wcr)/0.05)

    if pumping == True:
        vol_CA *= 0.9

    vol_FA = 1 - vol_CA

    return vol_CA, vol_FA

def mix_calculation(cc, sp_c, wc, v_ca, v_fa, sp_ca, sp_fa):
    """Mix Calculations per unit volume of concrete"""
    # Volume of cement
    vol_cement = (cc/sp_c) * 0.001
    print("\nVolume of cement = {:.4f}".format(vol_cement))

    # Volume of water
    vol_water = wc * 0.001
    print("\nVolume of water = {:.4f}".format(vol_water))

    # Volume of Chemical Admixture @ 2% by cementitious material
    mass_of_chemAd = cc * 0.02
    vol_chemAd = (mass_of_chemAd / 1.145) * 0.001
    print("\nVolume of Chemical Admixture = {:.4f}".format(vol_chemAd))

    # Volume of all in aggregate
    vol_all_aggr = (1 - (vol_cement + vol_water + vol_chemAd))
    print("\nVolume of all in aggregate = {:.4f}".format(vol_all_aggr))

    # Mass of Coarse aggregate
    mass_CA = vol_all_aggr * v_ca * sp_ca * 1000

    # Mass of Fine aggregate
    mass_FA = vol_all_aggr * v_fa * sp_fa * 1000

    return mass_of_chemAd, mass_CA, mass_FA

def fly_mix_calculation(cc, sp_c, wc, v_ca, v_fa, sp_ca, sp_fa, sp_fly, fc):
    """Mix Calculations per unit volume of concrete"""
    # Volume of cement
    vol_cement = (cc/sp_c) * 0.001
    print("\nVolume of cement = {:.4f}".format(vol_cement))

    # Volume of fly ash
    vol_flyash = (fc/sp_fly) * 0.001
    print("\nVolume of fly ash = {:.4f}".format(vol_flyash))

    # Volume of water
    vol_water = wc * 0.001
    print("\nVolume of water = {:.4f}".format(vol_water))

    # Volume of Chemical Admixture @ 2% by cementitious material
    mass_of_chemAd = cc * 0.02
    vol_chemAd = (mass_of_chemAd / 1.145) * 0.001
    print("\nVolume of Chemical Admixture = {:.4f}".format(vol_chemAd))

    # Volume of all in aggregate
    vol_all_aggr = (1 - (vol_cement + vol_flyash + vol_water + vol_chemAd))
    print("\nVolume of all in aggregate = {:.4f}".format(vol_all_aggr))

    # Mass of Coarse aggregate
    mass_CA = vol_all_aggr * v_ca * sp_ca * 1000

    # Mass of Fine aggregate
    mass_FA = vol_all_aggr * v_fa * sp_fa * 1000

    return mass_of_chemAd, mass_CA, mass_FA

# Input from user and calling the fuction

GRADE = input("\nEnter the Grade Designition (eg: M 40): ")
if len(GRADE) == 3:
    GRADE = GRADE.upper()
    GRADE = GRADE.replace('M', 'M ')

print("\nWhich mineral admixture are you using?")
print("""
        [1] None
        [2] Fly ash
    """)
min_ad = input("Choise (eg: 2): ")
if min_ad == '1':
    TYPE_OF_MINERAL_ADMIXTURE = ''
elif min_ad == '2':
    TYPE_OF_MINERAL_ADMIXTURE = "Fly ash"

SIZE_OF_AGGREGATE = input("\nEnter the maximum nominal size of aggregate in mm: ")

WORKABILITY = input("Enter the workability(slump) of cement in mm: ")

EXPOSURE_CONDITION = input("Enter the exposure condition (eg: Moderate): ")

METHOD_OF_PLACING = input("Will you pump the concrete? (yes or no): ")
while True:
    if METHOD_OF_PLACING.lower() == 'yes':
        pumping = True
        break
    elif METHOD_OF_PLACING.lower() == 'no':
        pumping = False
        break
    else:
        print("Invalid Input!!")
    METHOD_OF_PLACING = input("Will you pump the concrete? (yes or no): ")

print("\nSelect the type of aggregate:")
print("""
        [1] Sub-angular
        [2] Gravel
        [3] Rounded gravel
        [4] Crushed Angular
    """)
TYPE_OF_AGGREGATE = input("Choice (eg: 4): ")
if TYPE_OF_AGGREGATE == "1":
    toa = "sub-angular"
elif TYPE_OF_AGGREGATE == "2":
    toa = "gravel"
elif TYPE_OF_AGGREGATE == "3":
    toa = "rounded gravel"
else:
    toa = ''

print("\nSelect the type of chemical admixture:")
print("""
        [1] Super Plasticizer
        [2] Plasticizer    
    """)
CHEMICAL_ADMIXTURE = input("Choice (eg: 1): ")
if CHEMICAL_ADMIXTURE == "1":
    chem_ad = "Super Plasticizer"
elif CHEMICAL_ADMIXTURE == "2":
    chem_ad = "Plasticizer"

SP_CEMENT = float(input("\nEnter specific gravity of cement: "))

if TYPE_OF_MINERAL_ADMIXTURE == "Fly ash":
    SP_ADMIX = float(input("Enter specific gravity of fly ash: "))

SP_CA = float(input("Enter specific gravity of coarse aggregate: "))

SP_FA = float(input("Enter specific gravity of fine aggregate: "))

WATER_ABSORPTION_CA = float(input("Enter the water absorption of COARSE aggregates: "))

WATER_ABSORPTION_FA = float(input("Enter the water absorption of FINE aggregates: "))

print("\nSelect the zone of fine aggregates: ")
print("""
        [1] Zone 1
        [2] Zone 2
        [3] Zone 3
        [4] Zone 4
    """)
ZONE_OF_FA = input("Choice: ")
if ZONE_OF_FA == '1':
    zone = "Zone 1"
elif ZONE_OF_FA == '2':
    zone = "Zone 2"
elif ZONE_OF_FA == '3':
    zone = "Zone 3"
elif ZONE_OF_FA == '4':
    zone = "Zone 4"

# Printing the results
TARGET_STRENGTH = target_strength_calculation(GRADE)
print("\nTarget strength = {} N/mm^2".format(TARGET_STRENGTH))

WATER_CEMENT_RATIO = water_cement_ratio_calculation(EXPOSURE_CONDITION)

WATER_CONTENT = water_content_calculation(WORKABILITY, SIZE_OF_AGGREGATE, toa, chem_ad)
if TYPE_OF_MINERAL_ADMIXTURE == '':
    CEMENT_CONTENT = cement_content_calculation(EXPOSURE_CONDITION, WATER_CEMENT_RATIO, WATER_CONTENT)

    VOL_CA, VOL_FA = vol_of_CAnFA_calculation(zone, SIZE_OF_AGGREGATE, WATER_CEMENT_RATIO, pumping)
    print("\nProportion of Volume of COARSE AGGREGATE is {:.2f} and of FINE AGGREGATE is {:.2f}".format(VOL_CA, VOL_FA))

    MASS_CHEM_AD, MASS_CA, MASS_FA = mix_calculation(CEMENT_CONTENT, SP_CEMENT, WATER_CONTENT, VOL_CA, VOL_FA, SP_CA, SP_FA)

    print("\nMix Proportions for this trial:")
    print("""
            1. Cement               =   {:.2f} kg/m^3
            2. Water                =   {:.2f} lit
            3. Fine aggregate       =   {:.2f} kg
            4. Coarse aggregate     =   {:.2f} kg
            5. Chemical admixture   =   {:.2f} kg/m^3
            6. Water-cement ratio   =   {}
    """.format(CEMENT_CONTENT, WATER_CONTENT, MASS_FA, MASS_CA, MASS_CHEM_AD, WATER_CEMENT_RATIO))

    print("\nCorrection for Water absorption of aggregate:")
    print("""
            1. Coarse aggregate = {:.2f} lit
            2. Fine aggregate   = {:.2f} lit
    """.format((MASS_CA * WATER_ABSORPTION_CA * 0.01), (MASS_FA * WATER_ABSORPTION_FA * 0.01)))
else:
    CEMENT_CONTENT, FLYASH_CONTENT, CEMENT_SAVED, NEW_WATER_CEMENT_RATIO = fly_cement_content_calculation(EXPOSURE_CONDITION, WATER_CEMENT_RATIO, WATER_CONTENT)
    print("Cement saved while using flyash is {:.2f}".format(CEMENT_SAVED))

    VOL_CA, VOL_FA = fly_vol_of_CAnFA_calculation(zone, SIZE_OF_AGGREGATE, WATER_CEMENT_RATIO, pumping)
    print("\nProportion of Volume of COARSE AGGREGATE is {:.2f} and of FINE AGGREGATE is {:.2f}".format(VOL_CA, VOL_FA))

    MASS_CHEM_AD, MASS_CA, MASS_FA = fly_mix_calculation(CEMENT_CONTENT, SP_CEMENT, WATER_CONTENT, VOL_CA, VOL_FA, SP_CA, SP_FA, SP_ADMIX, FLYASH_CONTENT)

    print("\nMix Proportions for this trial:")
    print("""
            1. Cement               =   {:.2f} kg/m^3
            2. Flyash               =   {:.2f} kg/m^3
            3. Water                =   {:.2f} lit
            4. Fine aggregate       =   {:.2f} kg
            5. Coarse aggregate     =   {:.2f} kg
            6. Chemical admixture   =   {:.2f} kg/m^3
            7. Water-cement ratio   =   {:.3f}
    """.format(CEMENT_CONTENT, FLYASH_CONTENT, WATER_CONTENT, MASS_FA, MASS_CA, MASS_CHEM_AD, NEW_WATER_CEMENT_RATIO))

    print("\nCorrection for Water absorption of aggregate:")
    print("""
            1. Coarse aggregate = {:.2f} lit
            2. Fine aggregate   = {:.2f} lit
    """.format((MASS_CA * WATER_ABSORPTION_CA * 0.01), (MASS_FA * WATER_ABSORPTION_FA * 0.01)))