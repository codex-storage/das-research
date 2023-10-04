
def getStrFromDelayRange(range):
    if range == None:
        delay = "0"
    else:
        delay = f"{range[0]}-{range[-1]}"
    return delay
