import os,pprint
files = os.listdir(".")
filtered = [k for k in files if 'VAST' in k]
sorted_files = sorted(filtered, key=lambda item: int(item.split('_')[2]))
pprint.pprint(sorted_files)
for i in range(len(sorted_files)):
	if i != 0:
		os.system('patch ' + sorted_files[0] + ' ' + sorted_files[i])
