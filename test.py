import re
line='男主播小刚：嘿'
m = re.match(r"^(.*?)[：:]\s*(.*)$", line)
if m: print('asd')