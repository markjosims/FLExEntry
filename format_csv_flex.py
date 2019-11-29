global ready, not_ready
ready=[]
not_ready=[]

# read all lines in csv file
# save into lexemes list
def read_csv(filename):
    punct = ("\u2018", "\u2019", "\'", '\"', '\u201c', '\u201d', ".", "?", "(", ")", "[", "]", ";", ":",
        '-', '_', '\\', '/', '\ufeff')
    file = open(filename, 'r', encoding='utf8')
    header = file.readline()
    not_ready.append(header)
    ready.append(header)
    for line in file:
        lexeme = line.split(sep=",")[-1]
        retain = False
        for char in lexeme:
            if char in punct:
                retain = True
        if retain:
            not_ready.append(line)
        else:
            ready.append(line)
    file.close()


def write_csv(out_list, filename):
    file = open(filename, 'w', encoding='utf8')
    for line in out_list:
        file.write(line.strip()+'\n')
    file.close()

def main():
    read_csv("flex_spreadsheet.csv")
    write_csv(ready, "C:\\Users\\Mark\\Desktop\\to_enter.csv")
    write_csv(not_ready, "C:\\Users\\Mark\\Desktop\\to_process.csv")

main()
