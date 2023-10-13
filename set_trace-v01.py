import sys
from math import sqrt
import math
import pandas as pd
import os


class execution_path():
    def __init__(self):
        self.linenos_nonfaulty = {}  # none faulty line number
        self.linenos_faulty = {}    # faulty line number
        self.linenos_sum = {}
        self.exec_result = []
        self.Ochiai_suspiciousness = {} # every line suspiciousness score by Ochiai formula
        self.Tarantula_suspiciousness = {}  # every line suspiciousness score by Tarantula formula
        self.total_failed = 0
        self.total_passed = 0
        self.line_temp = []
        self.whole_activities = []
        self.test_case_alpha4 = [[[4, 4, 8, 9, 10], 1, "f"], [[4, 5, 8, 1, 7], 0, "t"], [[1, 6, 4, 3, 2], 1, "t"],
                                 [[3, 3, 4, 3, 3], 1, "t"], [[8, 7, 6, 5, 4], 1, "f"], [[7, 7, 7, 3, 7], 1, "t"],
                                 [[7, 8, 9, 4, 2], 0, "t"]]  # test suite for alpha4 function

    def traceit(self, frame, event, arg):
        if event == "line":

            lineno = frame.f_lineno

            if lineno not in self.line_temp:
                self.line_temp.append(lineno)

            if lineno in self.linenos_sum:

                self.linenos_sum[lineno] += 1
            else:
                self.linenos_sum[lineno] = 1

        return self.traceit

    def trace_back(self, frame, event, arg):  # neutralize "traceit" effects
        if event == "line":
            pass
        return self.trace_back

    @staticmethod
    def alpha4(array: list, type: int):
        arrayLenght = len(array)
        is_sorted = True
        sum = 0
        sum_square = 0
        Average = 0
        arr_norm_sd = list()
        arr_norm = list()
        for i in range(0, arrayLenght):
            arr_norm_sd.append(array[i])
            arr_norm.append(array[i])
        for i in range(0, len(arr_norm_sd) - 1):
            if arr_norm_sd[i] < arr_norm_sd[i + 1]:
                is_sorted = False
                break
        if not is_sorted:
            for i in range(0, arrayLenght - 1):
                for j in range(0, arrayLenght - i - 1):
                    if (arr_norm[j] > arr_norm[j + 1]):
                        temp = arr_norm[j]
                        arr_norm[j] = arr_norm[j + 1]
                        arr_norm[j + 1] = temp
            Range = arr_norm[arrayLenght - 1] - arr_norm[0]
            for i in range(0, arrayLenght):
                sum = sum + arr_norm_sd[i]
            avrage = sum / arrayLenght
            for number in arr_norm_sd:
                sum_square = sum_square + ((number - avrage) * (number - avrage))
            SD = math.sqrt(sum_square / (arrayLenght - 1))
            if type == 0:
                for i in (0, arrayLenght - 1):
                    arr_norm_sd[i] = ((array[i] - avrage) / SD)
                return arr_norm_sd
            else:
                for i in range(0, arrayLenght):
                    arr_norm[i] = array[i] - array[0] / (Range + 1)
                return arr_norm

    def Tarantula(self, line_number, passed, failed):
        self.Tarantula_suspiciousness[line_number] = (failed / self.total_failed) / (
                (failed / self.total_failed) + (passed / self.total_passed))

    def Ochiai(self, line_number, passed, failed):
        self.Ochiai_suspiciousness[line_number] = failed / sqrt(self.total_failed * (passed + failed))

    def extract_info(self):
        sys.settrace(self.traceit)
        ind = 1
        for i in self.test_case_alpha4:
            result = i[2]
            self.alpha4(array=i[0], type=i[1])

            if (result == "t"):
                # exec_result[ind] = 1
                self.exec_result.append("1")
                self.total_passed += 1
                for j in self.line_temp:
                    if j in self.linenos_nonfaulty:

                        self.linenos_nonfaulty[j] += 1
                    else:
                        self.linenos_nonfaulty[j] = 1

            else:
                self.exec_result.append("0")
                self.total_failed += 1
                for h in self.line_temp:
                    if h in self.linenos_faulty:

                        self.linenos_faulty[h] += 1
                    else:
                        self.linenos_faulty[h] = 1
            self.whole_activities.append(self.line_temp)
            self.line_temp = []
            ind += 1
        print(self.whole_activities)
        print(self.linenos_sum)
        sys.settrace(self.trace_back)  # neutralize "traceit" effects
        first_line = min(self.linenos_sum)
        last_line = max(self.linenos_sum)
        col_numbers = len(self.test_case_alpha4)
        rows_number = last_line - first_line + 1

        for i in self.linenos_sum.copy():
            passed_no = 0
            failed_no = 0
            if i in self.linenos_nonfaulty:
                passed_no = self.linenos_nonfaulty[i]

            if i in self.linenos_faulty:
                failed_no = self.linenos_faulty[i]

            self.Ochiai(i, passed_no, failed_no)
            self.Tarantula(i, passed_no, failed_no)

        self.matrix = []

        for i in range(rows_number + 1):
            new = []
            for j in range(col_numbers + 1):
                new.append(0)
            self.matrix.append(new)

        for m in range(1, col_numbers + 1):
            self.matrix[0][m] = m
        self.matrix[0][0] = 0

        for n in range(rows_number):
            self.matrix[n + 1][0] = first_line + n

        ind = 1
        for i in self.whole_activities:
            for j in i:

                for k in self.matrix:
                    if (k[0] == j):
                        ex_ind = j - (first_line - 1)
                        self.matrix[ex_ind][ind] = 1
            ind += 1

        self.exec_result.insert(0, "result")
        self.matrix[0].append("tarantula")
        self.matrix[0].append("Ochiai")

        for i, j in zip(range(first_line, first_line + rows_number), range(rows_number)):
            if i in self.Tarantula_suspiciousness:
                self.matrix[j + 1].append(self.Tarantula_suspiciousness[i])
                self.matrix[j + 1].append(self.Ochiai_suspiciousness[i])
        self.matrix.append(self.exec_result)
        self.df = pd.DataFrame(self.matrix).to_string(index=True)

    def export_data(self):
        pd.DataFrame(self.matrix).to_excel("output_matrix.xlsx")
        pd.DataFrame(self.matrix).to_latex("output_matrix.tex")
        print(self.df,
              f"\n------------------------------\n \n 0 : means fault\n\n------------------------------\nEXPLANATION : \ncolumns show line numbers \n and \nrows show test_data numbers\n 1 : means related line number execute with the test_data \n 0 : means related line number does NOT execute with the test_data  \n------------------------------\n")

        print("number of time that each line has appeared in faulty and non_faulty execution has shown below : \n")
        print(
            f"NONE_FAULTY : \n {sorted(self.linenos_nonfaulty.items())} \n\n FAULTY : \n {sorted(self.linenos_faulty.items())}\n\n")

    def runner(self):
        self.extract_info()
        self.export_data()


def main():
    instance = execution_path()
    instance.runner()
    print('end of the process')


if __name__ == '__main__':
    main()
