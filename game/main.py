'''
WWII Pacific Front - main.py
(C) 2021 Jesus Trujillo, Delaney Siggia, Calvin Guela, Anthony Jaimes, Rocco Carrozza
---
This module is the entry point for the game client.
'''

#this program should run a single-player battleship game against the computer
#I comment 'elephant' where things need to be worked on. ctrl-f that if needed.

import random
from gamemodels import Ship

#elephant (import other people's modules and work and everything)



#this function allows the user to place their ships at a point of their choice
def place_ship(board: Board, ship: Ship):

    #the user should be able to place their ship horizontally or vertically
    print("Press 1 to place your boat vertically or 2 to place your boat horizontally.")
    orientation = int(input)

    #places the boat vertically
    if orientation == 1:
        print(f"The {ship.name} ship is {ship.length} tiles long.")
        col = int(input("Select the column of the ship(0-15): "))

        #function continues if column is in bounds
        if col <= 15 and col >= 0:
            row = int(input("Place the top-most point of the ship: "))

            #if column input is valid, adds ship coordinates
            if row <= (15 - ship.length) and row > 0:
                for i in range(ship.length):
                    ship.coordinates.append(Tile(row+i, col))

            #error message if row input is invalid
            elif row > (15-ship.length):
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
        print(f"The {ship.name} ship is {ship.length} tiles long.")
        row = int(input("Select the row of the ship(0-15): "))

        #function continues if row input is valid
        if row <= 15 and row >= 0:
            col = int(input("Place the left-most point of the ship."))

            #if column input is valid, adds ship coordinates to list
            if col <= (15 - ship.length) and col > 0:
                for i in range(ship.length):
                    ship.coordinates.append(Tile(row, col+i))

            #error message if column input is invalid
            elif col > (15-ship.length):
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

    #ships cannot be placed on tiles already occupied by ships
    for tile in ship.coordinates:
        if tile.is_ship == True:
            print("A ship cannot be placed on top of another ship. Try again.")
            ship.coordinates = []
            


#this function allows the user to do everything required to take their turn
def take_turn(Board(board)):
    #the program should have the user select a tile to attack
    row = int(input("Select a row to attack(0-15): "))
    #the user should retry if the coordinates are out of bounds
    if row > 15 or row < 0:
        print("Invalid row input. Try again.")
        take_turn(board)

    else:
        #the user should retry if the tile has already been attacked
        if tile.attacked == False:
            tile.attacked = True
            #once an attack has been placed, it should be determined whether a ship has been hit
            if tile.is_ship = True:
                print("Hit")
                #if a ship has been hit, it should determine whether it has sank and notify the user
                #elephant (that ^)
            else:
                print("Miss")

    else:
        print("This tile has already been hit. Try again")
        take_turn

#this function should have the program attack a spot on the user's board
def comp_turn(board):
    #elephant (lots needed here. make the computer take a turn.)

#this function determines whether either player has won or lost
def win_or_lose(board):
    #elephant (all of this)
    #this should check if all of one player's ships has sank
    #if there is no winner, the function should return False,
    #if there is a winner, the function should return True


#defining the attributes of the ships; ship names might change
destroyer = Ship("Destroyer", 2)
submarine = Ship("Submarine", 3)
cruiser = Ship("Cruiser", 3)
battleship = Ship("Battleship", 4)
carrier = Ship("Carrier", 5)

#a tuple containing the ships
ships = (destroyer, submarine, cruiser, battleship, carrier)

#creates two boards: one for the user and one for the opponent
user_board = Board()
comp_board = Board()

#this loop should allow the user to place all their ships
for ship in ships:
    place_ship(user_board, ship) 

#this code should make the game run.
while 1:
    take_turn(comp_board)
    if win_or_lose(comp_board) == True:
        print("You won")
        break

    comp_turn(user_board)
    if win_or_lose(user_board) == True:
        print("You lost")
        break