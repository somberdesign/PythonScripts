
from argparse import ArgumentParser
from sys import argv, exit, stderr

parser = ArgumentParser()
parser.add_argument('-d', '--targetDirectory')
if len(argv) == 1:
    parser.print_help(stderr)
    exit(1)

args = parser.parse_args()
print(args.targetDirectory)





if __name__ == '__main__':
    pass    
    