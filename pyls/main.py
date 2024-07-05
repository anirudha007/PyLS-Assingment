import json
import argparse
from datetime import datetime

JSON_FILENAME = 'structure.json'


SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB']


def print_directory_contents_iterative(data, path=""):
    stack = [(data, 0)]  # Stack to hold tuples of (current_data, current_indent_level)
    while stack:
        current_data, indent = stack.pop()
        # print("current data", current_data)
        # print("index", indent)
        if 'contents' in current_data and indent == 0:
            if path:
                print(path)
            else:
                print(current_data['name'])
            for item in reversed(current_data['contents']):
                stack.append((item, indent + 2))
        elif 'contents' in current_data and indent != 0:
            print("|" + '-' * indent + current_data['name'])
            for item in reversed(current_data['contents']):
                stack.append((item, indent + 2))
        elif 'contents' not in current_data and indent == 2:
            print('|' + '-' * indent + current_data['name'])
        else:
            print('|  |' + '-' * (indent - 2) + current_data['name'])


def load_json_file(filename):
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: '{filename}' does not contain valid JSON.")
        return None


def find_entry_by_path(data, path):
    components = path.strip('./').split('/')
    current_data = data
    for component in components:
        found = False
        if 'contents' in current_data:
            for item in current_data['contents']:
                if item['name'] == component:
                    current_data = item
                    found = True
                    break
        if not found:
            return None
    return current_data


def list_top_level_entries(data, include_hidden=False, reverse=False, sort_by_time=False, filter_option=None):
    if 'contents' in data:
        contents = data['contents']
        if sort_by_time:
            contents.sort(key=lambda x: x.get('time_modified', 0))
        if reverse:
            contents.reverse()

        if filter_option == 'dir':
            contents = [item for item in contents if 'contents' in item]
        elif filter_option == 'file':
            contents = [item for item in contents if 'contents' not in item]
        elif filter_option:
            print(f"error: '{filter_option}' is not a valid filter criteria. Available filters are 'dir' and 'file'")
            return

        for item in contents:
            name = item['name']
            if not include_hidden and name.startswith('.'):
                continue
            print(name)
    else:
        print("Error: Input JSON does not have a 'contents' field at the top level.")


def get_formatted_timestamp(timestamp):
    dt_object = datetime.fromtimestamp(timestamp)
    return dt_object.strftime("%b %d %H:%M")


def format_size(size_bytes):
    if size_bytes == 0:
        return '0 B'
    i = 0
    while size_bytes >= 1024 and i < len(SIZE_UNITS) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.1f} {SIZE_UNITS[i]}"


def list_entries_with_details(data, include_hidden=False, reverse=False, sort_by_time=False, filter_option=None):
    if 'contents' in data:
        contents = data['contents']
        if sort_by_time:
            contents.sort(key=lambda x: x.get('time_modified', 0))
        if reverse:
            contents.reverse()

        if filter_option == 'dir':
            contents = [item for item in contents if 'contents' in item]
        elif filter_option == 'file':
            contents = [item for item in contents if 'contents' not in item]
        elif filter_option:
            print(f"error: '{filter_option}' is not a valid filter criteria. Available filters are 'dir' and 'file'")
            return

        for item in contents:
            name = item['name']
            if not include_hidden and name.startswith('.'):
                continue
            permissions = item['permissions']
            size = item['size']
            formatted_size = format_size(size)
            time_modified = item['time_modified']
            formatted_time = get_formatted_timestamp(time_modified)
            print(f"{permissions} {formatted_size} {formatted_time} {name}")
    else:
        print("Error: Input JSON does not have a 'contents' field at the top level.")


def main():
    parser = argparse.ArgumentParser(description="Python implementation of custom ls command.")
    parser.add_argument('-A', action='store_true', help='All entries, with hidden ones')
    parser.add_argument('-l', action='store_true', help='use a long listing format')
    parser.add_argument('-r', action='store_true', help='reverse the order')
    parser.add_argument('-t', action='store_true', help='sort by time(oldest first)')
    parser.add_argument('--filter', help='filter by type: file or directory')
    parser.add_argument('path', nargs='?', default='', help='path to directory or file within JSON structure')
    args = parser.parse_args()

    data = load_json_file(JSON_FILENAME)
    if data:
        if args.path:
            entry = find_entry_by_path(data, args.path)
            if entry:
                if 'contents' in entry:
                    if args.l:
                        list_entries_with_details(entry, include_hidden=args.A, reverse=args.r, sort_by_time=args.t,
                                                  filter_option=args.filter)
                    else:
                        list_top_level_entries(entry, include_hidden=args.A, reverse=args.r, sort_by_time=args.t,
                                               filter_option=args.filter)
                else:
                    permissions = entry['permissions']
                    size = entry['size']
                    formatted_size = format_size(size)
                    time_modified = entry['time_modified']
                    formatted_time = get_formatted_timestamp(time_modified)
                    print(f"{permissions} {formatted_size} {formatted_time} ./{args.path}")
            else:
                print(f"error: cannot access '{args.path}': No such file or directory")
        else:
            if args.l:
                list_entries_with_details(data, include_hidden=args.A, reverse=args.r, sort_by_time=args.t,
                                          filter_option=args.filter)
            else:
                list_top_level_entries(data, include_hidden=args.A, reverse=args.r, sort_by_time=args.t,
                                       filter_option=args.filter)
    # if you want to print the whole structrised output of all with indentation
    # print_directory_contents_iterative(data)


if __name__ == "__main__":
    main()
