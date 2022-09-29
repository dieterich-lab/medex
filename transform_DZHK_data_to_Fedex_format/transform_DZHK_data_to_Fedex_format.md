Fedex data pre-processing:

1. Move all data starting with the prefix 'mnpdzhk' from the directories: /home/magda/FEDEX/data_goetthingen/DZKH5 and /home/magda/FEDEX/data_goetthingen/DZKH7 
   to  /home/magda/__git__/Fedex/DZKH
   
2. Change the unit columns so that they all contain the name "einh"

3. Change the order of the columns so that the column with the unit is immediately after the value it belongs to

4. Change the commas in the DZKH files using command: awk -F'"' -v OFS='"' '{ for (i=2; i<=NF; i+=2) gsub(",", ";", $i) } 1' file > new_file.csv
mv new_file.csv > file.csv

In some files quotes contain quotes. You have to remove this quotes otherwise the command will not work:

	awk -F'"' -v OFS='"' '{ for (i=2; i<=NF; i+=2) gsub(",", ";", $i) } 1' mnpdzhk7lq_phq_d_DZHK7_20220810-113946.csv > check.csv

	4awk -F'"' -v OFS='"' '{ for (i=2; i<=NF; i+=2) gsub(",", ";", $i) } 1' mnpdzhk7herz_haemo_DZHK7_20220810-113946.csv > check.csv

5. Run the python script 'change_format', which: 
	1. merges all data 
	2. changes commas in values to periods
	3. changes entity names by adding entities to them
	4. selects only harmonized elements
	5. changes visit_id to names: baseline, follow up
	6. creates entites.csv and dataset.csv files