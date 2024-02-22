
#import requests
import os
#import shutil
import time
#from datetime import date
#import openpyxl
#import sys
#import datetime
import json

SDK_info_array = ["", "", "", "", ""]

def save_json_to_text(json_file, text_file, start_line, end_line):
    """
    Saves lines from a JSON file to a text file, line by line, preserving indentation.
    Handles empty lines and varying indentation levels.

    Args:
        json_file (str): Path to the JSON file.
        text_file (str): Path to the output text file.
        start_line (int): Line number to start from (1-based indexing).
        end_line (int): Line number to end at (inclusive, 1-based indexing).

    Raises:
        ValueError: If start or end line is invalid.
        IOError: If there's an error reading or writing files.
    """
    with open(json_file, 'r') as f:
        lines = f.readlines()

    if start_line < 1 or start_line > len(lines):
        raise ValueError("Invalid start line number: {}".format(start_line))
    if end_line < start_line or end_line > len(lines):
        raise ValueError("Invalid end line number: {}".format(end_line))

    with open(text_file, 'w') as f:
        current_indent = 0  # Start with no indentation
        for line in lines[start_line - 1:end_line]:
            if line.strip():  # Handle non-empty lines
                # Calculate actual indentation based on spaces
                indent = len(line) - len(line.lstrip())
                f.write(' ' * indent + line.strip() + '\n')
                current_indent = indent  # Update for subsequent lines
            else:  # Handle empty lines
                f.write('\n')  # Preserve empty lines if needed

def insert_text_into_json(target_file, file_to_insert, line_number):
    """Inserts data from a file into a JSON file above the specified line number, line by line.
    Args:
        target_file (str): Path to the target JSON file.
        file_to_insert (str): Path to the file containing the data to insert.
        line_number (int): The line number above which to insert the data (1-based indexing).

    Raises:
        ValueError: If the line number is invalid or the target file is empty.
        IOError: If there's an error reading or writing the files.
    """
    with open(target_file, 'r+') as f:
        lines = f.readlines()

        if line_number < 1 or line_number > len(lines):
            raise ValueError("Invalid line number: {}".format(line_number))

        with open(file_to_insert, 'r') as insert_file:
            insert_lines = insert_file.readlines()

            # Preserve indentation of the target file
            indent_level = lines[line_number - 1].count(' ')

            # Insert each line with proper indentation
            for line in insert_lines:
                insert_line = ' ' * indent_level + line.rstrip('\n') + '\n'
                lines.insert(line_number - 1, insert_line)
                line_number += 1  # Adjust for added lines

        # Rewrite the target file with the updated content
        f.seek(0)
        f.truncate()
        f.writelines(lines)

def replace_spaces_with_tabs_specific_lines(input_file, output_file, lines_to_replace, num_spaces=1, replace_leading_spaces=True):
    """
    Replaces spaces with tabs in specific lines of a text file, keeping spaces in other lines.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output text file.
        lines_to_replace (list[int]): List of line numbers to replace spaces with tabs (1-based indexing).
        num_spaces (int, optional): Number of spaces to replace with one tab. Defaults to 4.
        replace_leading_spaces (bool, optional): Whether to replace leading spaces. Defaults to False.
    """
    with open(input_file, 'r') as fin, open(output_file, 'w') as fout:
        line_number = 0
        for line in fin:
            line_number += 1
            # Convert line_number to a list or set before checking membership
            if line_number in [lines_to_replace]:  # Use a list containing only line_number
                if replace_leading_spaces:
                    # Replace all spaces in specified lines
                    new_line = line.replace(' ', '\t', num_spaces)
                else:
                    # Replace non-leading spaces in specified lines
                    new_line = line.lstrip().replace(' ', '\t', num_spaces)
            else:
                # Keep spaces in other lines
                new_line = line
            fout.write(new_line)

def replace_line_data(input_file, output_file, target_line_number, new_data, match_whole_line=True):
    """
    Replaces data in a specific line of a text file.

    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to the output text file (optional).
        target_line_number (int): The line number to replace (1-based indexing).
        new_data (str): The replacement data.
        match_whole_line (bool, optional): Whether to match the entire line for replacement.
            Defaults to False.

    Raises:
        ValueError: If the target line number is invalid or the file cannot be read/written.
    """

    try:
        with open(input_file, 'r') as fin:
            lines = fin.readlines()

        if target_line_number < 1 or target_line_number > len(lines):
            raise ValueError("Invalid target line number:", target_line_number)

        modified_line = lines[target_line_number - 1]

        if match_whole_line:
            new_line = new_data + '\n'  # Add newline if entire line is replaced
        else:
            # Handle potential index errors and edge cases for partial replacements
            try:
                start_index = modified_line.index(new_data)  # Use new_data for the search
                end_index = start_index + len(new_data)
                new_line = modified_line[:start_index] + new_data + modified_line[end_index:]
            except ValueError:
                #print("Warning: Data not found on that line. Skipping replacement.")
                new_line = modified_line

        lines[target_line_number - 1] = new_line

        with open(output_file if output_file else input_file, 'w') as fout:
            fout.writelines(lines)

        #print(f"Line {target_line_number} replaced successfully!")

    except (IOError, ValueError) as e:
        print(f"Error: {e}")

def text_update_release_info(temp1_file_path, temp2_file_path, SDK_info_array):
    SDK_stage = SDK_info_array[0]
    SDK_version = SDK_info_array[1]
    #SDK_Repo_branch= SDK_info_array[2]
    SDK_sha= SDK_info_array[2]
    SDK_size = SDK_info_array[3]

    if SDK_stage == "E":
        today_date = time.strftime("%Y%m%d")
        SDK_version = SDK_version + "-build" + today_date
        SDK_Repo_branch = "dev"
    elif SDK_stage == "R":
        SDK_Repo_branch = "main"
    else:
        remove_file(temp1_file_path)
        remove_file(temp2_file_path)

    # 4 9 10 11 12
    # 21 26
    # 31

    replace_line_data(temp1_file_path, temp2_file_path, 4, "          \"version\": \"" + SDK_version + "\",")
    replace_line_data(temp2_file_path, temp1_file_path, 9, "          \"url\": \"https://github.com/ambiot/ambpro2_arduino/raw/" + SDK_Repo_branch + "/Arduino_package/release/ameba_pro2-" + SDK_version + ".tar.gz\",")
    replace_line_data(temp1_file_path, temp2_file_path, 10, "          \"archiveFileName\": \"ameba_pro2-" + SDK_version + ".tar.gz\",")
    replace_line_data(temp2_file_path, temp1_file_path, 11, "          \"checksum\": \"SHA-256:" + SDK_sha + "\",")
    replace_line_data(temp1_file_path, temp2_file_path, 12, "          \"size\": \"" + SDK_size + "\",")

def json_copy_release_info(json_file_path, temp1_file_path, temp2_file_path, SDK_info_array):
    save_json_to_text(json_file_path, temp1_file_path, 13, 46)
    replace_spaces_with_tabs_specific_lines(temp1_file_path, temp2_file_path, 1)
    replace_spaces_with_tabs_specific_lines(temp2_file_path, temp1_file_path, 1)

    text_update_release_info(temp1_file_path, temp2_file_path, SDK_info_array)

    insert_text_into_json(json_file_path, temp2_file_path, 13)

def remove_file(remove_file_path):
#    if os.path.exists('./Arduino_package/temp.txt'):
#        os.remove('./Arduino_package/temp.txt')
    if os.path.exists(remove_file_path):
        os.remove(remove_file_path)

def main():
    print('......Running Python!!!')

#    json_file_name = sys.argv[5]
    json_file_name = './Arduino_package/package_realtek_amebapro2_early_index.json'

    open('./Arduino_package/temp1.txt', 'w').close() #Create the file
    open('./Arduino_package/temp2.txt', 'w').close() #Create the file
    json_file_path = os.path.abspath(json_file_name)
    temp1_file_path = os.path.abspath('./Arduino_package/temp1.txt')
    temp2_file_path = os.path.abspath('./Arduino_package/temp2.txt')

#    SDK_info_array[0] = sys.argv[1]
#    SDK_info_array[1] = sys.argv[2]
#    SDK_info_array[2] = sys.argv[3]
#    SDK_info_array[3] = sys.argv[4]

    SDK_info_array[0] = "E" # "R"
    SDK_info_array[1] = "4.0.7zzzzz"
    #SDK_info_array[2] = "devzzzzz"
    SDK_info_array[2] = "8cde4d989e56a3708a5801f5f86fc60e179aaad334150045a1694df36e349e74zzzzz"
    SDK_info_array[3] = "92706326zzzzz"

    json_copy_release_info(json_file_path, temp1_file_path, temp2_file_path, SDK_info_array)

    remove_file(temp1_file_path)
    remove_file(temp2_file_path)

    print('......Done')

if __name__ == "__main__":
    main()
#    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
