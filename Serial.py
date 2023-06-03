import numpy as np
from time import time


class ABFTImplement():

    # Implement
    def Implement(self):
        # Record the start time of implementation
        start_time = time()

        # Read matrix data in csv file using numpy package
        matrix_1 = np.loadtxt('matrix1.csv', delimiter=',', dtype=int, encoding='utf-8-sig')
        matrix_2 = np.loadtxt('matrix2.csv', delimiter=',', dtype=int, encoding='utf-8-sig')
        read_matirx_end_time = time()
        # Get duration of read.
        print(f'Reading matrix time is: {(read_matirx_end_time - start_time):.3}s')

        checksum_start_time = time()
        check_matrix_1 = self.Checksum(matrix=matrix_1, row_checksum=True, col_checksum=True)
        check_matrix_2 = self.Checksum(matrix=matrix_2, row_checksum=True, col_checksum=True)
        checksum_end_time = time()
        # Get duration of checksum.
        print(f'Checksum matrix time is: {(checksum_end_time - checksum_start_time):.3}s')

        ABFT_detection_start_time = time()
        detected_matrix_1 = self.ABFTDetection(matrix=check_matrix_1, row_checksum=True, col_checksum=True)
        detected_matrix_2 = self.ABFTDetection(matrix=check_matrix_2, row_checksum=True, col_checksum=True)
        ABFT_detection_end_time = time()
        # Get duration of detection.
        print(f'Detection and correction time is: {(ABFT_detection_end_time - ABFT_detection_start_time):.3}s')

        ABFT_multiplication_start_time = time()
        multiplied_matrix = self.ABFTMultiplication(matrix_1=detected_matrix_1, matrix_2=detected_matrix_2)
        ABFT_multiplication_end_time = time()
        # Get duration of multiplication.
        print(f'Matrix multiplication time is: {(ABFT_multiplication_end_time - ABFT_multiplication_start_time):.3}s')

        Inject_error_start_time = time()
        multiplied_matrix = self.Inject_error(multiplied_matrix=multiplied_matrix)
        Inject_error_end_time = time()
        # Get duration of injecting error.
        print(f'The injecting error time is: {Inject_error_end_time - Inject_error_start_time}')

        ABFT_detection_start_time = time()
        multiplied_matrix = self.ABFTDetection(matrix=multiplied_matrix, row_checksum=True, col_checksum=True)
        ABFT_detection_end_time = time()
        # Get duration of detection.
        print(f'Detection and correction time is: {(ABFT_detection_end_time - ABFT_detection_start_time):.3}s')

        Generate_matrix_start_time = time()
        correct_multiplied_matrix = np.matrix(matrix_1) * np.matrix(matrix_2)
        test_matrix = multiplied_matrix[:-1, :-1]
        matrix_norm = np.linalg.norm(correct_multiplied_matrix - test_matrix)
        print(f'the error matrix norm is: {matrix_norm}')

        # Write matrix in a csv file and output this csv file using numpy pakage
        np.savetxt('multiplied_matrix.csv', multiplied_matrix, delimiter=',', newline='\n', fmt='%d',
                   encoding='utf-8-sig')
        np.savetxt('test_matrix.csv', test_matrix, delimiter=',', newline='\n', fmt='%d', encoding='utf-8-sig')
        Generate_matrix_end_time = time()
        print(f'Generating matrix time is: {(Generate_matrix_end_time - Generate_matrix_start_time):.3}s')
        end_time = time()
        print(f'The total time is: {(end_time - start_time):.3}s')

    # Perform checksum encoding to matrix
    def Checksum(self, matrix, row_checksum=False, col_checksum=False):
        matrix_shape = matrix.shape
        check_row = matrix_shape[0]
        check_col = matrix_shape[1]

        # Increase col count by one if adding row checks
        if row_checksum is True:
            check_row += 1

        # Increase row count by one if adding col checks
        if col_checksum is True:
            check_col += 1

        # Initialize a matrix with checksum
        check_matrix = np.zeros((check_row, check_col))

        # Copy original matrix data to new matrix
        for row_index in range(matrix_shape[0]):

            # Append sum of original row to each row
            for col_index in range(matrix_shape[1]):
                check_matrix[row_index, col_index] = matrix[row_index, col_index]

        if row_checksum is True:
            # Append sum of each col to each col
            for row_index in range(matrix_shape[0]):
                check_matrix[row_index, check_col - 1] = sum(matrix[row_index, :])
        if col_checksum is True:
            for col_index in range(matrix_shape[1]):
                check_matrix[check_row - 1, col_index] = sum(matrix[:, col_index])
        if row_checksum is True and col_checksum is True:
            check_matrix[check_row - 1, check_col - 1] = sum(check_matrix[:, check_col - 1])

        return check_matrix

    # Try to detect errors. If errors are detected, then try to correct it.
    def ABFTDetection(self, matrix, row_checksum=False, col_checksum=False):
        matrix_shape = matrix.shape
        check_row = matrix_shape[0]
        check_col = matrix_shape[1]
        if row_checksum is True:
            check_col -= 1
        if col_checksum is True:
            check_row -= 1

        row_error_list = []
        col_error_list = []

        # Check for errors in each row
        if row_checksum is True:
            for row_index in range(check_row):
                if matrix[row_index, -1] != sum(matrix[row_index, :-1]):
                    row_error_list.append(row_index)
                    print(f'the error is in the {row_index} row.')

        # Check for errors in each column
        if col_checksum is True:
            for col_index in range(check_col):
                if matrix[-1, col_index] != sum(matrix[:-1, col_index]):
                    col_error_list.append(col_index)
                    print(f'the error is in the {col_index} col.')
        if row_checksum is True and col_checksum is True:
            if matrix[-1, -1] != sum(matrix[-1, :-1]):
                if check_row not in row_error_list:
                    row_error_list.append(check_row)
                    print(f'the error is in the {check_row} row.')
            if matrix[-1, -1] != sum(matrix[:-1, -1]):
                if check_col not in col_error_list:
                    col_error_list.append(check_col)
                    print(f'the error is in the {check_col} row.')

        # Return original matrix if no errors detected
        if len(row_error_list) == 0 and len(col_error_list) == 0:
            return matrix

        # Correct if necessary
        else:
            corrected_matrix = self.ABFTCorrect(matrix=matrix, row_error_list=row_error_list,
                                                col_error_list=col_error_list)
            return corrected_matrix

    # Attempt to correct errors in matrix
    def ABFTCorrect(self, matrix, row_error_list, col_error_list):
        corrected_matrix = matrix

        # Correct recoverable errors
        if len(row_error_list) == 1 and len(col_error_list) == 1:

            row_error_index = row_error_list[0]
            col_error_index = col_error_list[0]

            # Calculate correction value
            corrected_matrix[row_error_index, col_error_index] = matrix[row_error_index, col_error_index] + matrix[
                row_error_index, -1] - sum(matrix[row_error_index, :-1])

            # Inform the user which position in the matrix is being corrected
            print(f'The correted index is ({row_error_index}, {col_error_index})')
        else:
            try:
                True == False
            except ValueError:
                print('There are more than one value that needs to be corrected.')

        return corrected_matrix

    # Perform matrix multiplication for matrices with abft checksum
    def ABFTMultiplication(self, matrix_1, matrix_2):

        # remove checksum before multiplication
        matrix_1 = matrix_1[:, :-1]
        matrix_1_shape = matrix_1.shape
        matrix_2 = matrix_2[:-1, :]
        matrix_2_shape = matrix_2.shape

        try:
            matrix_1_shape[1] == matrix_2_shape[0]
        except ValueError:
            print('"The two matrix can not multiply!"')
        multiplied_matrix = np.zeros((matrix_1_shape[0], matrix_2_shape[1]))

        # Perform multiplication
        for row_index in range(matrix_1_shape[0]):
            # Iterate matrices
            for col_index in range(matrix_2_shape[1]):
                row_ = matrix_1[row_index, :]
                col_ = matrix_2[:, col_index]
                try:
                    len(row_) == len(col_)
                except ValueError:
                    print('Dot product error.')
                dot_product = 0

                # Calculate dot product of row and col in corresponding matrices
                for index in range(len(row_)):
                    dot_product += row_[index] * col_[index]
                multiplied_matrix[row_index, col_index] = dot_product

        return multiplied_matrix

    # Inject errors to the matrix with a certain probability
    def Inject_error(self, multiplied_matrix):
        multiplied_matrix_shape = multiplied_matrix.shape
        row_length = multiplied_matrix_shape[0]
        col_length = multiplied_matrix_shape[1]

        # initialize the number of error which will be injected
        error_number = 0

        if np.random.uniform(0, 1) <= 0.2:
            error_number += 1

        # Inject errors into matrices
        for index in range(error_number):
            # Randomly choose the position of matrix where error occurs
            row_random_index = np.random.randint(row_length)
            col_random_index = np.random.randint(col_length)

            # Randomly choose a corrupted value and injected it into matrix
            multiplied_matrix[row_random_index, col_random_index] = np.random.randint(-800, 800)

            print(
                f'The injected error index is: ({row_random_index}, {col_random_index}). And the injected error value is: {multiplied_matrix[row_random_index, col_random_index]}')

        return multiplied_matrix


if __name__ == '__main__':
    abft_implement = ABFTImplement()
    abft_implement.Implement()
