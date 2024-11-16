"""
In search.py, you will implement Backtracking and AC3 searching algorithms
for solving Sudoku problem which is called by sudoku.py
"""
import time 
from csp import *
from copy import deepcopy
from collections import deque
import util



def Backtracking_Search(csp):
    """
    Backtracking search initializes the initial assignment
    and calls the recursive backtrack function
    """
    # startpuzle = time.time()
    # sudoku = csp  # Sử dụng đối tượng csp đã được khởi tạo từ sudoku.py
    # solved = Recursive_Backtracking({}, sudoku)  # Truyền đối tượng csp
    # print("The board takes", time.time() - startpuzle, "seconds")
    
    # if solved != "FAILURE":
    #     print("After solving: ")
    #     display(solved)
    #     return solved
    # else:
    #     print("No solution found for the puzzle.")
    #     return "FAILURE"
    return Recursive_Backtracking({}, csp)


def Recursive_Backtracking(assignment, csp):
    """
    The recursive function which assigns value using backtracking
    """
    # # If assignment is complete, return it (success).
    # if isComplete(assignment):
    #     return assignment
    
    # # Select the next unassigned variable to assign a value to.
    # var = Select_Unassigned_Variables(assignment, csp)
    # domain = deepcopy(csp.values)


    # # Try each value in the domain of the variable.
    # for value in csp.values[var]:
    #     if isConsistent(var, value, assignment, csp):
    #         assignment[var] = value
    #         inferences = {}
    #         inferences = Inference(assignment, inferences, csp, var, value)
    #         if inferences != "FAILURE":
    #             result = Recursive_Backtracking(assignment, csp)
    #             if result != "FAILURE":
    #                 return result

    #         del assignment[var]
    #         csp.values.update(domain)

    # return "FAILURE"
#-----------------------------------------------------------
    """
    The recursive function which assigns value using backtracking and AC3
    """
    # If assignment is complete, return it (success).
    if isComplete(assignment):
        return assignment

    # Select the next unassigned variable to assign a value to.
    var = Select_Unassigned_Variables(assignment, csp)
    domain = deepcopy(csp.values)

    # Try each value in the domain of the variable.
    for value in csp.values[var]:
        if isConsistent(var, value, assignment, csp):
            # Assign the value and make inferences.
            assignment[var] = value

            # Perform inference using AC3
            csp.values[var] = value  # Update the domain of var
            ac3_result = AC3(csp)   # Enforce arc consistency

            if ac3_result != "FAILURE":  # If AC3 succeeds
                result = Recursive_Backtracking(assignment, csp)
                if result != "FAILURE":
                    return result

            # Undo the assignment and restore the domain if failure occurs
            del assignment[var]
            csp.values.update(domain)

    return "FAILURE"


def Inference(assignment, inferences, csp, var, value):
    """
    Forward checking using concept of Inferences
    """

    inferences[var] = value

    for neighbor in csp.peers[var]:
        if neighbor not in assignment and value in csp.values[neighbor]:
            if len(csp.values[neighbor]) == 1:
                return "FAILURE"

            remaining = csp.values[neighbor] = csp.values[neighbor].replace(value, "")

            if len(remaining) == 1:
                flag = Inference(assignment, inferences, csp, neighbor, remaining)
                if flag == "FAILURE":
                    return "FAILURE"

    return inferences

def Order_Domain_Values(var, assignment, csp):
    """
    Returns string of values of given variable
    """
    return csp.values[var]

def Select_Unassigned_Variables(assignment, csp):
    """
    Selects new variable to be assigned using minimum remaining value (MRV)
    """
    unassigned_variables = dict((squares, len(csp.values[squares])) for squares in csp.values if squares not in assignment.keys())
    mrv = min(unassigned_variables, key=unassigned_variables.get)
    return mrv

def isComplete(assignment):
    return set(assignment.keys()) == set(squares)

def isConsistent(var, value, assignment, csp):
    """
    Check if assignment is consistent
    """
    for neighbor in csp.peers[var]:
        if neighbor in assignment.keys() and assignment[neighbor] == value:
            return False
    return True

def forward_checking(csp, assignment, var, value):
    csp.values[var] = value
    for neighbor in csp.peers[var]:
        csp.values[neighbor] = csp.values[neighbor].replace(value, '')

def display(values):
    # """
    # Display the solved sudoku on screen
    # """
    # for row in rows:
    #     if row in 'DG':
    #         print("-------------------------------------------")
    #     for col in cols:
    #         if col in '47':
    #             print(' | ', values[row + col], ' ', end=' ')
    #         else:
    #             print(values[row + col], ' ', end=' ')
    #     print(end='\n')

      for row in rows:
        if row in 'DG':
            print("-------------------------------------------")
        for col in cols:
            cell = row + col
            # Nếu ô chưa có giá trị (missing key), hiển thị 'X' hoặc giá trị mặc định
            if cell in values:
                print(values[cell], ' ', end=' ')
            else:
                print('X', ' ', end=' ')
        print(end='\n')

def write(values):
    # """
    # Write the string output of solved sudoku to file
    # """
    # output = ""
    # for variable in squares:
    #     output = output + values[variable]
    # return output

    """
    Write the string output of solved sudoku to file
    """
    output = ""
    for variable in squares:
         output = output + values[variable]
        # if variable in values:
        #     output = output + values[variable]
        # else:
        #     print(f"Missing key: {variable}")  # Debugging missing keys
    return output
"""
------------------------------------------------------------------------------------------
"""
def AC3(csp):
    """
    AC-3 algorithm to enforce arc consistency on the CSP.
    It processes all arcs and reduces domains if necessary.
    """
    queue = deque([(x, y) for x in csp.variables for y in csp.peers[x]])

    while queue:
        (xi, xj) = queue.popleft()

        # If xi's domain is reduced, check its neighbors
        if revise(csp, xi, xj):
            # If xi's domain is empty, no solution
            if len(csp.values[xi]) == 0:
                return "FAILURE"

            # Add all neighbors of xi back to the queue
            for xk in csp.peers[xi]:
                if xk != xj:
                    queue.append((xk, xi))
    return csp

def revise(csp, xi, xj):
    """
    Revise the domain of variable xi by removing values that are not consistent
    with variable xj.
    Returns True if the domain of xi is reduced.
    """
    revised = False
    for value in csp.values[xi]:
        # If there is no valid value for xi that satisfies the constraint with xj, remove it
        if not any(isConsistent(xi, value, {xi: value, xj: other_value}, csp) for other_value in csp.values[xj]):
            csp.values[xi] = csp.values[xi].replace(value, '')
            revised = True
    return revised