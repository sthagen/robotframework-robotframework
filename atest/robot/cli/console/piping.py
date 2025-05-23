import sys


def read_all():
    fails = 0
    for line in sys.stdin:
        if "FAIL" in line:
            fails += 1
    print(f"{fails} lines with 'FAIL' found!")


def read_some():
    for line in sys.stdin:
        if "FAIL" in line:
            print("Line with 'FAIL' found!")
            sys.stdin.close()
            break


def read_none():
    sys.stdin.close()


globals()[sys.argv[1]]()
