from abstract_utilities import *
lists = """/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/buildUi.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/collect_utils.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/detect_utils.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/endpoint_utils.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/fetch_utils.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/functions.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/logging_utils.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/prefix_utils.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/row_utils.py
/home/computron/Documents/pythonTools/modules/abstract_ide/src/abstract_ide/utils/managers/utils/mainWindow/functions/init_tabs/apiGui/APIConsole/functions/send_utils.py""".split('\n')
func_names = []
index_names=[]
for li in lists:
    filename = os.path.splitext(os.path.basename(li))[0]
    importit = f"from .{filename} import ("
    contents = read_from_file(li).split('\n')
    for line in contents:
        if line.startswith('def'):
            func_name = line.split('def ')[1].split('(')[0]
            func_names.append(func_name)
            importit+=f"{func_name},"

    index_names.append(importit[:-1]+")")    
print('\n'.join(index_names))
func_names = list(set(func_names))

for i,func_name in enumerate(func_names):
    func_names[i] = f"self.{func_name} = {func_name}"
            

print('\n'.join(func_names))
