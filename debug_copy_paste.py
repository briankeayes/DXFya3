#!/usr/bin/env python3
"""
Debug script to test AppleScript selection and copy/paste
"""

import subprocess
import time

def test_selection_copy_paste():
    """Test the selection and copy/paste logic"""
    
    print("🔄 Testing AppleScript selection and copy/paste...")
    
    # Test 1: Check if we can select all objects
    print("Test 1: Testing select all...")
    select_script = '''
    tell application "Adobe Illustrator"
        try
            tell document 1
                select all
                return "Select all completed"
            end tell
        on error errMsg
            return "Error: " & errMsg
        end try
    end tell
    '''
    
    result1 = subprocess.run(['osascript', '-e', select_script], 
                           capture_output=True, text=True, timeout=30)
    print(f"Select all result: {result1.stdout.strip()}")
    if result1.stderr.strip():
        print(f"Select all error: {result1.stderr.strip()}")
    
    # Test 2: Test copy
    print("Test 2: Testing copy...")
    copy_script = '''
    tell application "Adobe Illustrator"
        try
            copy
            return "Copy completed"
        on error errMsg
            return "Error: " & errMsg
        end try
    end tell
    '''
    
    result2 = subprocess.run(['osascript', '-e', copy_script], 
                           capture_output=True, text=True, timeout=30)
    print(f"Copy result: {result2.stdout.strip()}")
    if result2.stderr.strip():
        print(f"Copy error: {result2.stderr.strip()}")
    
    # Test 3: Create new layer and paste
    print("Test 3: Testing layer creation and paste...")
    paste_script = '''
    tell application "Adobe Illustrator"
        try
            tell document 1
                -- Create new layer
                set newLayer to make new layer
                set name of newLayer to "Test Layer"
                
                -- Move to front
                move newLayer to beginning of layers
                
                -- Select the new layer
                select layer 1
                
                -- Paste
                paste
                
                return "Paste completed"
            end tell
        on error errMsg
            return "Error: " & errMsg
        end try
    end tell
    '''
    
    result3 = subprocess.run(['osascript', '-e', paste_script], 
                           capture_output=True, text=True, timeout=30)
    print(f"Paste result: {result3.stdout.strip()}")
    if result3.stderr.strip():
        print(f"Paste error: {result3.stderr.strip()}")
    
    # Test 4: Check layer count
    print("Test 4: Checking layer count...")
    count_script = '''
    tell application "Adobe Illustrator"
        try
            return count of layers of document 1
        on error errMsg
            return "Error: " & errMsg
        end try
    end tell
    '''
    
    result4 = subprocess.run(['osascript', '-e', count_script], 
                           capture_output=True, text=True, timeout=30)
    print(f"Layer count: {result4.stdout.strip()}")

if __name__ == "__main__":
    test_selection_copy_paste()





