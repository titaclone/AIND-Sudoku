assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def assign_value(values, box, value):
	"""
	Please use this function to update your values dictionary!
	Assigns a value to a given box. If it updates the board record it.
	"""

	# Don't waste memory appending actions that don't actually change any values
	if values[box] == value:
		return values

	values[box] = value
	if len(value) == 1:
		assignments.append(values.copy())
	return values

def diag(a,b):
	"""Get the two diagonal units of the grid
	Args:
		values(dict): rows and columns

	Returns:
		the key values of the two diagonal units of the grid.
	"""
	diag_unit1=[ ]
	diag_unit2=[ ]
	diag_units=[ ]
	for r in range(9):
		diag_unit1.append(a[r]+b[r])
		diag_unit2.append(a[r]+b[8-r])
	diag_units.append(diag_unit1)
	diag_units.append(diag_unit2)
	return diag_units

def naked_twins(values):
	"""Eliminate values using the naked twins strategy.
	Args:
		values(dict): a dictionary of the form {'box_name': '123456789', ...}

	Returns:
		the values dictionary with the naked twins eliminated from peers.
	"""

	# Find all instances of naked twins
	# Eliminate the naked twins as possibilities for their peers
	for unit_list in unitlist:   
		# Find all instances of naked twins for each unit in the grid
		twins_list = []
		for bk1 in unit_list:
			for bk2 in unit_list:
				if(bk1 != bk2 and values[bk1]==values[bk2] and len(values[bk1])==2):
					twins = []
					if bk1 not in twins:
						twins.append(bk1)
					if bk2 not in twins:    
						twins.append(bk2)
					if sorted(twins) not in twins_list:
						twins_list.append(sorted(twins))
		# Eliminate the naked twins as possibilities in that unit
		if len(twins_list):
			for tl in twins_list:
				if len(tl):
					for k in unit_list:
						if k not in tl:
							for d in values[k]:
								if d in values[tl[0]]:
									values[k]=values[k].replace(d, '')

	return values

def cross(a, b):
	return [s+t for s in a for t in b]

diagonal_units = diag(rows, cols)

boxes = cross(rows, cols)
diagonal_units = diag(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units 

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def grid_values(grid):
	"""Convert grid string into {<box>: <value>} dict with '.' value for empties.

	Args:
		grid: Sudoku grid in string form, 81 characters long
	Returns:
		Sudoku grid in dictionary form:
		- keys: Box labels, e.g. 'A1'
		- values: Value in corresponding box, e.g. '8', or '.' if it is empty.
	"""
	values = []
	all_digits = '123456789'
	for c in grid:
		if c == '.':
			values.append(all_digits)
		elif c in all_digits:
			values.append(c)
	assert len(values) == 81
	return dict(zip(boxes, values))

def display(values):
	"""
	Display the values as a 2-D grid.
	Input: The sudoku in dictionary form
	Output: None
	"""
	width = 1+max(len(values[s]) for s in boxes)
	line = '+'.join(['-'*(width*3)]*3)
	for r in rows:
		print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
					  for c in cols))
		if r in 'CF': print(line)
	return

def eliminate(values):
	"""Eliminate values from peers of each box with a single value.

	Go through all the boxes, and whenever there is a box with a single value,
	eliminate this value from the set of values of all its peers.

	Args:
		values: Sudoku in dictionary form.
	Returns:
		Resulting Sudoku in dictionary form after eliminating values.
	"""
	solved_values = [box for box in values.keys() if len(values[box]) == 1]
	for box in solved_values:
		digit = values[box]
		#remove that solved box in peers of that box
		for peer in peers[box]:
			values[peer] = values[peer].replace(digit,'')
		#if that box is part of a diagonal remove it from other boxes of that diagonals
		for r in range(2):
			if box in diagonal_units[r]:
				for db in diagonal_units[r]:
					if db != box:
						values[db] = values[db].replace(digit,'')
	return values

def only_choice(values):
	"""Finalize all values that are the only choice for a unit.

	Go through all the units, and whenever there is a unit with a value
	that only fits in one box, assign the value to this box.

	Input: Sudoku in dictionary form.
	Output: Resulting Sudoku in dictionary form after filling in only choices.
	"""
	for unit in unitlist:
		for digit in '123456789':
			dplaces = [box for box in unit if digit in values[box]]
			if len(dplaces) == 1:
				values[dplaces[0]] = digit
	return values

def reduce_puzzle(values):
	"""
	Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
	If the sudoku is solved, return the sudoku.
	If after an iteration of both functions, the sudoku remains the same, return the sudoku.
	Input: A sudoku in dictionary form.
	Output: The resulting sudoku in dictionary form.
	"""
	stalled = False
	while not stalled:
		# Check how many boxes have a determined value
		solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
		# Use the Eliminate Strategy
		values = eliminate(values)
		# Use the Only Choice Strategy
		values = only_choice(values)
		# Check how many boxes have a determined value, to compare
		solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
		# If no new values were added, stop the loop.
		stalled = solved_values_before == solved_values_after
		# Sanity check, return False if there is a box with zero available values:
		if len([box for box in values.keys() if len(values[box]) == 0]):
			return False
	return values

def search(values):
	"Using depth-first search and propagation, try all possible values."
	# First, reduce the puzzle using the previous function
	values = reduce_puzzle(values)
	if values is False:
		return False ## Failed earlier
	if all(len(values[s]) == 1 for s in boxes): 
		return values ## Solved!
	# Choose one of the unfilled squares with the fewest possibilities
	n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
	# Now use recurrence to solve each one of the resulting sudokus, and 
	for value in values[s]:
		new_sudoku = values.copy()
		new_sudoku[s] = value
		attempt = search(new_sudoku)
		if attempt:
			return attempt

def solve(grid):
	"""
	Find the solution to a Sudoku grid.
	Args:
		grid(string): a string representing a sudoku grid.
			Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
	Returns:
		The dictionary representation of the final sudoku grid. False if no solution exists.
	"""
	#transform the grid str to dictionary form
	values = grid_values(grid)
	#apply search and contraints propagation to sole the sudoku
	values = search(values)
	return values


if __name__ == '__main__':
	diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
	display(solve(diag_sudoku_grid))

	try:
		from visualize import visualize_assignments
		visualize_assignments(assignments)

	except SystemExit:
		pass
	except:
		print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
