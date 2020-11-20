"""Application for Parallel Mouse Simulation."""
import sys
import numpy as np
from dataclasses import dataclass
from enum import Enum
from PyQt5.QtGui import QPixmap
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
    REWARD = 1
    FIRE = -1
    ROCK = -0.1
    EMPTY = -0.04


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
        self.mouse_grid = self.create_mouse_grid()
        self.button_panel = self.create_button_panel()
        self.h_box = QHBoxLayout()
        self.h_box.addWidget(self.mouse_grid)
        self.h_box.addLayout(self.button_panel)
        self.display_time = QLabel("0 ms")

        self.setLayout(self.h_box)
        self.show()

    def create_button_panel(self):
        """Creates button panel for user to edit grid."""
        grid_editor_ui = self.create_grid_editor_ui()
        parallel_toggle_ui = self.create_parallel_toggle_ui()

        play_button = QPushButton("Play Mouse")
        play_button.setToolTip("This will start the mouse pathing")
        play_button.clicked.connect(self.on_click_play)

        v_box = QVBoxLayout()
        v_box.addLayout(grid_editor_ui)
        v_box.addLayout(parallel_toggle_ui)
        v_box.addWidget(play_button)
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
        erase_button.setToolTip("This will allow you to remove a rock or fire object from the map")
        erase_button.clicked.connect(self.on_click_erase)

        v_box = QVBoxLayout()
        v_box.addWidget(grid_editor_label)
        v_box.addWidget(add_fire_button)
        v_box.addWidget(add_rock_button)
        v_box.addWidget(move_reward_button)
        v_box.addWidget(move_mouse_button)
        v_box.addWidget(erase_button)
        return v_box

    def create_parallel_toggle_ui(self):
        """Creates parallel display UI layout."""
        parallel_check_box = QCheckBox("Parallel")
        parallel_check_box.setToolTip("If checked, the algorithm will run in parallel")
        # parallel_check_box.stateChanged.connect(self.is_parallel_checked)

        h_box = QHBoxLayout()
        h_box.addWidget(parallel_check_box)
        # h_box.addWidget(self.display_time)
        return h_box

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

    def on_click_play(self):
        print(self.generate_numpy_matrix())

    def on_click_grid_cell(self):
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


def seq_cell_update(rewards):
    """Sequential updating of maze cell values sequentially"""
    maze = np.zeros((20,20))
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
        maze = temp.copy()
        if max_util_change < max_error:
            break
        max_util_change = 0
    return maze

if __name__ == '__main__':
    app = QApplication([])
    main = App()
    main.show()
    sys.exit(app.exec_())