# -*- coding: utf-8 -*-
from random import uniform
box_body = [u'.ılılıll', u'|̲̅̅●̲̅̅|̲̅̅=̲̅̅|̲̅̅●̲̅̅|', u'llılılı.']

def to_tag(r, g, b):
    """Convert rgb tuple to colorhex tag."""
    return u'<c=#%06x>' % ((r<<16) + (g<<8) + b)

def to_rgb(hue, sat, lit):
    """Convert hsl tuple to rgb color value."""
    hue /= 60
    chroma = sat * (1 - abs(2*lit - 1))
    minc = int(round(255 * (lit - 0.5*chroma)))
    midc = int(round(255 * (chroma * (1 - abs(hue%2 - 1)) + (lit - 0.5*chroma))))
    maxc = int(round(255 * (lit + 0.5*chroma)))
    if 0 <= hue < 1:
        # Red to Yellow
        return to_tag(maxc, midc, minc)
    elif 1 <= hue < 2:
        # Yellow to Green
        return to_tag(midc, maxc, minc)
    elif 2 <= hue < 3:
        # Green to Cyan
        return to_tag(minc, maxc, midc)
    elif 3 <= hue < 4:
        # Cyan to Blue
        return to_tag(minc, midc, maxc)
    elif 4 <= hue < 5:
        # Blue to Magenta
        return to_tag(midc, minc, maxc)
    elif 5 <= hue < 6:
        # Magenta to Red
        return to_tag(maxc, minc, midc)
    else:
        # Invalid Values
        return u'<c=#000000>'

def boombox(intext):
    # The base hue, used for the boombox.
    base = uniform(0, 360)
    # The boombox sound needs a hue that is visibly different
    # from the boombox body hue, so generate a random hue that
    # differs at least by 60 degrees of hue.
    hues = [(uniform(base - 120, base + 120) + 180) % 360, base]
    # The color tags that will be used.
    colortag = [
        to_rgb(
            hue,
            # Saturation range
            uniform(0.85, 1.00),
            # Value range 
            uniform(0.45, 0.70),
            )
        for hue in hues
        ]
    # The boombox text, now decorated with its tags.
    return (
        intext
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
