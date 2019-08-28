# -*- coding: utf-8 -*-
from random import uniform
box_body = [u'.ılılıll', u'|̲̅̅●̲̅̅|̲̅̅=̲̅̅|̲̅̅●̲̅̅|', u'llılılı.']

def hsl2rgbn(h, c, l, n):
    k = (n + h/30) % 12
    return int(round(255*(l - c*max(min(k-3, 9-k, 1), -1))))

def hsl_to_rgb(hue, sat, lit):
    """Convert hsl tuple to rgb color hex tag."""
    chroma = sat * min(lit, 1 - lit)
    r = hsl2rgbn(hue, chroma, lit, 0)
    g = hsl2rgbn(hue, chroma, lit, 8)
    b = hsl2rgbn(hue, chroma, lit, 4)
    return u'<c=#%02x%02x%02x>' % (r, g, b)

def boombox(text):
    # The base hue used for the boombox.
    base = uniform(0, 360)
    # The boombox sound needs a hue that is visibly different
    # from the boombox body hue, so generate a random hue that
    # differs at least by 60 degrees of hue.
    hues = [(uniform(base - 120, base + 120) + 180) % 360, base]
    # The color tags that will be used.
    colortag = [hsl_to_rgb(
            hue,
            uniform(0.85, 1.00), # Saturation range
            uniform(0.45, 0.70), # Value range 
            )
        for hue in hues]
    # The boombox text, now decorated with its tags.
    return (
        text
        + u' '
        + colortag[0]
        + box_body[0]
        + colortag[1]
        + box_body[1]
        + u'</c>'
        + box_body[2]
        + u'</c>'
        )

boombox.command = "boombox"

"""
To use in the quirks menu:
regex replace ^(.*)$ 
and replace it with
boombox(\1)

where gradientname is the name entered in the double quotes.

Remember to click the RELOAD FUNCTIONS button
so that it will appear in the functions list
and to test if you did it right.

There will be no error messages if you edited this file correctly.
Don't forget to click FINISH then OK when you're done.
If you want to test it, use the QUIRK TEST button so
you don't flood memos or chats.
"""
