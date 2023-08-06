def filtertest(var):
    if var % 2 == 0:
        return True
    else:
        return False

for i in filter(filtertest, range(0,10)):
    print i
