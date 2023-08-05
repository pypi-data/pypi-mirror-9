def sanitize(time_string):
    if '-' in time_string:
        spliiter = '-'
    elif ':' in time_string:
        splitter = ':'
    else:
        return(time_string)
    (mins, sec) = time_string.split(splitter)
    return(mins + '.' + sec)
