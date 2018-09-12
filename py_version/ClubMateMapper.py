#!/usr/bin/python3

CRATE_VERTICAL = [
    0,  1,  2,  3,
    7,  6,  5,  4,
    8,  9,  10, 11,
    15, 14, 13, 12,
    16, 17, 18, 19
]

CRATE_HORIZONTAL = [
    16, 15,  8, 7, 0,
    17, 14,  9, 6, 1,
    18, 13, 10, 5, 2,
    19, 12, 11, 4, 3
]

HORIZONTAL_2x5 = [
    0, 1, 2, 3, 4,
    9, 8, 7, 6, 5,
]


class ClubMateMapper():
    def __init__(self, crate_positions, crate_orientation):
        """
        - crate_positions:
            How are crates wired inside the matrix.
        - crate_orientation:
            How are led wired inside a crate.
        """
        self.crate_positions = crate_positions
        self.crate_orientation = crate_orientation

        self.nbr_pixels = len(self.crate_orientation) * len(self.crate_positions)
        self.buffer = None
        self.reset_buffer()

    def reset_buffer(self):
        self.buffer = [0 for _ in range(self.nbr_pixels)]

    def array_position_generator(self):
        for crate in self.crate_positions:
            for position in self.crate_orientation:
                yield position + (crate * len(self.crate_orientation))

    def matrix_position_generator(self):
        for crate_x in range(2):
            for crate_y in range(5):
                for bottle_x in range((crate_x * 5), (crate_x * 5) + 5):
                    for bottle_y in range((crate_y * 4), (crate_y * 4) + 4):
                        yield (bottle_x, bottle_y)


    def map(self, matrix):
        for i, (x, y) in zip(self.array_position_generator(), self.matrix_position_generator()):
            try:
                self.buffer[i] = matrix[x][y]
            except:
                print("exception")
                print("In array : %s" % i)
                print("In matrix : %s, %s" % (x, y))

                print("Len of array : %s" % len(self.buffer))
                print("Len of matrix : (%s, %s)" % (len(matrix), len(matrix[x])))
        return self.buffer

    def map_and_transform_to_bytes_for_the_matrix(self, matrix):
        v = self.map(matrix)
        out = bytes()
        for i in range(0, len(v), 8):
            out += bytes([
                int("".join(map(str, v[i : i + 8][::-1])), 2)
            ])
        return out

    def magic_func(self, matrix):
        return self.map_and_transform_to_bytes_for_the_matrix(matrix)
