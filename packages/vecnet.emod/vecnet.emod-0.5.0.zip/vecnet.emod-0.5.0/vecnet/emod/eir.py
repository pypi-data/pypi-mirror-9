import math

def prevalence(eir):
    """
EIR to prevalence conversion. This relationship is used by Philip Eckhoff to calibrate EMOD model.

Please refer to paper below for additional details
Smith, D. L., Dushoff, J., Snow, R. W., & Hay, S. I. (2005). The entomological inoculation rate and Plasmodium
falciparum infection in African children. Nature, 438(7067) 492-495.doi:10.1038/nature04024
http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3128496/#FD1
"""
    prevalence = 1 - math.pow(1 + 0.45*4.2*eir, -0.238)
    return prevalence
