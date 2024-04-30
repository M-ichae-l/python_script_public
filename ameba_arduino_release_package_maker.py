#import requests
import os
#import shutil
import time
#from datetime import date
#import openpyxl
import sys
#import datetime
import json

SDK_info_array = ["", "", "", "", "", "", ""]
Package_name = ["TEMP.tar.gz", ""]

def string_search_and_replace(text, substring, replacement, case_sensitive=True):
    """
    Searches for a substring in a string and replaces all occurrences with a replacement string.

    Args:
        text: The string to search in.
        substring: The substring to search for.
        replacement: The string to replace the substring with.
        case_sensitive: Whether to perform a case-sensitive search (default: True).

    Returns:
        The modified string with all occurrences of the substring replaced.
    """
    if not case_sensitive:
        text = text.lower()
        substring = substring.lower()
    new_text = text

    if substring not in text:
        raise ValueError("release type and branch not match")

    index = new_text.find(substring)
    new_text = new_text[:index] + replacement + new_text[index + len(substring):]
    return new_text

def update_tag(release_type, text, substring="QC", remove="-"):
    if release_type == "E" or release_type == "R":
        if substring not in text:
            index = 5
            new_value = str(int(text[index]) + 1)
            return text[1:index] + new_value + text[index + 1:]
        else:
            index_substring = text.find(substring)
            index_remove = text.find(remove)
            return text[1:index_remove]
    else:
        raise ValueError("no match branch")

def remove_left_of_second_data(text, second_data="/"):
    """
    Finds the second occurrence of second_data from the right and removes all data to the left of it.

    Args:
        text: The string to modify.
        second_data: The data to search for (default: "A").

    Returns:
        The modified string with data to the left of the second occurrence of second_data removed.
    """

    # Reverse the string
    reversed_text = text[::-1]

    # Find the first two occurrences of second_data
    first_index = reversed_text.find(second_data)
    second_index = reversed_text.find(second_data, first_index + 1)

    # Check if the second occurrence exists
    if second_index == -1:
        return text  # Return original text if the second instance is not found

    # Calculate the index to keep in the original string
    index_to_keep = len(text) - second_index - len(second_data)

    # Return the portion of the string to the right of the second data A
    return text[index_to_keep:]

def remove_after_word(text, word="raw"):
    """
    Removes all data from the right of a specified word in a string, including the word itself.

    Args:
        text: The string to modify.
        word: The word to find and remove data after (case-sensitive).

    Returns:
        The modified string with data after the specified word removed.
    """

    # Find the index of the word
    index = text.find(word)

    # Return the portion of the string up to the index of the word + its length
    if index != -1:
        return text[:index + len(word)] + "/"  # Include the length of the word
    else:
        return text + "/"

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
    SDK_repo = SDK_info_array[0]
    SDK_release_type = SDK_info_array[1]
    SDK_tag = SDK_info_array[2]
    SDK_sha= SDK_info_array[3]
    SDK_size = SDK_info_array[4]

    SDK_https_raw = remove_after_word(SDK_info_array[5])
#    print(http_raw)

    if SDK_release_type == "E":
        today_date = time.strftime("%Y%m%d")
        SDK_tag = SDK_tag + "-build" + today_date
        SDK_Repo_branch = "dev"
    elif SDK_release_type == "R":
        if SDK_info_array[6] == "main":
            SDK_Repo_branch = "main"
        elif SDK_info_array[6] == "master":
            SDK_Repo_branch = "master"
        else:
            raise ValueError("wrong branch name main/master")
    else:
        raise ValueError("no match branch")

    # 4 9 10 11 12
    # 21 26
    # 31

    replace_line_data(temp1_file_path, temp2_file_path, 4, "          \"version\": \"" + SDK_tag + "\",")
    replace_line_data(temp2_file_path, temp1_file_path, 9, "          \"url\": \"" +SDK_https_raw + SDK_Repo_branch + "/Arduino_package/release/" + SDK_repo + "-" + SDK_tag + ".tar.gz\",")
    replace_line_data(temp1_file_path, temp2_file_path, 10, "          \"archiveFileName\": \"" + SDK_repo + "-" + SDK_tag + ".tar.gz\",")
    replace_line_data(temp2_file_path, temp1_file_path, 11, "          \"checksum\": \"SHA-256:" + SDK_sha + "\",")
    replace_line_data(temp1_file_path, temp2_file_path, 12, "          \"size\": \"" + SDK_size + "\",")

    Package_name[0] = "./Arduino_package/release/" + Package_name[0]
    Package_name[1] = "./Arduino_package/release/" + SDK_repo + "-" + SDK_tag + ".tar.gz"

def json_copy_release_info(json_file_path, temp1_file_path, temp2_file_path, SDK_info_array):
    save_json_to_text(json_file_path, temp1_file_path, 13, 51)
    replace_spaces_with_tabs_specific_lines(temp1_file_path, temp2_file_path, 1)
    replace_spaces_with_tabs_specific_lines(temp2_file_path, temp1_file_path, 1)

    text_update_release_info(temp1_file_path, temp2_file_path, SDK_info_array)

    insert_text_into_json(json_file_path, temp2_file_path, 13)

def remove_file(remove_file_path):
#    if os.path.exists('./Arduino_package/temp.txt'):
#        os.remove('./Arduino_package/temp.txt')
    if os.path.exists(remove_file_path):
        os.remove(remove_file_path)

def rename_file(old_path, new_path):
    """
    Renames a file from the old path to the new path.

    Args:
        old_path: The current path of the file.
        new_path: The desired new path of the file.

    Raises:
        OSError: If renaming fails due to various reasons.
    """
    try:
        os.rename(old_path, new_path)
    except OSError as e:
        raise OSError(f"Failed to rename file: {e}") from e

def main(input_1, input_2, input_3, input_4, input_5, input_6, input_7):
    print('......Running Python!!!')

    if input_2 == "E":
        string_search_and_replace(input_6, "dev", "dev")
    elif input_2 == "R":
        string_search_and_replace(input_6, input_7, input_7)
    else:
        raise ValueError("no match branch")

    SDK_info_array[0] = input_1 # ameba_pro2
    SDK_info_array[1] = input_2 # E

    input_3 = update_tag(input_2, input_3)
    SDK_info_array[2] = input_3 # ${{ env.LAST_TAG }}

    SDK_info_array[3] = input_4 # ${{ env.PACKAGE_SHA }}
    SDK_info_array[4] = input_5 # ${{ env.PACKAGE_SIZE }}

    input_6 = string_search_and_replace(input_6, "blob", "raw")
    SDK_info_array[5] = input_6 # json url

    SDK_info_array[6] = input_7 # main/master

    json_file_name = "." + remove_left_of_second_data(input_6)
#    print(json_file_name)

    open('./temp1.txt', 'w').close() #Create the file
    open('./temp2.txt', 'w').close() #Create the file
    json_file_path = os.path.abspath(json_file_name)
    temp1_file_path = os.path.abspath('./temp1.txt')
    temp2_file_path = os.path.abspath('./temp2.txt')

    json_copy_release_info(json_file_path, temp1_file_path, temp2_file_path, SDK_info_array)

    remove_file(temp1_file_path)
    remove_file(temp2_file_path)

    rename_file(Package_name[0], Package_name[1])

    print('......Done')

if __name__ == "__main__":
#    main()
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7])
