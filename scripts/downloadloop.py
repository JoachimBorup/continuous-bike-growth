debug = False

exec(open("../parameters/parameters.py").read())
exec(open("../src/path.py").read())
exec(open("../src/setup.py").read())
exec(open("../src/functions.py").read())

if __name__ == '__main__':

    print("Running 01.py")
    exec(open("01.py").read())

    print("Running 02.py")
    exec(open("02.py").read())