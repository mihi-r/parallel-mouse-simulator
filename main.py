"""Application for Parallel Mouse Simulation."""

import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

DISCOUNT_FACTOR = 0.90
DEFAULT_REWARD = 0.04

class App(QWidget):
    """Display window of the main app."""

    def __init__(self):
        """Initiate UI elements."""
        super().__init__()

        label = QLabel('Parallel Mouse Simulator')
        label.show()

def seq_cell_update(rewards, maze):
    """Sequential updating of maze cell values sequentially"""
    temp = maze.copy()
    dim = maze.shape[0]
    max_util_change = 0
    max_error = 0.00001*(1 - DISCOUNT_FACTOR)/DISCOUNT_FACTOR
    count = 0
    while True:
        for row_index in range(dim):
            for col_index in range(dim):
                if rewards[row_index, col_index] == -1*DEFAULT_REWARD:
                    dir_values = []
                    up_val = maze[row_index, col_index]
                    down_val = maze[row_index, col_index]
                    left_val = maze[row_index, col_index]
                    right_val = maze[row_index, col_index]
                    if row_index - 1 >= 0:
                        up_val = maze[row_index - 1, col_index]
                    if col_index - 1 >= 0:
                        left_val = maze[row_index, col_index - 1]
                    if row_index + 1 < dim:
                        down_val = maze[row_index + 1, col_index]
                    if col_index + 1 < dim:
                        right_val = maze[row_index, col_index + 1]
                    dir_up_val = 0.8*up_val + 0.1*left_val + 0.1*right_val
                    dir_left_val = 0.8*left_val + 0.1*up_val + 0.1*down_val
                    dir_down_val = 0.8*down_val + 0.1*left_val + 0.1*right_val
                    dir_right_val = 0.8*right_val + 0.1*up_val + 0.1*down_val
                    dir_values.append(dir_up_val)
                    dir_values.append(dir_left_val)
                    dir_values.append(dir_down_val)
                    dir_values.append(dir_right_val)
                    final_util = rewards[row_index, col_index] + DISCOUNT_FACTOR*max(dir_values)
                    temp[row_index, col_index] = final_util
                    if abs(temp[row_index, col_index] - maze[row_index, col_index]) > max_util_change:
                        max_util_change = abs(temp[row_index, col_index] - maze[row_index, col_index])
                else:
                    temp[row_index, col_index] = rewards[row_index, col_index]
        count+= 1
        # print(count)
        maze = temp.copy()
        if max_util_change < max_error:
            print(f'max util on break: {max_util_change}')
            break
        max_util_change = 0
    print(maze)
    print(count)
    


if __name__ == '__main__':
    rewards = np.zeros((20,20)) - DEFAULT_REWARD
    rewards[0,4] = 1
    rewards[1,1] = -1
    rewards[2,0] = -0.5
    rewards[3,3] = -0.5
    maze = np.zeros((20,20))
    seq_cell_update(rewards, maze)
