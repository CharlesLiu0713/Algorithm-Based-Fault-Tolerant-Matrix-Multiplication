import numpy as np
import time

# Changes iteration order (could increase speed)
row_then_col = False


# Strip data containing checksum depending on mode
def strip_abft_check_data(input_matrix, strip_mode="row"):
    if strip_mode == "row":
        return input_matrix[:, :-1]
    elif strip_mode == "col":
        return input_matrix[:-1, :]
    elif strip_mode == "all":
        return input_matrix[:-1, :-1]


# Add data to matrix for ABFT implementation
def add_abft_check_data(input_matrix, row_checks=False, col_checks=False):
    curr_shape = input_matrix.shape
    new_rows = curr_shape[0]
    new_cols = curr_shape[1]

    # Increase col count by one if adding row checks
    if row_checks:
        new_cols = new_cols + 1

    # Increase row count by one if adding col checks
    if col_checks:
        new_rows = new_rows + 1

    new_shape = (new_rows, new_cols)

    # Initialize zero matrix
    buffered_matrix = np.zeros(new_shape)

    # Copy old matrix
    for i in range(curr_shape[0]):
        for j in range(curr_shape[1]):
            buffered_matrix[i, j] = input_matrix[i, j]

    # If adding row checks
    if row_checks:
        # Append sum of original row to each row
        for i in range(curr_shape[0]):
            sum_check = sum(input_matrix[i, :])
            buffered_matrix[i, new_cols - 1] = sum_check

    # If adding col checks
    if col_checks:
        # Append sum of each col to each col
        for j in range(curr_shape[1]):
            sum_check = sum(input_matrix[:, j])
            buffered_matrix[new_rows - 1, j] = sum_check

    # If both were enabled, add double sum in corner
    if row_checks == True and col_checks == True:
        sum_check = sum(buffered_matrix[:, new_cols - 1])
        buffered_matrix[new_rows - 1, new_cols - 1] = sum_check

    return buffered_matrix


# Checks if val_2 is within a percentage error of val_1 (floats), or if they are equal
def is_in_tolerance(val_1, val_2):
    if val_1 == val_2:
        return True


# Verify that a matrix is fault free, if not, attempt correction
def abft_verify(input_matrix, row_checks=False, col_checks=False):
    mat_shape = input_matrix.shape
    num_rows = mat_shape[0]
    num_cols = mat_shape[1]

    row_errors = []
    col_errors = []

    start = time.time()
    # if enforcing row checking
    if row_checks == True:
        num_cols = num_cols - 1
    # if enforcing col checking
    if col_checks == True:
        num_rows = num_rows - 1

    # Check for errors in each row
    if row_checks == True:
        for i in range(num_rows):
            row_slice = input_matrix[i, :-1]
            test_sum = sum(row_slice)
            check_sum = input_matrix[i, -1]
            if is_in_tolerance(test_sum, check_sum) == False:
                print("\tError detected in row %s" % (i))
                row_errors.append(i)

    # Check for errors in each row
    if col_checks == True:
        for j in range(num_cols):
            col_slice = input_matrix[:-1, j]
            test_sum = sum(col_slice)
            check_sum = input_matrix[-1, j]
            if is_in_tolerance(test_sum, check_sum) == False:
                print("\tError detected in col %s" % (j))
                col_errors.append(j)

    # Check that checksums are consistent (corner data)
    if col_checks == True and row_checks == True:

        # Check row checks
        row_slice = input_matrix[-1, :-1]
        test_sum = sum(row_slice)
        check_sum = input_matrix[-1, -1]
        if is_in_tolerance(test_sum, check_sum) == False:
            if num_rows not in row_errors:
                # print("Error detected in row %s" % (num_rows))
                print("\tError detected in row %s (checksum)" % (num_rows))
                row_errors.append(num_rows)

        # Check col checks
        col_slice = input_matrix[:-1, -1]
        test_sum = sum(col_slice)
        check_sum = input_matrix[-1, -1]
        if is_in_tolerance(test_sum, check_sum) == False:
            if num_cols not in col_errors:
                # print("Error detected in col %s" % (num_cols))
                print("\tError detected in col %s (checksum)" % (num_cols))
                col_errors.append(num_cols)

    end = time.time()
    print("Error Detection completed in %s" % str(end - start))

    # Return original matrix if no errors detected
    if len(row_errors) == 0 and len(col_errors) == 0:
        return input_matrix
    # Correct if necessary
    else:
        new_matrix = abft_correct(input_matrix, row_errors, col_errors)

        return new_matrix


# Conducts matrix multiplication on an ABFT encoded matrices
def multiply_matrix_abft(matrix_1_in, matrix_2_in):
    # Strip down coding for multiplication
    matrix_1 = strip_abft_check_data(matrix_1_in, strip_mode="row")
    matrix_2 = strip_abft_check_data(matrix_2_in, strip_mode="col")

    shape_1 = matrix_1.shape
    shape_2 = matrix_2.shape

    # Verify valid shape
    assert shape_1[1] == shape_2[0], "Matrix Shapes not multipliable!"

    new_shape = (shape_1[0], shape_2[1])

    result_matrix = np.zeros(new_shape)

    # Begin multiplication
    # Iterate over rows
    if row_then_col:

        for i in range(new_shape[0]):
            # Iterate over cols (elements of rows)
            for j in range(new_shape[1]):
                old_row = matrix_1[i, :]
                old_col = matrix_2[:, j]

                # Calculate dot product of row and col in corresponding matrices
                prod_sum = dot_product(old_row, old_col)

                result_matrix[i, j] = prod_sum

    else:
        for j in range(new_shape[1]):
            # Iterate over cols (elements of rows)
            for i in range(new_shape[0]):
                old_row = matrix_1[i, :]
                old_col = matrix_2[:, j]

                # Calculate dot product of row and col in corresponding matrices
                prod_sum = dot_product(old_row, old_col)

                result_matrix[i, j] = prod_sum

    return result_matrix


# Calculates dot product of row and col of two matrices
def dot_product(row, col):
    assert len(row) == len(col), "Invalid size for dot product"

    prod_sum = 0

    for i in range(len(row)):
        prod_sum += row[i] * col[i]

    return prod_sum
