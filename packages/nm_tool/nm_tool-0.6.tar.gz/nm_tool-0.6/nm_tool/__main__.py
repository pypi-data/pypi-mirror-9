import nm_tool

def main():
    info = nm_tool.get_dict()
    if info is not None:
        from pprint import pprint
        pprint(info)
    else:
        print "Unable to parse nm-tool output"

if __name__ == '__main__':
    main()
