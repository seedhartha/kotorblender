"""
Light utility functions.
"""

def calc_light_power(light):
    """
    Calculate Eevee light power from Aurora light radius and multiplier
    """
    light.data.energy = light.kb.multiplier * light.kb.radius * light.kb.radius
