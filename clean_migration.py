import os


directory = './migrations/versions'
files = os.listdir(directory)
files_migration = filter(lambda x: x.endswith('.py'), files)
files_migration_list = list(files_migration)[:]
for file_migration in files_migration_list:
    path_file_migration = os.path.join(directory, file_migration)
    path_file_migration_temp = os.path.join(directory, file_migration+"_temp")
    origine = open(path_file_migration, 'r')
    process = open(path_file_migration_temp, 'w')
    brackets = {"(": 0, ")": 0}
    flag_find = False
    while 1:
        line = origine.readline()
        if not line: break
        if line.find("op.create_table('view_") != -1:
            flag_find = True
            process.write("    pass\n")
        if line.find("op.drop_table('view_") != -1:
            flag_find = True
            process.write("    pass\n")
        if flag_find:
            for bracket in brackets:
                brackets[bracket] += line.count(bracket)
        else:
            process.write(line)
        if brackets["("] == brackets[")"]:
            flag_find = False
    origine.close()
    process.close()

for file_migration in files_migration_list:
    os.remove(os.path.join(directory, file_migration))
files = os.listdir(directory)
files_migration = filter(lambda x: x.endswith('_temp'), files)
files_migration_list = list(files_migration)[:]
for file_migration in files_migration_list:
    os.rename(os.path.join(os.path.join(directory, file_migration)), os.path.join(directory, file_migration[:-5]))

