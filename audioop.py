"""
Stub minimal du module `audioop` pour éviter ModuleNotFoundError dans des environnements
où l'extension C `_audioop` n'est pas disponible. Fournit des versions de base de
quelques fonctions (rms, add, mul, ratecv). Ne remplace pas l'implémentation complète.
"""

import struct
import math
from typing import Tuple, Optional

def _samples_from_bytes(fragment: bytes, width: int):
    if width == 1:
        fmt = f"{len(fragment)}b"
        return struct.unpack(fmt, fragment)
    elif width == 2:
        count = len(fragment) // 2
        fmt = f"<{count}h"
        return struct.unpack(fmt, fragment)
    else:
        # widths autres non supportés : renvoyer bytes bruts comme valeurs 0
        return []

def rms(fragment: bytes, width: int) -> int:
    samples = _samples_from_bytes(fragment, width)
    if not samples:
        return 0
    mean_sq = sum(s * s for s in samples) / len(samples)
    return int(math.sqrt(mean_sq))

def add(fragment1: bytes, fragment2: bytes, width: int) -> bytes:
    # addition simple échantillon par échantillon, avec saturation pour éviter overflow
    s1 = _samples_from_bytes(fragment1, width)
    s2 = _samples_from_bytes(fragment2, width)
    if not s1 or not s2:
        return b""
    length = min(len(s1), len(s2))
    out = []
    maxv = 2 ** (8 * width - 1) - 1
    minv = -2 ** (8 * width - 1)
    for i in range(length):
        v = s1[i] + s2[i]
        if v > maxv: v = maxv
        if v < minv: v = minv
        out.append(int(v))
    if width == 1:
        return struct.pack(f"{len(out)}b", *out)
    else:
        return struct.pack(f"<{len(out)}h", *out)

def mul(fragment: bytes, factor: float, width: int) -> bytes:
    s = _samples_from_bytes(fragment, width)
    if not s:
        return b""
    maxv = 2 ** (8 * width - 1) - 1
    minv = -2 ** (8 * width - 1)
    out = []
    for val in s:
        v = int(val * factor)
        if v > maxv: v = maxv
        if v < minv: v = minv
        out.append(v)
    if width == 1:
        return struct.pack(f"{len(out)}b", *out)
    else:
        return struct.pack(f"<{len(out)}h", *out)

def ratecv(fragment: bytes, width: int, nchannels: int, inrate: int, outrate: int, state: Optional[Tuple]=None):
    """
    Conversion d'échantillonnage très basique : si inrate == outrate on renvoie inchangé.
    Retourne (converted_fragment, new_state).
    """
    if inrate == outrate or not fragment:
        return fragment, state
    # Pas d'implémentation complète : renvoyer inchangé mais garder l'interface
    return fragment, state

# Fonctions supplémentaires minimalistes pour compatibilité
def avg(fragment: bytes, width: int) -> int:
    s = _samples_from_bytes(fragment, width)
    if not s:
        return 0
    return int(sum(s) / len(s))

def max(fragment: bytes, width: int) -> int:
    s = _samples_from_bytes(fragment, width)
    if not s:
        return 0
    return max(s)
