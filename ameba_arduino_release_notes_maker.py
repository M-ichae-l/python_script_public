#import requests
import os
import shutil
import time
#from datetime import date
#import openpyxl
import sys
#import datetime
#import json

LOG_info_array = ""

def get_last_line_number(filename):
    line_number = 0
    with open(filename, 'r') as file:
        for line in file:
            line_number += 1
    if line_number > 0:
        return line_number
    else:
        raise ValueError("Invalid get_last_line_number")

def find_line_number_up(filename, data_check="#"):
    with open(filename, "r") as file:
        for line_number, line in enumerate(file, start=1):
            if line.startswith(data_check):
                return line_number
    return -1

def find_line_number_down(filename, data_check="#"):
    with open(filename, "r") as file:
        lines = file.readlines()  # Read all lines into memory
    for line_number in reversed(range(len(lines))):
        if lines[line_number].startswith(data_check):
            return line_number + 1  # Adjust for 1-based indexing
    return -1

def read_lines(filename, start_line, end_line):
    try:
        with open(filename, "r") as file:
            lines = file.readlines()
            if start_line < 1 or end_line < 1 or start_line > end_line or start_line > len(lines):
                raise ValueError("Invalid line range")
                #return []    # Invalid line range
            return lines[start_line - 1:end_line]

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return []

def write_to_last_line(filename, line_to_append):
    try:
        with open(filename, "a") as file:
            # Seek to the end of the file
            file.seek(0, 2)
            for line in line_to_append:
                file.write(f"{line}")
    except FileNotFoundError:
        print(f"Error: File '{filename}' could not be opened for writing.")

def remove_part_data_line(line, part_data, remove_direction="L", include_data="Y", plus_index=0, minus_index=0):
    index = line.find(part_data)
    if index != -1:
        if remove_direction == "L":
            if include_data == "Y":
                line = line[(index + len(part_data) + plus_index - minus_index):].strip()
            else:
                line = line[(index + plus_index - minus_index):].strip()
        elif remove_direction == "R":
            if include_data == "Y":
                line = line[:(index + plus_index - minus_index)].strip()
            else:
                line = line[:(index + len(part_data) + plus_index - minus_index)].strip()
                if part_data[-1] == " ":
                    line = line + " "
        else:
            raise ValueError("remove_part_data_line direction error")
    else:
        if part_data == "-QC":
            return line
        else:
            raise ValueError("remove_part_data_line error")
    return line

def get_time_version(filename):
    with open(filename, "r") as file:
        try:
            first_line = next(file).strip()
            first_line = remove_part_data_line(first_line, "Release ")
        except StopIteration:  # Handle an empty file
            print("The file is empty.")
    today_date = time.strftime("%Y/%m/%d") + "\n"
    return ("\n" + first_line + " - " + today_date)

def update_data_after_second_dot(target, mode=0, line_number=1):
    if mode == 0:
        with open(target, "r") as file:
            first_line = file.readlines()[line_number - 1]  # Access by index (0-based)
            parts = first_line.split(".")
            parts[2] = str(int(parts[2]) + 1)
            return ".".join(parts)
    else:
        parts = target.split(".")
        parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)

def remove_empty_lines_from_bottom(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    # Check if last line is empty and remove while it is
    while lines and not lines[-1].strip():
        lines.pop()
    # Overwrite the file with the modified lines
    with open(filename, 'w') as f:
        f.writelines(lines)

def log_release_type(filename, release_type):
    global LOG_info_array
    try:
        with open(filename, 'r') as file:
            first_line = file.readline().strip()  # Read and remove trailing newline
            if first_line[0] == "P":
                if release_type == "E":
                    LOG_info_array = "PE"
                elif release_type == "R":
                    LOG_info_array = "PR"
                else:
                    LOG_info_array = ""
            elif first_line[0] == "R":
                if release_type == "E":
                    LOG_info_array = "RE"
                elif release_type == "R":
                    LOG_info_array = "RR"
                else:
                    LOG_info_array = ""
            else:
                raise ValueError("log file error first line")
            print("LOG_info_array: " + LOG_info_array)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def tag_compare(tag_1, tag_2):
    tag_1_a = int(tag_1[0])
    tag_2_a = int(tag_2[0])
    if tag_1_a > tag_2_a:
        return [tag_1, "tag_1_input"]
    elif tag_1_a < tag_2_a:
        return [tag_2, "tag_2_log"]
    else:
        tag_1_b = int(tag_1[2])
        tag_2_b = int(tag_2[2])
        if tag_1_b > tag_2_b:
            return [tag_1, "tag_1_input"]
        elif tag_1_b < tag_2_b:
            return [tag_2, "tag_2_log"]
        else:
            tag_1_c = int(tag_1[4:].strip())
            tag_2_c = int(tag_2[4:].strip())
            if tag_1_c > tag_2_c:
                return [tag_1, "tag_1_input"]
            elif tag_1_c < tag_2_c:
                return [tag_2, "tag_2_log"]
            else:
                return [tag_1, "tag_equal"]

def tag_check(LOG_info_array, tag_input_type, tag_final_type):
    if LOG_info_array == "PE":
        if tag_input_type == "early":
            if tag_final_type == "tag_equal":
                return
            else:
                raise ValueError("Error - early release tag")
        else:
            raise ValueError("Error - early release tag")
    elif LOG_info_array == "PR":
        if tag_input_type == "early":
            if tag_final_type == "tag_equal":
                return
            else:
                raise ValueError("Error - early release tag")
        else:
            raise ValueError("Error - early release tag")
    elif LOG_info_array == "RE":
        if tag_input_type == "early":
            raise ValueError("Error - release tag")
        else:
            if tag_final_type == "tag_equal":
                return
            else:
                raise ValueError("Error - release tag")
    elif LOG_info_array == "RR":
        if tag_input_type == "early":
            raise ValueError("Error - release tag")
        else:
            if tag_final_type == "tag_equal":
                return
            else:
                raise ValueError("Error - release tag")
    else:
        raise ValueError("tag_check LOG_info_array error")

def write_release_commit_log(filename, temp_filename, reference_filename, tag_input):
    print("write_release_commit_log LOG_info_array: " + LOG_info_array)
    temp_line_number_filename_Last = get_last_line_number(filename)

    temp_lines = read_lines(reference_filename, 1, 1)
    temp_lines[0] = remove_part_data_line(temp_lines[0], "Version ")

    if tag_input.find("-QC") > 0:
        tag_input_type = "early"
    else:
        tag_input_type = "release"
    tag_input = remove_part_data_line(tag_input, "-QC", "R")
    tag_input = remove_part_data_line(tag_input, "V")
    tag_final_list = tag_compare(tag_input, temp_lines[0])
    tag_final = tag_final_list[0]
    tag_final_type = tag_final_list[1]
    tag_check(LOG_info_array, tag_input_type, tag_final_type)

    temp_lines = []
    if LOG_info_array == "PE":
#        temp_lines = read_lines(reference_filename, 1, 1)
#        temp_lines[0] = remove_part_data_line(temp_lines[0], "Version ", "R", "N")
#        temp_lines[0] = temp_lines[0] + tag_final + "\n"
#        write_to_last_line(temp_filename, temp_lines)
#        temp_lines = []

        temp_lines = "Pre Release Version " + tag_final + "\n"
        write_to_last_line(temp_filename, temp_lines)
        temp_lines = []

    elif LOG_info_array == "PR":
#        temp_lines = update_data_after_second_dot(reference_filename)
#        index = temp_lines.find("Pre ")
#        temp_lines = temp_lines[index + len("Pre "):].strip()
#        temp_lines = temp_lines + "\n"
#        write_to_last_line(temp_filename, temp_lines)
#        temp_lines = []

        tag_final = update_data_after_second_dot(tag_final, 1)
        temp_lines = "Release Version " + tag_final + "\n"
        write_to_last_line(temp_filename, temp_lines)
        temp_lines = []
        
    elif LOG_info_array == "RE":
#        temp_lines = update_data_after_second_dot(reference_filename)
#        temp_lines = "Pre " + temp_lines + "\n"
#        write_to_last_line(temp_filename, temp_lines)
#        temp_lines = []

        tag_final = update_data_after_second_dot(tag_final, 1)
        temp_lines = "Pre Release Version " + tag_final + "\n"
        write_to_last_line(temp_filename, temp_lines)
        temp_lines = []
    elif LOG_info_array == "RR":
#        temp_lines = update_data_after_second_dot(reference_filename)
#        temp_lines = temp_lines + "\n"
#        write_to_last_line(temp_filename, temp_lines)
#        temp_lines = []

        tag_final = update_data_after_second_dot(tag_final, 1)
        temp_lines = "Release Version " + tag_final + "\n"
        write_to_last_line(temp_filename, temp_lines)
        temp_lines = []
    else:
        raise ValueError("write_release_commit_log check error")

    temp_lines = get_time_version(temp_filename)
    write_to_last_line(temp_filename, temp_lines)
    temp_lines = []
    temp_lines = read_lines(filename, 1, temp_line_number_filename_Last)
    temp_lines = ["\n"] + temp_lines
    write_to_last_line(temp_filename, temp_lines)
    temp_lines = []

def write_release_log(temp_release_log, release_log, release_commit_log):
    print("write_release_log LOG_info_array: " + LOG_info_array)
    temp_lines = []

    temp_line_number_1_V = find_line_number_down(release_log, "V")
    temp_line_number_1_F = find_line_number_down(release_log, "F")
    temp_line_number_1_A = find_line_number_down(release_log, "A")
    temp_line_number_1_M = find_line_number_down(release_log, "M")
    temp_line_number_1_Last = get_last_line_number(release_log)

    temp_line_number_2_V = find_line_number_down(release_commit_log, "V")
    temp_line_number_2_F = find_line_number_down(release_commit_log, "F")
    temp_line_number_2_A = find_line_number_down(release_commit_log, "A")
    temp_line_number_2_M = find_line_number_down(release_commit_log, "M")
    temp_line_number_2_Last = get_last_line_number(release_commit_log)

    if LOG_info_array == "PE":
        # Title
        temp_lines = read_lines(release_commit_log, 1, 2)
        write_to_last_line(temp_release_log, temp_lines)
        temp_lines = []
        # Version
        temp_lines = read_lines(release_log, 3, temp_line_number_1_V)
        write_to_last_line(temp_release_log, temp_lines)
        temp_lines = []
        temp_lines = read_lines(release_commit_log, temp_line_number_2_V, temp_line_number_2_V)
        write_to_last_line(temp_release_log, temp_lines)
        temp_lines = []
        # Feature
        if read_lines(release_log, (temp_line_number_1_F + 1), (temp_line_number_1_F + 1))[0][0] == "-":
            temp_lines = read_lines(release_log, (temp_line_number_1_F - 1), (temp_line_number_1_A - 2))
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        if read_lines(release_commit_log, (temp_line_number_2_F + 1), (temp_line_number_2_F + 1))[0][0] == "-":
            temp_lines = read_lines(release_commit_log, (temp_line_number_2_F + 1), (temp_line_number_2_A - 2))
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        # API Updates
        if read_lines(release_log, (temp_line_number_1_A + 1), (temp_line_number_1_A + 1))[0][0] == "-":
            temp_lines = read_lines(release_log, (temp_line_number_1_A - 1), (temp_line_number_1_M - 2))
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        if read_lines(release_commit_log, (temp_line_number_2_A + 1), (temp_line_number_2_A + 1))[0][0] == "-":
            temp_lines = read_lines(release_commit_log, (temp_line_number_2_A + 1), (temp_line_number_2_M - 2))
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        # Misc
        if temp_line_number_1_Last > temp_line_number_1_M:
            temp_lines = read_lines(release_log, (temp_line_number_1_M - 1), temp_line_number_1_Last)
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        if temp_line_number_2_Last > temp_line_number_2_M:
            temp_lines = read_lines(release_commit_log, (temp_line_number_2_M + 1), temp_line_number_2_Last)
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
    elif LOG_info_array == "PR":
        # Title
        temp_lines = read_lines(release_commit_log, 1, 2)
        write_to_last_line(temp_release_log, temp_lines)
        temp_lines = []
        # Version
#        temp_lines = read_lines(release_log, 3, temp_line_number_1_V)
#        write_to_last_line(temp_release_log, temp_lines)
#        temp_lines = []
        temp_lines = read_lines(release_commit_log, temp_line_number_2_V, temp_line_number_2_V)
        write_to_last_line(temp_release_log, temp_lines)
        temp_lines = []
        # Feature
        if read_lines(release_log, (temp_line_number_1_F + 1), (temp_line_number_1_F + 1))[0][0] == "-":
            temp_lines = read_lines(release_log, (temp_line_number_1_F - 1), (temp_line_number_1_A - 2))
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        if read_lines(release_commit_log, (temp_line_number_2_F + 1), (temp_line_number_2_F + 1))[0][0] == "-":
            temp_lines = read_lines(release_commit_log, (temp_line_number_2_F + 1), (temp_line_number_2_A - 2))
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        # API Updates
        if read_lines(release_log, (temp_line_number_1_A + 1), (temp_line_number_1_A + 1))[0][0] == "-":
            temp_lines = read_lines(release_log, (temp_line_number_1_A - 1), (temp_line_number_1_M - 2))
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        if read_lines(release_commit_log, (temp_line_number_2_A + 1), (temp_line_number_2_A + 1))[0][0] == "-":
            temp_lines = read_lines(release_commit_log, (temp_line_number_2_A + 1), (temp_line_number_2_M - 2))
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        # Misc
        if temp_line_number_1_Last > temp_line_number_1_M:
            temp_lines = read_lines(release_log, (temp_line_number_1_M - 1), temp_line_number_1_Last)
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
        if temp_line_number_2_Last > temp_line_number_2_M:
            temp_lines = read_lines(release_commit_log, (temp_line_number_2_M + 1), temp_line_number_2_Last)
            write_to_last_line(temp_release_log, temp_lines)
            temp_lines = []
    elif LOG_info_array == "RE":
        with open(temp_release_log, "w") as file:
            file.write("")
        source_path = os.path.abspath(release_commit_log)
        target_path = os.path.abspath(temp_release_log)
        shutil.copyfile(source_path, target_path)
    elif LOG_info_array == "RR":
        with open(temp_release_log, "w") as file:
            file.write("")
        source_path = os.path.abspath(release_commit_log)
        target_path = os.path.abspath(temp_release_log)
        shutil.copyfile(source_path, target_path)
    else:
        raise ValueError("write_log check error")

def remove_file(remove_file_path):
    if os.path.exists(remove_file_path):
        os.remove(remove_file_path)

def main(input_1, input_2, input_3, input_4):
    print('......Running Python!!!')

    # print(input_1) # input_1  E / R / ET
    # print(input_2) # input_2  release log path
    # print(input_3) # input_3  release commit log path
    # print(input_4) # input_4  last tag name

    if input_1 == "ET" :
        input_1 = "E"

    temp_release_commit_log_file_path = "./temp_release_commit_log.txt"
    temp_release_log_file_path =  "./temp_release_log.txt"
    release_log_file_path = input_2
    release_commit_log_file_path = input_3

    remove_empty_lines_from_bottom(input_2)
    remove_empty_lines_from_bottom(input_3)

    open(temp_release_commit_log_file_path, 'w').close() #Create the file
    open(temp_release_log_file_path, 'w').close() #Create the file

    log_release_type(release_log_file_path, input_1)

    write_release_commit_log(release_commit_log_file_path, temp_release_commit_log_file_path, release_log_file_path, input_4)

    write_release_log(temp_release_log_file_path, release_log_file_path, temp_release_commit_log_file_path)

    with open(input_2, "w") as file:
        file.write("")
    source_path = os.path.abspath(temp_release_log_file_path)
    target_path = os.path.abspath(input_2)
    shutil.copyfile(source_path, target_path)

    remove_file(temp_release_log_file_path)

    print('......Done')

if __name__ == "__main__":
#    main()
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
