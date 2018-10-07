@echo off
rem Run tests generating nircmd command lines.
rem For this script, no output is good. diff will output
rem all lines that are different.
rem
python ../grammar/main.py testcases.txt > test_out.txt
grep -e "nircmd" -e "Error:" test_out.txt > commands.txt
diff --strip-trailing-cr commands.txt testcases_expected_windows_englishuskeymap.txt
rm test_out.txt commands.txt
