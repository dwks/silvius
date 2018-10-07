#!/bin/sh
python ../grammar/main.py testcases.txt > test_out.txt
grep -e "cliclick" -e "Error:" test_out.txt > commands.txt
diff commands.txt testcases_expected_mac.txt
rm test_out.txt commands.txt
