#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import tkinter as tk
import json


class Position(object):

    length = 75

    @property
    def position(self):
        return "ABCDEFGH"[self.col] + str(8 - self.row)

    @property
    def x1(self):
        return self.length * self.col

    @property
    def y1(self):
        return self.length * self.row

    @property
    def x2(self):
        return self.length + self.x1

    @property
    def y2(self):
        return self.length + self.y1

    def in_range(self, x, y):
        cx = x in range(self.x1, self.x2)
        cy = y in range(self.y1, self.y2)
        return cx and cy

    def __repr__(self):
        return self.position

    def __init__(self, row, col):
        (self.row, self.col) = (row, col)


class Square(Position):

    dark = "#d18b47"
    light = "#ffce9e"

    @property
    def coords(self):
        return (self.x1, self.y1, self.x2, self.y2)

    @property
    def colors(self):
        return (self.light, self.dark)

    @property
    def color_id(self):
        return (self.row + self.col) % 2

    @property
    def design(self):
        return dict(fill=self.color)

    def draw(self, canvas):
        canvas.create_rectangle(*self.coords, **self.design)

    def __init__(self, row, col):
        super().__init__(row, col)
        self.color = self.colors[self.color_id]


class Squares(object):

    def find_square(self, x, y):
        for s in self:
            if s.in_range(x, y):
                return s

    def draw(self):
        for s in self:
            s.draw(self.canvas)

    def __iter__(self):
        for s in self.squares:
            yield s

    def __len__(self):
        return len(self.squares)

    def __init__(self, canvas):
        self.canvas = canvas
        self.squares = []
        for row in range(8):
            for col in range(8):
                s = Square(row, col)
                self.squares.append(s)


class Piece(Position):

    @property
    def coords(self):
        x = self.x1 + (self.length / 2)
        y = self.y1 + (self.length / 2)
        return (x, y)

    @property
    def design(self):
        return dict(text=self.text, fill=self.color, font=("", 56))

    def dump(self):
        return {
            "team": self.color,
            "name": self._name
        }

    def draw(self, canvas):
        canvas.create_text(*self.coords, **self.design)

    def __str__(self):
        return json.dumps(self.dump(), indent=2)

    def __init__(self, name, color, text, *args):
        super().__init__(*args)
        self._name = name
        self.color = color
        self.text = text


class King(Piece):

    def __init__(self, color, row):
        super().__init__("king", color, chr(0x265A), row, 3)


class Queen(Piece):

    def __init__(self, color, row):
        super().__init__("queen", color, chr(0x265B), row, 4)


class Rook(Piece):

    def __init__(self, color, *args):
        super().__init__("rook", color, chr(0x265C), *args)


class Bishop(Piece):

    def __init__(self, color, *args):
        super().__init__("bishop", color, chr(0x265D), *args)


class Knight(Piece):

    def __init__(self, color, *args):
        super().__init__("knight", color, chr(0x265E), *args)


class Pawn(Piece):

    def __init__(self, color, *args):
        super().__init__("pawn", color, chr(0x265F), *args)


class Black(object):

    def __init__(self):
        king = King("black", 0)
        queen = Queen("black", 0)
        rooks = [Rook("black", 0, _) for _ in (0, 7)]
        bishops = [Bishop("black", 0, _) for _ in (2, 5)]
        knights = [Knight("black", 0, _) for _ in (1, 6)]
        pawns = [Pawn("black", 1, _) for _ in range(8)]
        self.pieces = [king, queen] + rooks + bishops + knights + pawns


class White(object):

    def __init__(self):
        king = King("white", 7)
        queen = Queen("white", 7)
        rooks = [Rook("white", 7, _) for _ in (0, 7)]
        bishops = [Bishop("white", 7, _) for _ in (2, 5)]
        knights = [Knight("white", 7, _) for _ in (1, 6)]
        pawns = [Pawn("white", 6, _) for _ in range(8)]
        self.pieces = [king, queen] + rooks + bishops + knights + pawns


class Pieces(object):

    def find_piece(self, x, y):
        for p in self.pieces:
            if p.in_range(x, y):
                return p

    def draw(self):
        for p in self.pieces:
            p.draw(self.canvas)

    def __len__(self):
        return len(self.pieces)

    def __iter__(self):
        for p in self.pieces:
            yield p

    def __init__(self, canvas):
        self.canvas = canvas
        self.pieces = Black().pieces + White().pieces


class Board(object):

    move_count = 0
    selected = None

    @classmethod
    def inc_move_count(cls):
        cls.move_count += 1

    @property
    def turn(self):
        teams = ("white", "black")
        move_id = (self.move_count % 2)
        return teams[move_id]

    def get_click_data(self, *pos):
        square = self.squares.find_square(*pos)
        piece = self.pieces.find_piece(*pos)
        return (square, piece)

    def display_info(self, square):
        info = {
            "move": self.move_count,
            "turn": self.turn,
            "square": str(square)
        }
        if self.selected:
            info["piece"] = self.selected.dump()
        print(json.dumps(info, indent=2))

    def highlight(self, square):
        color = square.color
        square.color = "purple"
        self.draw()
        square.color = color

    def left_click(self, event):
        self.selected = None
        pos = (event.x, event.y)
        (square, piece) = self.get_click_data(*pos)
        self.display_info(square)
        # self.highlight(square)
        if piece:
            self.selected = piece
            if self.selected.color != self.turn:
                print(f"[-] It is {self.turn}'s turn!")
            else:
                print("[+] Make a move with this piece.")

    def draw(self):
        self.squares.draw()
        self.pieces.draw()

    def __init__(self, master):
        self.canvas = tk.Canvas(master, width=600, height=600)
        master.bind("<Button-1>", self.left_click)
        self.squares = Squares(self.canvas)
        self.pieces = Pieces(self.canvas)
        self.canvas.pack()
        self.draw()


def main():
    window = tk.Tk()
    window.title("Chess")
    window.resizable(width=False, height=False)
    board = Board(window)
    window.mainloop()


if __name__ == "__main__":
    main()
