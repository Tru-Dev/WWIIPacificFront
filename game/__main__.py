# WWII Pacific Front - main.py
# (C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
'''
This module is the entry point for the game client.
'''

#this program should run a single-player battleship game against the computer
#needs to be tested with other modules to debug

import random
from .gamemodels import Ship

# TODO: import other people's modules and work and everything  (specifically Board and Tiles)


#this function allows the user to place their ships at a point of their choice
def place_ship(board: Board, ship: Ship):

    #the user should be able to place their ship horizont ally or vertically
    print("Press 1 to place your boat vertically or 2 to place your boat horizontally.")
    orientation = int(input)

    #'error' switch determines whether the function should continue running
    error = False

    #places the boat vertically
    if orientation == 1:
        print(f"The {ship.name} ship is {ship.size} tiles long.")
        col = int(input("Select the column of the ship(0-15): "))

        #function continues if column is in bounds
        if col <= 15 and col >= 0:
            row = int(input("Place the top-most point of the ship: "))

            #if column input is valid, adds ship coordinates
            if row <= (15 - ship.size) and row > 0:

                for i in range(ship.size):
                    ship.coordinates.append(Tile(row+i, col))

                    #ships can not be placed on tiles already occupied by ships
                    for tile in ship.coordinates:
                        if tile.is_ship == True:
                            error = True
                            print("A ship cannot be placed on top of another ship. Try again.")
                            ship.coordinates = []
                            place_ship(board, ship)
                
                #assigns the name of the ship to the tile
                if error == False:
                    for tile in ship.coordinates:
                        tile.name = ship.name

                #the code shouldn't fall here
                else:
                    print("The person coding this messed up with the coordinates part. Go bother her so she can change it.")

            #error message if row input is invalid
            elif row > (15-ship.size):
                print("This ship will not fit at this point. Try again.")
                place_ship(board, ship)

            #error message if row input is invalid
            elif row < 0:
                print("Invalid row input. Try again.")
                place_ship(board, ship)

            #the code shouldn't go here, but I wrote it just in case
            else:
                print('''If you're seeing this, it's because the code is wrong. 
                Please go bother the person who wrote the code.''')

        #error message if column is out of bounds; restarts function
        else:
            print("Invalid column input. Try again.")
            place_ship(board, ship)

    #places the boat horizontally
    elif orientation == 2:
        print(f"The {ship.name} ship is {ship.size} tiles long.")
        row = int(input("Select the row of the ship(0-15): "))

        #function continues if row input is valid
        if row <= 15 and row >= 0:
            col = int(input("Place the left-most point of the ship."))

            #if column input is valid, adds ship coordinates to list
            if col <= (15 - ship.size) and col > 0:
                for i in range(ship.size):
                    ship.coordinates.append(Tile(row, col+i))
                    #ships can not be placed on tiles already occupied by ships
                    for tile in ship.coordinates:
                        if tile.is_ship == True:
                            print("A ship cannot be placed on top of another ship. Try again.")
                            ship.coordinates = []
                            place_ship(board, ship)

            #error message if column input is invalid
            elif col > (15-ship.size):
                print("This ship will not fit at this point. Try again.")
                place_ship(board, ship)

            #error message if column input is invalid
            elif col < 0:
                print("Invalid input. Try again.")
                place_ship(board, ship)

            #if I really screwed this up, this message will appear. hopefully that won't happen
            else:
                print('''If you're seeing this, it's because the code is wrong. 
                Please go bother the person who wrote the code.''')

        else:
            print("Invalid row input. Try again.")
            place_ship(board, ship)

    else: 
        print("Invalid input entered. Try again.")
        place_ship(board, ship)       


#this function should have the computer randomly place a ship on its board
def place_cpu_ship(board: Board, ship: Ship):
    #the program randomly selects the orientation of its ship
    orientation = random.randint(1,3)

    #'error' switch determines whether the function should continue running 
    error = False

    #places the boat vertically
    if orientation == 1:
        col = random.randint(15)
        row = random.randint(15 - ship.size)

        for i in range(ship.size):
            ship.coordinates.append(Tile(row+i, col))
            #ships can not be placed on tiles already occupied by ships
            for tile in ship.coordinates:             
                if tile.is_ship == True:
                    error = True
                    ship.coordinates = []
                    place_ship(board, ship)

                #assigns the name of the ship to the tile
                if error == False:
                    for tile in ship.coordinates:
                        tile.name = ship.name

                #the code shouldn't fall here
                else:
                    print("The person coding this messed up with the coordinates part. Go bother her so she can change it.")

    #places the boat horizontally
    elif orientation == 2:
        row = random.randint(15)
        col = random.randint(15-ship.size)

        for i in range(ship.size):
            ship.coordinates.append(Tile(row, col+i))
            #ships can not be placed on tiles already occupied by ships
            for tile in ship.coordinates:             
                if tile.is_ship == True:
                    ship.coordinates = []
                    place_ship(board, ship)


#this function allows the user to do everything required to take their turn
def take_turn(board: Board):

    #'error' switch determines whether function should continue running
    error = False

    #the program should have the user select a tile to attack
    row = int(input("Select a row to attack(0-15): "))
    #the user should retry if the coordinates are out of bounds
    if row > 15 or row < 0:
        print("Invalid row input. Try again.")
        take_turn(board)

    else:
        #the program should determine whether the tile has already been attacked
        if tile.attacked == False:
            tile.attacked = True
            #once an attack has been placed, it should be determined whether a ship has been hit
            if tile.is_ship == True:
                print("Hit")
                #if a ship has been hit, it should determine whether it has sank and notify the user
                hit_ship = tile.name
                for tile in hit_ship.coordinates:
                    if tile.attacked == False:
                        error = True
                        print(f"You hit your opponents' {hit_ship.name} ship. It did not sink.")
                        return

                if error == False:
                    print(f"You hit your opponents' {hit_ship.name} ship. The opponents' {hit_ship.name} has sunk.")
                    return

                #the code should not fall here
                else:
                    print("The person coding this messed up with...something. Go bother her so she can change it.")

            else:
                print("Miss")
        #the user should retry if the tile has already been attacked
        else:
            print("This tile has already been hit. Try again")
            take_turn

#this function should have the program attack a spot on the user's board
def cpu_turn(board):
    #program chooses a random spot on the grid to attack
    row = random.randint(16)
    col = random.randint(16)

    if Tile([row][col]).attacked == False:
        print(f"The computer has attacked at row {row}, column {col}.")
        tile.attacked = True

        #determines whether or not a ship has been hit
        if tile.is_ship == True:
            print("One of your ships has been hit")
        else:
            print("None of your ships have been hit")

    #if the tile has been hit already, the program will choose new numbers       
    else:
        cpu_turn(board)


#this function determines whether either player has won or lost
def win_or_lose(board, ships):

    #'error' switch determines whether function should continue running
    error = False

    #this should check if all of one player's ships has sank
    for ship in ships:
        #return False if any ship coordinates have not been hit
        for tile in ship.coordinates:
            if tile.attacked == False:
                error = True
                return False

    #function returns True if all coordinates on all ships have been hit            
    if error == False:
        return True


#defining the attributes of the ships; ship names might change
destroyer = Ship("Destroyer", 2)
submarine = Ship("Submarine", 3)
cruiser = Ship("Cruiser", 3)
battleship = Ship("Battleship", 4)
carrier = Ship("Carrier", 5)

#a tuple containing the ships for the user and the computer
my_ships = (destroyer, submarine, cruiser, battleship, carrier)
cpu_ships = my_ships[:]

#creates two boards: one for the user and one for the opponent
user_board = Board()
cpu_board = Board()

#this loop should allow the user to place all their ships
for ship in my_ships:
    place_ship(user_board, ship) 

#this loop should have the computer place its ships
for ship in cpu_ships:
    place_cpu_ship(cpu_board, cpu_ships)

#this code should make the game run.
while 1:
    take_turn(cpu_board)
    if win_or_lose(cpu_board, ) == True:
        print("All the opponents ships have been sunk. You win")
        break

    cpu_turn(user_board)
    if win_or_lose(user_board, ) == True:
        print("All of your ships have been sunk. You lost")
        break

print("Game over.")
# TODO: something else should probably happen after the game ends. not sure what.
