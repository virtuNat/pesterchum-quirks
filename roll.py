#!/usr/bin/env python
import re
import random

def parse_roll_cmd(intext):
    # Assume regex to matched was a command: r'^>(.*)$'
    match = re.match(r'roll\s+(\d+)\s*d\s*(\d+)\s*(?:([-+])\s*(\d+))?\s*', intext)
    if match:
        # Grab the groups.
        ndice, nfaces, sign, mod = [group or 0 for group in match.groups()]
        # Convert number and faces of dice to integer type.
        ndice, nfaces = int(ndice), int(nfaces)
        # Apply sign to modifier.
        mod = int(mod) * -1 if sign == '-' else int(mod)
        # Calculate the rolls.
        rolls = [random.randrange(nfaces) + 1 for _ in range(ndice)]
        # Give the sum of the rolls.
        rollsum = sum(rolls)
        # Generate the text representing each roll result.
        rolltext = ' + '.join(str(roll) for roll in rolls)
        # Generate the text to be prepended.
        rollstart = 'Rolled %dd%d' % (ndice, nfaces)
        if mod:
            return (
                '%s%s%s: (%s) %s %d = %d'
                % (rollstart, sign, mod, rolltext, sign, abs(mod), rollsum + mod)
                )
        return '%s: %s = %d' % (rollstart, rolltext, rollsum)
    return intext
parse_roll_cmd.command = 'roll'
