#!/bin/sh
python ../grammar/main.py testcases.txt > test_out.txt
grep -e "xdotool" -e "Error:" test_out.txt > commands.txt
diff commands.txt testcases_expected_linux.txt
rm test_out.txt commands.txt
