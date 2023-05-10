import sys
from math import sqrt
import pandas as pd

linenos_nonfaulty = {}
linenos_faulty = {}
linenos_sum = {}
exec_result = {}
Ochiai_suspiciousness = {}
Tarantula_suspiciousness = {}
total_failed = 0
total_passed = 0
line_temp = []
whole_activities = []
# test_cases_test = [[1,0],[6,12],[3,2],[9,18],[12,24],[0,-1]]
test_cases_getImpact =[[[4,1,3],4],[[7,6,3],7],[[6,3,3],6],[[2,1,3],2],[[3,2,3],3],[[9,7,3],9],[[8,3,2],(8/3)],[[9,2,2],(9/2)],[[6,8,3],8],[[7,6,1],13],[[6,12,3],12],[[8,9,3],9]]


def traceit(frame, event, arg):

    if event == "line":

        lineno = frame.f_lineno

        line_temp.append(lineno)

        if lineno in linenos_sum:
            
            linenos_sum[lineno] +=1
        else:
            linenos_sum[lineno] = 1

    return traceit


def getImpact(a,b,c):
    res = 0
    div = 1
    sum = a+b
    if (a > 0) and (b > 0):
        div = a/b
    max = b
    if a > b:
        max = b
    if c == 1:
        res = sum
    if c == 2:
        res = div
    if c == 3:
        res = max
    return res
# def test(x):
#     if(x>5):
#         return(2*x)
#     else:
#         return(x-2)


def Tarantula(line_number,passed,failed):
    Tarantula_suspiciousness[line_number] = (failed/total_failed) / ((failed/total_failed) + (passed/total_passed))


def Ochiai(line_number,passed,failed):

    Ochiai_suspiciousness[line_number] = failed / sqrt(total_failed*(passed+failed))


sys.settrace(traceit)

"""for i in test_cases_test:   ----------------------------->   uncomment for check the "test" function  -----
    result = test(i[0])
    if(i[1] == result):
        total_passed+=1
        for j in line_temp:
            if j in linenos_nonfaulty:

                linenos_nonfaulty[j] += 1
            else:
                linenos_nonfaulty[j] = 1
    else:
        total_failed+=1
        for j in line_temp:
            if j in linenos_faulty:

                linenos_faulty[j] += 1
            else:
                linenos_faulty[j] = 1
    line_temp = []"""
ind = 1
for i in test_cases_getImpact:
    result = getImpact(i[0][0], i[0][1], i[0][2])

    if i[1] == result:
        exec_result[ind] = 1
        total_passed += 1
        for j in line_temp:
            if j in linenos_nonfaulty:

                linenos_nonfaulty[j] += 1
            else:
                linenos_nonfaulty[j] = 1

    else:
        exec_result[ind] = 0
        total_failed += 1
        for h in line_temp:
            if h in linenos_faulty:

                linenos_faulty[h] += 1
            else:
                linenos_faulty[h] = 1
    whole_activities.append(line_temp)
    line_temp = []
    ind += 1
rows_number = len(linenos_sum)
col_numbers = len(test_cases_getImpact)
li = sorted(linenos_sum.items())
first_line = li[0][0]

for i in linenos_sum.copy():
    passed_no = 0
    failed_no = 0
    if i in linenos_nonfaulty:
        passed_no = linenos_nonfaulty[i]

    if i in linenos_faulty:
        failed_no = linenos_faulty[i]

    Ochiai(i,passed_no,failed_no)
    Tarantula(i,passed_no,failed_no)



matrix = []

for i in range(col_numbers+1):
    new = []
    for j in range(rows_number+1):
        new.append(0)
    matrix.append(new)

for m in range(rows_number):


    matrix[0][m+1] = first_line + m
matrix[0][0] = 0

for n in range (1,col_numbers+1):
    matrix[n][0] = n


ind = 1
for i in whole_activities:
    for j in i:

            if(j in matrix[0]):

                ex_ind = j - (first_line-1)
                matrix[ind][ex_ind] = 1
    ind += 1

df = pd.DataFrame(matrix).to_string(index=False)

pd.DataFrame(matrix).to_csv("out.csv")
print(df,f"\n------------------------------\nresult for each test_data is : {exec_result} \n 0 : means fault\n\n------------------------------\nEXPLANATION : \ncolumns show line numbers \n and \nrows show test_data numbers\n 1 : means related line number execute with the test_data \n 0 : means related line number does NOT execute with the test_data  \n------------------------------\n")

print("number of time that each line appeared in faulty and non_faulty execution has shown below : \n")
print(f"NONE_FAULTY : \n {sorted(linenos_nonfaulty.items())} \n\n FAULTY : \n {sorted(linenos_faulty.items())}\n\n")
print(f" the ochiai suspiciousness is : \n\n {sorted(Ochiai_suspiciousness.items())} \n\n\n and the Tarantula suspiciousness is :\n\n {sorted(Tarantula_suspiciousness.items())} \n")
