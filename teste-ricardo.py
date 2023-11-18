# Libraries
import math

# Inputs
Ks = 120
Qc = 0.003070
Dint = 0.1036
Inc = 0.02
teta = math.pi


# Code
def newton(_Ks, _Dint, _Inc, _Qc, _teta):
    _val = _Ks * (_Dint*2)/8 * (_teta - math.sin(_teta)) * (_Dint/4(_teta - math.sin(_teta))/_teta)*(2./3)  * (_Inc)*(1./2) - Qc
    return _val

for n in range(6):
    val = newton(Ks, Dint, Inc, Qc, teta)
    while val > 0:
        teta = teta - 1/10**n
        val = newton(Ks, Dint, Inc, Qc, teta)
    teta = teta + 1/10**n

# Outputs
OUT = teta