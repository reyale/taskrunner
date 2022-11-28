

def render(path, time):
    strings = []
    strings.append(('$YYYYMMDD', time.strftime('%Y%m%d')))
    strings.append(('$YYYYMM', time.strftime('%Y%m')))
    strings.append(('$YYYY', time.strftime('%Y')))
    strings.append(('$MM', time.strftime('%m')))
    strings.append(('$DD', time.strftime('%d')))

    for string in strings:
        path = path.replace(string[0], string[1])

    return path
