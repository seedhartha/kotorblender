def _i(asciiBlock, intList, numVals, initialFloat=True):
    """Parse a float and integers into a numVals tuple into intList"""
    l_float = float
    l_int = int
    for line in asciiBlock:
        vals = []
        for idx in range(0, numVals):
            if numVals < 2 or idx > 0 or not initialFloat:
                try:
                    vals.append(l_int(line[idx]))
                except ValueError:
                    vals.append(l_int(l_float(line[idx])))
            else:
                vals.append(l_float(line[idx]))
        if len(vals) > 1:
            intList.append(tuple(vals))
        else:
            intList.append(vals[0])

def _f(asciiBlock, floatList, numVals):
    """Parse floats into a numVals tuple into floatList"""
    l_float = float
    for line in asciiBlock:
        vals = []
        for idx in range(0, numVals):
            vals.append(l_float(line[idx]))
        if len(vals) > 1:
            floatList.append(tuple(vals))
        else:
            floatList.append(vals[0])

def f1(asciiBlock, floatList):
    """Parse a series on floats into a list."""
    _f(asciiBlock, floatList, 1)

def f2(asciiBlock, floatList):
    """Parse a series on float tuples into a list."""
    _f(asciiBlock, floatList, 2)

def f3(asciiBlock, floatList):
    """Parse a series on float 3-tuples into a list."""
    _f(asciiBlock, floatList, 3)

def f4(asciiBlock, floatList):
    """Parse a series on float 4-tuples into a list."""
    _f(asciiBlock, floatList, 4)

def f5(asciiBlock, floatList):
    """Parse a series on float 5-tuples into a list."""
    _f(asciiBlock, floatList, 5)

def i2(asciiBlock, intList):
    l_int = int
    for line in asciiBlock:
        intList.append((l_int(line[0]), l_int(line[1])))

def i3(asciiBlock, intList, initialFloat=True):
    _i(asciiBlock, intList, 3, initialFloat)

def txt(asciiBlock, txtBlock):
    # txtBlock = ['\n'+' '.join(l) for l in aciiBlock]
    for line in asciiBlock:
        txtBlock = txtBlock + '\n' + ' '.join(line)
