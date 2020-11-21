"""Application for Parallel Mouse Simulation."""
import sys
import time
from dataclasses import dataclass
from enum import Enum
import numpy as np
from numba import jit, prange
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout, \
    QTableWidget, QVBoxLayout, QPushButton, QCheckBox, QAbstractScrollArea, \
    QTableWidgetItem


DISCOUNT_FACTOR = 0.90
DEFAULT_REWARD = 0.04


class ButtonKey(Enum):
    NONE = 1
    MOUSE = 2
    REWARD = 3
    FIRE = 4
    ROCK = 5
    ERASE = 6


class CellWidgetType(Enum):
    MOUSE = 'MOUSE'
    REWARD = 'REWARD'
    FIRE = 'FIRE'
    ROCK = 'ROCK'


class CellRewards(Enum):
    MOUSE = -0.04
    REWARD = 1.0
    FIRE = -3.0
    ROCK = -0.1
    EMPTY = -0.04


class Direction(Enum):
    CURRENT = 1
    UP = 2
    RIGHT = 3
    DOWN = 4
    LEFT = 5


class MouseWidget(QLabel):
    """Image of a mouse."""
    def __init__(self):
        "Initialize widget."
        super().__init__()
        pic = QPixmap('./images/mouse.png')
        self.setScaledContents(True)
        self.setPixmap(pic)


class RewardWidget(QLabel):
    """Image of cheese."""
    def __init__(self):
        "Initialize widget."
        super().__init__()
        pic = QPixmap('./images/cheese.png')
        self.setScaledContents(True)
        self.setPixmap(pic)


class FireWidget(QLabel):
    """Image of fire."""
    def __init__(self):
        "Initialize widget."
        super().__init__()
        pic = QPixmap('./images/fire.png')
        self.setScaledContents(True)
        self.setPixmap(pic)


class RockWidget(QLabel):
    """Image of a rock."""
    def __init__(self):
        "Initialize widget."
        super().__init__()
        pic = QPixmap('./images/rock.png')
        self.setScaledContents(True)
        self.setPixmap(pic)


@dataclass
class Coordinates:    
    def __init__(self, row=0, column=0):
        self.row = row
        self.column = column


class App(QWidget):
    """Display window of the main app."""
    def __init__(self):
        """Initialize UI elements."""
        super().__init__()

        self.button_selected = ButtonKey.NONE
        self.mouse_coordinates = Coordinates()
        self.reward_coordinates = Coordinates()

        self.grid_dim = 20
        self.is_parallel_checked = False
        self.is_mouse_playing = False
        self.play_button = QPushButton("Play Mouse")
        self.time_stat_label = QLabel("Value interation time: 0s")
        self.iteration_stat_label = QLabel("Interation count: 0")
        self.mouse_grid = self.create_mouse_grid()
        self.button_panel = self.create_button_panel()
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.mouse_grid)
        self.h_box.addLayout(self.button_panel)

        self.setLayout(self.h_box)
        self.show()

    def create_button_panel(self):
        """Creates button panel for user to edit grid."""
        grid_editor_ui = self.create_grid_editor_ui()
        parallel_toggle_ui = self.create_parallel_toggle_ui()

        self.play_button.setToolTip("This will start the mouse pathing")
        self.play_button.clicked.connect(self.on_click_play)

        v_box = QVBoxLayout()
        v_box.addLayout(grid_editor_ui)
        v_box.addWidget(parallel_toggle_ui)
        v_box.addWidget(self.time_stat_label)
        v_box.addWidget(self.iteration_stat_label)
        v_box.addWidget(self.play_button)
        return v_box

    def create_grid_editor_ui(self):
        """Creates Grid Editor button UI layout."""
        grid_editor_label = QLabel()
        grid_editor_label.setText("Grid Editor")

        add_fire_button = QPushButton("Add Fire")
        add_fire_button.setToolTip("This will allow you to add a fire object to the grid")
        add_fire_button.clicked.connect(self.on_click_add_fire)

        add_rock_button = QPushButton("Add Rock")
        add_rock_button.setToolTip("This will allow you to add a rock object to the grid")
        add_rock_button.clicked.connect(self.on_click_add_rock)

        move_reward_button = QPushButton("Move Reward")
        move_reward_button.setToolTip("This will allow you to move the reward to a different spot")
        move_reward_button.clicked.connect(self.on_click_reward_move)

        move_mouse_button = QPushButton("Move Mouse")
        move_mouse_button.setToolTip("This will allow you to move the mouse to a different starting location")
        move_mouse_button.clicked.connect(self.on_click_mouse_move)

        erase_button = QPushButton("Erase")
        erase_button.setToolTip("This will allow you to remove a rock or fire object from the grid")
        erase_button.clicked.connect(self.on_click_erase)

        erase_all_button = QPushButton("Erase All")
        erase_all_button.setToolTip("This will remove all rock and fire objects from the grid")
        erase_all_button.clicked.connect(self.on_click_erase_all)

        v_box = QVBoxLayout()
        v_box.addWidget(grid_editor_label)
        v_box.addWidget(add_fire_button)
        v_box.addWidget(add_rock_button)
        v_box.addWidget(move_reward_button)
        v_box.addWidget(move_mouse_button)
        v_box.addWidget(erase_button)
        v_box.addWidget(erase_all_button)
        return v_box

    def create_parallel_toggle_ui(self):
        """Creates parallel display UI layout."""
        parallel_check_box = QCheckBox("Parallel")
        parallel_check_box.setToolTip("If checked, the algorithm will run in parallel")
        parallel_check_box.stateChanged.connect(self.on_click_parallel_check)

        return parallel_check_box

    def create_mouse_grid(self):
        """Create the grid for the mouse and the obstacles."""
        grid = QTableWidget()
        grid.setRowCount(self.grid_dim)
        grid.setColumnCount(self.grid_dim)
        grid.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        grid.horizontalHeader().hide()
        grid.verticalHeader().hide()
        grid.clicked.connect(self.on_click_grid_cell)

        for y_index in range(self.grid_dim):
            for x_index in range (self.grid_dim):
                blank_widget = QTableWidgetItem('')
                blank_widget.setWhatsThis('Blank')
                grid.setItem(x_index, y_index, blank_widget)
                grid.setColumnWidth(x_index, 30)
                grid.setRowHeight(y_index, 30)

        # Add mouse to grid
        mouse_widget = MouseWidget()
        mouse_widget.setWhatsThis(CellWidgetType.MOUSE.name)
        grid.setCellWidget(0, 0, mouse_widget)
        self.mouse_coordinates.row = 0
        self.mouse_coordinates.column = 0


        # Add reward to grid
        reward_widget = RewardWidget()
        reward_widget.setWhatsThis(CellWidgetType.REWARD.name)
        grid.setCellWidget(self.grid_dim - 1, self.grid_dim - 1, reward_widget)
        self.reward_coordinates.row = self.grid_dim - 1
        self.reward_coordinates.column = self.grid_dim - 1

        return grid

    def on_click_mouse_move(self):
        self.button_selected = ButtonKey.MOUSE

    def on_click_reward_move(self):
        self.button_selected = ButtonKey.REWARD 
        
    def on_click_add_fire(self):
        self.button_selected = ButtonKey.FIRE
    
    def on_click_add_rock(self):
        self.button_selected = ButtonKey.ROCK

    def on_click_erase(self):
        self.button_selected = ButtonKey.ERASE

    def on_click_erase_all(self):
        self.button_selected = ButtonKey.NONE

        if not self.is_mouse_playing:
            for y_index in range(self.grid_dim):
                for x_index in range (self.grid_dim):
                    cell_widget = self.mouse_grid.cellWidget(x_index, y_index)
                    if (cell_widget and
                        (cell_widget.whatsThis() == CellWidgetType.ROCK.name or
                        cell_widget.whatsThis() == CellWidgetType.FIRE.name)):
                        self.mouse_grid.removeCellWidget(x_index, y_index)

    def on_click_play(self):
        if self.is_mouse_playing:
            self.play_button.setText("Start Mouse")
            self.play_button.repaint()
            self.is_mouse_playing = False
            self.reset_grid()
        else:
            self.play_button.setText("Stop Mouse")
            self.play_button.repaint()
            self.is_mouse_playing = True

            if self.is_parallel_checked:
                current_grid_rewards = self.generate_numpy_matrix()

                start_time = time.perf_counter()
                utilities_grid, count = parallel_value_iteration(current_grid_rewards)
                total_time = time.perf_counter() - start_time

                self.time_stat_label.setText(f"Value interation time: {total_time:0.4f}s")
                self.iteration_stat_label.setText(f"Interation count: {count}")
                self.time_stat_label.repaint()
                self.iteration_stat_label.repaint()

                self.animate_mouse(utilities_grid)
            else:
                current_grid_rewards = self.generate_numpy_matrix()

                start_time = time.perf_counter()
                utilities_grid, count = seq_value_iteration(current_grid_rewards)
                total_time = time.perf_counter() - start_time

                self.time_stat_label.setText(f"Value interation time: {total_time:0.4f}s")
                self.iteration_stat_label.setText(f"Interation count: {count}")
                self.time_stat_label.repaint()
                self.iteration_stat_label.repaint()

                self.animate_mouse(utilities_grid)

    def reset_grid(self):
        for y_index in range(self.grid_dim):
            for x_index in range (self.grid_dim):
                self.mouse_grid.item(x_index, y_index).setBackground(QColor(255, 255, 255))

                cell_widget = self.mouse_grid.cellWidget(x_index, y_index)
                if cell_widget and cell_widget.whatsThis() == CellWidgetType.MOUSE.name:
                    self.mouse_grid.removeCellWidget(x_index, y_index)

        # Add mouse to grid
        mouse_widget = MouseWidget()
        mouse_widget.setWhatsThis(CellWidgetType.MOUSE.name)
        self.mouse_grid.setCellWidget(self.mouse_coordinates.row, self.mouse_coordinates.column, mouse_widget)

        # Add reward to grid
        reward_widget = RewardWidget()
        reward_widget.setWhatsThis(CellWidgetType.REWARD.name)
        self.mouse_grid.setCellWidget(self.reward_coordinates.row, self.reward_coordinates.column, reward_widget)

    def animate_mouse(self, utilities_grid):
        current_mouse_location = Coordinates(self.mouse_coordinates.row, self.mouse_coordinates.column)

        while self.is_mouse_playing:
            max_cell_value = utilities_grid[current_mouse_location.row, current_mouse_location.column]
            max_cell_direction = Direction.CURRENT

            if (current_mouse_location.row - 1 >= 0 and
                utilities_grid[current_mouse_location.row - 1, current_mouse_location.column] > max_cell_value and
                utilities_grid[current_mouse_location.row - 1, current_mouse_location.column] != CellRewards.ROCK.value):
                max_cell_value = utilities_grid[current_mouse_location.row - 1, current_mouse_location.column]
                max_cell_direction = Direction.UP
            
            if (current_mouse_location.row + 1 < self.grid_dim and
                utilities_grid[current_mouse_location.row + 1, current_mouse_location.column] > max_cell_value and
                utilities_grid[current_mouse_location.row + 1, current_mouse_location.column] != CellRewards.ROCK.value):
                max_cell_value = utilities_grid[current_mouse_location.row + 1, current_mouse_location.column]
                max_cell_direction = Direction.DOWN
            
            if (current_mouse_location.column - 1 >= 0 and
                utilities_grid[current_mouse_location.row, current_mouse_location.column - 1] > max_cell_value and
                utilities_grid[current_mouse_location.row, current_mouse_location.column - 1] != CellRewards.ROCK.value):
                max_cell_value = utilities_grid[current_mouse_location.row, current_mouse_location.column - 1]
                max_cell_direction = Direction.LEFT

            if (current_mouse_location.column + 1 < self.grid_dim and
                utilities_grid[current_mouse_location.row, current_mouse_location.column + 1] > max_cell_value and
                utilities_grid[current_mouse_location.row, current_mouse_location.column + 1] != CellRewards.ROCK.value):
                max_cell_value = utilities_grid[current_mouse_location.row, current_mouse_location.column + 1]
                max_cell_direction = Direction.RIGHT

            self.mouse_grid.item(current_mouse_location.row, current_mouse_location.column).setBackground(QColor(255, 255, 204))
            self.mouse_grid.removeCellWidget(current_mouse_location.row, current_mouse_location.column)
            new_mouse_widget = MouseWidget()
            new_mouse_widget.setWhatsThis(CellWidgetType.MOUSE.name)

            if max_cell_direction == Direction.UP:
                self.mouse_grid.setCellWidget(current_mouse_location.row - 1, current_mouse_location.column, new_mouse_widget)
                current_mouse_location = Coordinates(current_mouse_location.row - 1, current_mouse_location.column)
            elif max_cell_direction == Direction.DOWN:
                self.mouse_grid.setCellWidget(current_mouse_location.row + 1, current_mouse_location.column, new_mouse_widget)
                current_mouse_location = Coordinates(current_mouse_location.row + 1, current_mouse_location.column)
            elif max_cell_direction == Direction.LEFT:
                self.mouse_grid.setCellWidget(current_mouse_location.row, current_mouse_location.column - 1, new_mouse_widget)
                current_mouse_location = Coordinates(current_mouse_location.row, current_mouse_location.column - 1)
            elif max_cell_direction == Direction.RIGHT:
                self.mouse_grid.setCellWidget(current_mouse_location.row, current_mouse_location.column + 1, new_mouse_widget)
                current_mouse_location = Coordinates(current_mouse_location.row, current_mouse_location.column + 1)
            else:
                self.mouse_grid.setCellWidget(current_mouse_location.row, current_mouse_location.column, new_mouse_widget)
                break

            app.processEvents()
            time.sleep(0.3)

    def on_click_parallel_check(self):
        self.is_parallel_checked = not self.is_parallel_checked

    def on_click_grid_cell(self):
        if not self.is_mouse_playing:
            for grid_item in self.mouse_grid.selectedItems():
                cell_widget = self.mouse_grid.cellWidget(grid_item.row(), grid_item.column())
                
                if self.button_selected == ButtonKey.MOUSE:
                    if not cell_widget:
                        # Remove mouse widget
                        self.mouse_grid.removeCellWidget(self.mouse_coordinates.row, self.mouse_coordinates.column)

                        # Place mouse widget in selected cell
                        mouse_widget = MouseWidget()
                        mouse_widget.setWhatsThis(CellWidgetType.MOUSE.name)
                        self.mouse_grid.setCellWidget(grid_item.row(), grid_item.column(), mouse_widget)

                        # Update mouse widget coordinates
                        self.mouse_coordinates.row = grid_item.row()
                        self.mouse_coordinates.column = grid_item.column()
                elif self.button_selected == ButtonKey.REWARD:
                    if not cell_widget:
                        # Remove reward widget
                        self.mouse_grid.removeCellWidget(self.reward_coordinates.row, self.reward_coordinates.column)

                        # Place reward widget in selected cell
                        reward_widget = RewardWidget()
                        reward_widget.setWhatsThis(CellWidgetType.REWARD.name)
                        self.mouse_grid.setCellWidget(grid_item.row(), grid_item.column(), reward_widget)

                        # Update reward widget coordinates
                        self.reward_coordinates.row = grid_item.row()
                        self.reward_coordinates.column = grid_item.column()
                elif self.button_selected == ButtonKey.FIRE:
                    if not cell_widget:
                        fire_widget = FireWidget()
                        fire_widget.setWhatsThis(CellWidgetType.FIRE.name)
                        self.mouse_grid.setCellWidget(grid_item.row(), grid_item.column(), fire_widget)
                elif self.button_selected == ButtonKey.ROCK:
                    if not cell_widget:
                        rock_widget = RockWidget()
                        rock_widget.setWhatsThis(CellWidgetType.ROCK.name)
                        self.mouse_grid.setCellWidget(grid_item.row(), grid_item.column(), rock_widget)
                elif self.button_selected == ButtonKey.ERASE:
                    cell_widget = self.mouse_grid.cellWidget(grid_item.row(), grid_item.column())
                    
                    if cell_widget:
                        if cell_widget.whatsThis() == CellWidgetType.FIRE.name or cell_widget.whatsThis() == CellWidgetType.ROCK.name:
                            self.mouse_grid.removeCellWidget(grid_item.row(), grid_item.column())

    def generate_numpy_matrix(self):
        numpy_array = np.empty((self.grid_dim, self.grid_dim))

        for x in range(self.grid_dim):
            for y in range(self.grid_dim):
                cell_widget = self.mouse_grid.cellWidget(x, y)
                
                if not cell_widget:
                    numpy_array[x][y] = CellRewards.EMPTY.value
                elif cell_widget.whatsThis() == CellWidgetType.MOUSE.name:
                    numpy_array[x][y] = CellRewards.MOUSE.value
                elif cell_widget.whatsThis() == CellWidgetType.FIRE.name:
                    numpy_array[x][y] = CellRewards.FIRE.value
                elif cell_widget.whatsThis() == CellWidgetType.ROCK.name:
                    numpy_array[x][y] = CellRewards.ROCK.value
                elif cell_widget.whatsThis() == CellWidgetType.REWARD.name:
                    numpy_array[x][y] = CellRewards.REWARD.value
        return numpy_array


def seq_value_iteration(rewards):
    """Sequential updating of maze cell values sequentially."""
    dim = rewards.shape[0]
    maze = np.zeros((dim,dim))
    temp = maze.copy()
    max_util_change = 0
    max_error = 0.0001*(1 - DISCOUNT_FACTOR)/DISCOUNT_FACTOR
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
                    if row_index - 1 >= 0 and rewards[row_index - 1, col_index] != CellRewards.ROCK.value:
                        up_val = maze[row_index - 1, col_index]
                    if col_index - 1 >= 0 and rewards[row_index, col_index - 1] != CellRewards.ROCK.value:
                        left_val = maze[row_index, col_index - 1]
                    if row_index + 1 < dim and rewards[row_index + 1, col_index] != CellRewards.ROCK.value:
                        down_val = maze[row_index + 1, col_index]
                    if col_index + 1 < dim and rewards[row_index, col_index + 1] != CellRewards.ROCK.value:
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
        maze = temp.copy()
        if max_util_change < max_error:
            break
        max_util_change = 0

    return (maze, count)


@jit(parallel=True, nopython=True)
def parallel_value_iteration(rewards):
    """Parallel updating of maze cell values in parallel."""
    dim = rewards.shape[0]
    maze = np.zeros((dim,dim))
    temp = maze.copy()
    max_util_change = np.zeros(dim*dim, dtype=np.float64)
    max_error = 0.0001*(1 - DISCOUNT_FACTOR)/DISCOUNT_FACTOR
    count = 0

    while True:
        for row_index in prange(dim):
            for col_index in prange(dim):
                if rewards[row_index, col_index] == -1*DEFAULT_REWARD:
                    dir_values = np.empty((0,0), dtype=np.float64)
                    up_val = maze[row_index, col_index]
                    down_val = maze[row_index, col_index]
                    left_val = maze[row_index, col_index]
                    right_val = maze[row_index, col_index]
                    if row_index - 1 >= 0 and rewards[row_index - 1, col_index] != CellRewards.ROCK.value:
                        up_val = maze[row_index - 1, col_index]
                    if col_index - 1 >= 0 and rewards[row_index, col_index - 1] != CellRewards.ROCK.value:
                        left_val = maze[row_index, col_index - 1]
                    if row_index + 1 < dim and rewards[row_index + 1, col_index] != CellRewards.ROCK.value:
                        down_val = maze[row_index + 1, col_index]
                    if col_index + 1 < dim and rewards[row_index, col_index + 1] != CellRewards.ROCK.value:
                        right_val = maze[row_index, col_index + 1]
                    dir_up_val = 0.8*up_val + 0.1*left_val + 0.1*right_val
                    dir_left_val = 0.8*left_val + 0.1*up_val + 0.1*down_val
                    dir_down_val = 0.8*down_val + 0.1*left_val + 0.1*right_val
                    dir_right_val = 0.8*right_val + 0.1*up_val + 0.1*down_val
                    dir_values = np.append(dir_values, dir_up_val)
                    dir_values = np.append(dir_values, dir_left_val)
                    dir_values = np.append(dir_values, dir_down_val)
                    dir_values = np.append(dir_values, dir_right_val)

                    final_util = rewards[row_index, col_index] + DISCOUNT_FACTOR*np.max(dir_values)
                    temp[row_index, col_index] = final_util

                    max_util_change[dim * row_index + col_index] = abs(temp[row_index, col_index] - maze[row_index, col_index])
                    
        for row_index in prange(dim):
            for col_index in prange(dim):
                if rewards[row_index, col_index] != -1*DEFAULT_REWARD:
                    temp[row_index, col_index] = rewards[row_index, col_index]

        count+= 1
        maze = temp.copy()
        if len(max_util_change) and np.max(max_util_change) < max_error:
            break

    return (maze, count)


if __name__ == '__main__':
    app = QApplication([])
    main = App()
    main.show()
    sys.exit(app.exec_())