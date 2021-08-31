from Definitions.fix import fix_from_directory, extract_fix
import sys


def print_features():
    print("-e <filename> [Destination] Extracts File to a Directory. Default Destination: ./extract")
    print("-b <dds folder> <fix file> Builds a fix File Using dds Textures Found in Specified Directory")


args = sys.argv
if len(args) >= 3:
    if args[1] == "-e":
        if len(args) == 3:
            args.append('extract')
        extract_fix(args[2], args[3])
    elif args[1] == "-b":
        if len(args) != 3:
            fix_from_directory(args[2], args[3])
        else:
            print_features()
    else:
        print_features()
else:
    print_features()

