import random
from PIL import Image, ImageDraw

class Cell:
    NORTH = "North"
    SOUTH = "South"
    EAST = "East"
    WEST = "West"

    def __init__(self, row:list, col:list) -> None: 
        self.row = row
        self.col = col
        self.neighbor_cells = {} 
        self.links = set()
        self.content = " "  # Placeholder for any content you want to store in the cell
        self.distance = 0  # Initialize distance as infinite for pathfinding algorithms

    def link(self, cell, bidirectional=True) -> None:
        # Creates a passage between this cell and the provided cell. 
        # If bidirectional == True, create the same link (edge) between 
        # the other cell and this one. 
        self.links.add(cell)
        if bidirectional:
            cell.link(self, False)

    def unlink(self, cell, bidirectional=True) -> None:
        # Removes a passage (edge) between this cell and the provided one. 
        # If bidirectional == True, remove the edge from the other 
        # cell to this one.
        self.links.discard(cell)
        if bidirectional:
            cell.unlink(self, False)

    def is_linked(self, cell) -> bool:
        # Returns True if this cell is linked to the provided cell 
        # (there's an edge from this cell to the other one)
        return cell in self.links
    
    def get_neighbor(self, direction:str) -> None:
        # get neighbor - self explanatory
        if direction not in [Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST]:
            raise NotImplementedError

        # Return the neighbor if it exists, or None if it doesn't
        return self.neighbor_cells.get(direction)
    
    def set_neighbor(self, direction:str, cell) -> None:
        # set direction to neighbor
        if direction in [Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST]:
            self.neighbor_cells[direction] = cell
        else:
            raise NotImplementedError

    def neighbors(self) -> list:
        # Returns a list of its neighbors: basically, the north, south, 
        # east, and west cells put into a list
        return [neighbor for neighbor in self.neighbor_cells.values() if neighbor is not None]

    def get_closest_cell(self) -> list:
        # Finds the linked neighbor that has the shortest distance assigned 
        # to it. If there are no linked neighbors, return None. 
        # A Linked Neighbor is a neighboring Cell (e.g North/South/East/West) 
        # that has an edge/link/passage.
        all_neighbors = self.neighbors()
        # Adding direct attribute checks
        for direction in [Cell.NORTH, Cell.SOUTH, Cell.EAST, Cell.WEST]:
            neighbor = getattr(self, direction.lower(), None)
            if neighbor and self.is_linked(neighbor):
                all_neighbors.append(neighbor)

        if not all_neighbors:
            return None

        return min(all_neighbors, key=lambda n: n.distance)

    def print(self) -> str:
        return f"Cell({self.row}, {self.col})"

# This is the grid for the maze, full of cells.
class Grid:
    def __init__(self, num_rows:int, num_cols:int) -> None:
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.rows = []
        self.prepare_grid()
        self.configure_cells()

    def __iter__(self) -> None:
        for row in self.rows:
            for cell in row:
                yield cell

    def prepare_grid(self) -> None:
        # Create all the rows, populating them by creating cells
        self.rows = [[Cell(row, col) for col in range(self.num_cols)] for row in range(self.num_rows)]

    def configure_cells(self) -> None:
        # Iterate through all the cells, telling each cell what it's neighbors 
        # are (e.g. what Cell.north, etc are).
        #
        # Hint: The north neighbor of cell is the one at row cell.row - 1 and column cell.col
        for cell in self.all_cells():
            row, col = cell.row, cell.col
            cell.set_neighbor(Cell.NORTH, self.get_cell(row - 1, col))
            cell.set_neighbor(Cell.SOUTH, self.get_cell(row + 1, col))
            cell.set_neighbor(Cell.EAST, self.get_cell(row, col + 1))
            cell.set_neighbor(Cell.WEST, self.get_cell(row, col - 1))

    def get_cell(self, row, col) -> Cell:
        # Return the cell at the specified row and column.
        if 0 <= row < self.num_rows and 0 <= col < self.num_cols:
            return self.rows[row][col]
        return None

    def all_cells(self) -> list:
        # Return a flattened list of all the cells in the grid.
        return [cell for row in self.rows for cell in row]
    
    def export_image(self, filename:str='maze.png', path:str=None) -> None:
        # Export image to png format
        cell_size = 20  # Size of each cell in the image (pixels)
        img_width = self.num_cols * cell_size
        img_height = self.num_rows * cell_size

        img = Image.new('RGB', (img_width, img_height), 'white')
        draw = ImageDraw.Draw(img)

        # Draw the maze
        for cell in self.all_cells():
            x1 = cell.col * cell_size
            y1 = cell.row * cell_size
            x2 = (cell.col + 1) * cell_size
            y2 = (cell.row + 1) * cell_size

            # Draw the cell walls
            if not cell.is_linked(cell.get_neighbor('North')):
                draw.line([(x1, y1), (x2, y1)], fill='black')
            if not cell.is_linked(cell.get_neighbor('South')):
                draw.line([(x1, y2), (x2, y2)], fill='black')
            if not cell.is_linked(cell.get_neighbor('East')):
                draw.line([(x2, y1), (x2, y2)], fill='black')
            if not cell.is_linked(cell.get_neighbor('West')):
                draw.line([(x1, y1), (x1, y2)], fill='black')

        # Draw the solution path if provided
        if path:
            for i in range(len(path) - 1):
                cell1 = path[i]
                cell2 = path[i + 1]
                mid1 = ((cell1.col + 0.5) * cell_size, (cell1.row + 0.5) * cell_size)
                mid2 = ((cell2.col + 0.5) * cell_size, (cell2.row + 0.5) * cell_size)
                draw.line([mid1, mid2], fill='red', width=3)

        img.save(filename)

    def draw_export_image(self, image_path:str, path:str=None, filename:str='solved_maze.png') -> None:
        # Draw path through generated maze
        cell_size = 20
        image = Image.open(image_path)
        draw = ImageDraw.Draw(image)

        offset = cell_size // 2

        for i in range(len(path) - 1):
            cell1 = path[i]
            cell2 = path[i + 1]
            x1, y1 = cell1.col * cell_size + offset, cell1.row * cell_size + offset
            x2, y2 = cell2.col * cell_size + offset, cell2.row * cell_size + offset
            draw.line([(x1, y1), (x2, y2)], fill='red', width=2)

        image.save(filename)
        # image.show()
    
    def print(self) -> None:
        # Prints out the grid.
        output = "+---" * self.num_cols + "+\n"
        for row in self.rows:
            top = "|"
            bottom = "+"
            for cell in row:
                body = "   "  # three spaces for the cell body
                east_boundary = " " if cell.is_linked(cell.get_neighbor(Cell.EAST)) else "|"
                south_boundary = "   " if cell.is_linked(cell.get_neighbor(Cell.SOUTH)) else "---"
                top += body + east_boundary
                bottom += south_boundary + "+"
            output += top + "\n" + bottom + "\n"
        print(output)
        return output
    
    def solve_maze(self, start_cell, end_cell):
        stack = [(start_cell, [start_cell])]
        visited = set()

        while stack:
            current_cell, path = stack.pop()
            if current_cell == end_cell:
                return path

            visited.add(current_cell)

            for neighbor in current_cell.links:
                if neighbor not in visited:
                    new_path = list(path)
                    new_path.append(neighbor)
                    stack.append((neighbor, new_path))
        return None
    
# This is a simple maze maker algorithm that uses a "binary tree" approach 
# to making a simple maze: It starts in the upper-left corner of the grid, 
# and then "breaks" walls to either the east or the south, via a random choice.
# This maze making algorithm is simple, but the mazes aren't very interesting. 
# It's provided as a reference to get you started with a basic maze and see 
# how all the things come together.
class BinaryTreeMazeMaker:
    def __init__(self, grid:Grid) -> None:
        self.grid = grid

    def make_maze(self) -> None:
        for cell in self.grid.all_cells():
            neighbors = []
            south_neighbor = cell.get_neighbor(Cell.SOUTH)
            east_neighbor = cell.get_neighbor(Cell.EAST)

            if south_neighbor:
                neighbors.append(south_neighbor)
            if east_neighbor:
                neighbors.append(east_neighbor)

            if neighbors:
                chosen = random.choice(neighbors)
                cell.link(chosen)

# Starting in the northwest corner
# "Flip a coin": Get a random number between 0 and 1
# If "tails" (e.g. the random number is 0)
# Erase the east wall
# Move to the eastern neighbor ("go through the corridor")
# If "heads" (e.g. the random number is 1)
# Choose one of the cells that we've just linked together, 
#  and delete the south wall.
# Move to the next eastern neighbor.
# If you're at a cell that has no eastern neighbor, just delete the south wall.
# Go to the start of the next row, and repeat the process.
# If you're in the last row, instead of choosing between removing 
# the east or south wall, just remove the east wall.
class SidewinderMazeMaker:
    def __init__(self, grid:Grid) -> None:
        self.grid = grid

    def make_maze(self) -> None:
        for row in self.grid.rows:
            run = []
            for cell in row:
                run.append(cell)
                at_eastern_boundary = (cell.get_neighbor(Cell.EAST) is None)
                at_northern_boundary = (cell.get_neighbor(Cell.NORTH) is None)

                # Flip a coin
                should_close_out = at_eastern_boundary or (not at_northern_boundary and random.randint(0, 1) == 0)

                if should_close_out:
                    member = random.choice(run)
                    if member.get_neighbor(Cell.NORTH):
                        member.link(member.get_neighbor(Cell.NORTH))
                    run = []
                else:
                    cell.link(cell.get_neighbor(Cell.EAST))

# Initialize source:
# Set the distance attribute of all nodes (cells) in the graph (grid)
#  to float('inf') or 10000
# Set the distance for the source node (the north-west cell) to be 0
# Put all the nodes in the graph into a queue
# While there are more nodes in the queue:
# Get the node from the queue with the smallest distance assigned
# Add it to the set of nodes that we know the distance to
# For all the linked neighbors of the node, relax the weights
# Recover the path from the grid:
# Start with the target cell (the cell at the south-east corner of the maze)
# Put it in the path
# Until we get to the source:
# Find the linked neighbor that has the smallest distance
# Put it in the path
# Reverse the path list
# Return the path
class DjikstraSolver:
    def __init__(self, grid: Grid) -> None:
        self.grid = grid
        self.queue = []

    def initialize(self) -> None:
        # Sets all cells' distances to infinity except for the start cell.

        # NOTE: Originally had 'inf' but based on piazza messages, I switched
        # it to 10000 based on the discussions (cell.distance)
        for cell in self.grid.all_cells():
            cell.distance = 10000
        self.grid.get_cell(0, 0).distance = 0

    def weight(self, cell1:Cell, cell2:Cell) -> float:
        # Calculate the weight of the edge between cell1 and cell2.
        return 1 if cell2 in cell1.links else 10000

    def relax(self, cell:Cell) -> None:
        # Relaxes the edge weights for the given cell's neighbors.
        for neighbor in cell.links:
            new_distance = cell.distance + self.weight(cell, neighbor)
            if new_distance < neighbor.distance:
                neighbor.distance = new_distance
                neighbor.previous = cell
                self.add_to_queue(neighbor, new_distance)

    def add_to_queue(self, cell:Cell, distance:int) -> None:
        # Sort the queue by distance
        self.queue.append((distance, cell))
        self.queue.sort(key=lambda x: x[0]) 

    def solve(self) -> list:
        # Solves the maze using Dijkstra's algorithm.
        self.initialize()
        self.add_to_queue(self.grid.get_cell(0, 0), 0)

        while self.queue:
            _, curr_cell = self.queue.pop(0)  # Retrieve and remove the cell with the lowest distance
            self.relax(curr_cell)

        target = self.grid.get_cell(self.grid.num_rows - 1, self.grid.num_cols - 1)
        if target.distance == 10000:
            return []  # No path found

        return self.recover_path()

    def recover_path(self) -> list:
        # Recovers the path from the target cell back to the source cell.
        path = []
        current = self.grid.get_cell(self.grid.num_rows - 1, self.grid.num_cols - 1)
        while current:
            path.append(current)
            if current.row == 0 and current.col == 0:
                break
            neighbors = [neighbor for neighbor in current.links if neighbor.distance < current.distance]
            if not neighbors:
                break
            current = min(neighbors, key=lambda n: n.distance)
        path.reverse()
        return path
    
# The general idea is as follows: Consider the grid one row 
# at a time, sequentially. Assign unvisited cells in the current 
# row to different sets. Randomly link adjacent cells that belong to different 
# sets, marging the sets together as you go. For each remaining set, choose 
# at least one cell and carve south, adding the southern cell to the set as 
# well. Repeat for every row in the rid. On the final row, link all adjacent 
# cells that belong to different sets.
class EllerMazeMaker:
    def __init__(self, grid:Grid) -> None:
        self.grid = grid

    def make_maze(self) -> None:
        set_counter = 0
        sets = {}

        # NOTE: While im not a fan of nested loops and statements, like this,
        # it was sadly the best way I could incorporate. Specific feedback here
        # on how I could make this look better is greatly appreciated if you 
        # you have the time :)
        for y, row in enumerate(self.grid.rows):
            for cell in row:
                if cell not in sets:
                    set_counter += 1
                    sets[cell] = set_counter

            for i in range(len(row) - 1):
                cell = row[i]
                next_cell = row[i + 1]
                if sets[cell] != sets[next_cell] and random.choice([True, False]):
                    cell.link(next_cell)
                    self.merge_sets(sets, cell, next_cell)

            set_groups = self.group_sets_by_id(sets, row)
            for group in set_groups.values():
                if y < self.grid.num_rows - 1:  # Skip for last row
                    cell_to_link = random.choice(list(group))
                    south_cell = self.grid.get_cell(cell_to_link.row + 1, cell_to_link.col)
                    cell_to_link.link(south_cell)
                    sets[south_cell] = sets[cell_to_link]

            if y == self.grid.num_rows - 1:
                for i in range(len(row) - 1):
                    cell = row[i]
                    next_cell = row[i + 1]
                    if sets[cell] != sets[next_cell]:
                        cell.link(next_cell)

    def merge_sets(self, sets, cell:Cell, other_cell:Cell) -> None:
        # Merge sets when a horizontal connection is made.
        target_set_id = sets[other_cell]
        source_set_id = sets[cell]
        for c in sets:
            if sets[c] == source_set_id:
                sets[c] = target_set_id

    def group_sets_by_id(self, sets:dict, row:dict) -> list:
        # Group cells by their set IDs.
        groups = {}
        for cell in row:
            cell_set_id = sets[cell]
            if cell_set_id not in groups:
                groups[cell_set_id] = []
            groups[cell_set_id].append(cell)
        return groups