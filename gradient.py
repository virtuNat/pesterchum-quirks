"""
For this file to work properly, you should please follow the instructions.

Place this file in the Pesterchum quirks folder, which is usually
C:\Pesterchum\quirks for Windows.
Remember to set the file type as "All" and the extension to .py

Please read thoroughly.
If you have any questions, ask someone who knows about gradients.
"""

gradient = ['COLOR1', 'COLOR2', 'COLOR3', 'COLOR4', 'COLOR5', 'COLOR6']

"""
Put the colors you want up there, in CORRECT order. They must be in RRGGBB HEXADECIMAL format.
If you don't know what that is, look it up on Google and have your color values converted there.

You can use as many colors as you want, just note that it may get cut off if your messages and 
gradient length are both lengthy.

Remember to enclose each color value in single quotes and separate the color values with commas.
"""

def apply_gradient(intext):
    """Surrounds a message in color tags in roughly equal portions."""
    textlen = len(intext)
    gradlen = len(gradient)
    # The maximum number of additional color tags that can fit this message.
    maxcolors = ((256 - textlen) // 15) - 1
    if maxcolors < 1:
        # If the message is too long to fit a single color hex, don't bother.
        return intext
    # The set of colors to be used in the tags.
    usecolors = gradient[:
        # If message length is too small, use only as many tags as the length.
        textlen if textlen < gradlen else
        # If message length is too large, use only as many tags as can fit.
        maxcolors if maxcolors < gradlen else
        # Otherwise, use full gradient.
        gradlen
        ]
    # Break the message into roughly even chunks based on the number of colors.
    size, extra = divmod(textlen, len(usecolors))
    textchunks = [
        # If index is less than the number of extra chars, increment one char to chunk.
        intext[i*size + min(i, extra):(i+1)*size + min(i+1, extra)]
        for i in range(len(usecolors))
        ]
    # Surround each chunk with the appropriate tag and join them back together.
    outtext = ''.join(
        '<c=#%s>%s</c>' % (color, chunk)
        for color, chunk in zip(usecolors, textchunks)
        )
    return outtext

"""
Don't do anything to this part of the code unless you know what you're doing.
You'll break the gradient function.
"""

apply_gradient.command = "gradient"

"""
To use in the quirks menu:
regex replace ^(.*)$ 
and replace it with
gradient(\1)

where gradientname is the name entered in the double quotes.

Remember to click the RELOAD FUNCTIONS button
so that it will appear in the functions list
and to test if you did it right.

There will be no error messages if you edited this file correctly.
Don't forget to click FINISH then OK when you're done.
If you want to test it, use the QUIRK TEST button so
you don't flood memos or chats.
"""
