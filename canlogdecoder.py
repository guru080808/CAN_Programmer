import ast
f=open('C:/GURU/vecmocon/VIM/ivec-application/Scripts/CAN_Programmer/CAN_FLASHER/out.log')
lines=f.readlines()
f.close()
for line in lines:
    if '|' in line:
        str=line.split('|')[2]
        print(ast.literal_eval(str).decode('utf-16'))
    else:
        print(line)