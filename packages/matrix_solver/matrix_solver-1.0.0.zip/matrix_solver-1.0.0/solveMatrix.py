

def getDeterminant(the_matrix, idx=-1):
    size = len(the_matrix)
    if size == 2:
        if idx < 0:
            return the_matrix[0][0]*the_matrix[1][1]-the_matrix[0][1]*the_matrix[1][0]
        elif idx == 0:
            return the_matrix[0][size]*the_matrix[1][1]-the_matrix[0][1]*the_matrix[1][size]
        elif idx == 1:
            return the_matrix[0][0]*the_matrix[1][size]-the_matrix[0][size]*the_matrix[1][0]
    det = 0
    x = 0
    while x < size:
        n = 0
        y = x
        temp = 1
        while n < size:
            if idx >= 0 and idx == y:
                temp *= the_matrix[n][size]
            else:
                temp *= the_matrix[n][y]
            n += 1
            y += 1
            if y == size:
                y = 0
        det += temp
        x += 1
        
    x = size - 1
    while x >= 0:
        n = 0
        y = x
        temp = 1
        while n < size:
            if idx >= 0 and idx == y:
                temp *= the_matrix[n][size]
            else:
                temp *= the_matrix[n][y]
            n += 1
            y -= 1
            if y < 0:
                y = size - 1
        det -= temp
        x -= 1
    return det
    

def solveMatrix(the_matrix):
    if isinstance(the_matrix, list):
        size = len(the_matrix)
        det = getDeterminant(the_matrix)
        
        for idx in range(size):
            print(idx, "=", getDeterminant(the_matrix, idx)/det)
            
    else:
        print("The given arugument is not a matrix")
        


    
