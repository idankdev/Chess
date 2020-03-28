#!/usr/bin/python3
# -*- coding: utf-8 -*-

import chess
import numpy as np
import tensorflow as tf
from flask import Flask, request, jsonify

app = Flask(__name__)

# [0,  1,  2,  3,  4,  5,  6,  7,  8,  9,  10,  11]
# [bp, bn, bb, br, bq, bk, wp, wn, wb, wr, wq, wk ]

def board_tokenizer(board):
  matrix = np.zeros((8, 8, 12), dtype=np.int8)
  row = 0
  column = 0
  for i in chess.SQUARES:
    piece = board.piece_at(i)
    if piece != None:
      matrix[row, column, piece.piece_type + 6 * piece.color - 1] = 1
    if column == 7:
      row += 1
      column = 0
    else:
      column += 1
  return matrix


def material_score(board, move):
  board.push(move)
  if board.is_checkmate():
    board.pop()
    return 10
  board.pop()
  if board.is_capture(move):
    piece_type = board.piece_type_at(getattr(chess, move.uci()[2:4].upper()))
    if piece_type is not None:
      return grades[piece_type - 1]
    if board.turn == chess.WHITE:
      return grades[board.piece_type_at(getattr(chess, move.uci()[2:4].upper()) - 8) - 1]
    if board.turn == chess.BLACK:
      return grades[board.piece_type_at(getattr(chess, move.uci()[2:4].upper()) + 8) - 1]   
  return 0

def material_score_after_move(board, move):
  board.push(move)
  high_score = 0
  for move in board.legal_moves:
    move_score = material_score(board, move)
    if  move_score > high_score:
      high_score = move_score
  board.pop()
  return high_score

def get_classical_children(board):
  children = []
  for move in board.legal_moves:
    children.append([move.uci(), material_score(board, move)])
  children.sort(key = lambda a: a[1], reverse = True)
  return children[:8]

def classical_minimax(board, depth = 2, player = 1, alpha = -float("inf"), beta = float("inf")):
  children = get_classical_children(board)
  if len(children) == 0:
    return [0]
  elif depth == 0:
    return [children[0][1]]
  predicted_child = children[0][0]
  bestVal = -1 * player * float("inf")
  for move, score in children:
    board.push_uci(move)
    result = classical_minimax(board, depth-1, -1*player, alpha, beta)
    opposition_value = result[0]
    advantage_score = player * score + opposition_value
    if player == 1:
        if advantage_score > bestVal:
            bestVal = advantage_score
            favourite_child = move
            alpha = max(alpha, bestVal)
            if beta <= alpha:
                board.pop()
                break
    elif player == -1:
        if advantage_score < bestVal:
            bestVal = advantage_score
            favourite_child = move
            beta = min(beta, bestVal)
            if beta <= alpha:
                board.pop()
                break
    board.pop()
  return [bestVal, favourite_child, predicted_child]

def generate_move_with_classical_minimax(board, minimax_depth = 4):
  if board.turn == chess.WHITE:
    class_minimax = classical_minimax(board, depth = minimax_depth, player = 1)
  else:
    class_minimax = classical_minimax(board, depth = minimax_depth, player = -1)
  minimax_score = class_minimax[0]
  minimax_move = class_minimax[1]
  model1 = tf.keras.models.load_model('/root/server/model1.h5')
  model2 = tf.keras.models.load_model('/root/server/model2.h5')
  from_square = model1.predict(board_tokenizer(board).reshape(1, 8, 8, 12))[0]
  to_square = model2.predict(board_tokenizer(board).reshape(1, 8, 8, 12))[0]
  children = []
  for move in board.legal_moves:
    children.append([move.uci(), from_square[getattr(chess, move.uci()[:2].upper())] + to_square[getattr(chess, move.uci()[2:4].upper())] +  + material_score(board, move) - material_score_after_move(board, move)])
  children.sort(key = lambda a: a[1], reverse = True)
  print ("nn move is " + children[0][0] + " and the score is ", children[0][1])
  print ("minimax move is " + minimax_move + " and the score is ", minimax_score) 
  if minimax_score - children[0][1] > 1.5:
    return minimax_move
  else:
    return children[0][0]      

@app.route('/', methods=['GET', 'POST'])
def get():
  fen = request.args.get("fen")
  response = jsonify({'move': generate_move_with_classical_minimax(chess.Board(fen), minimax_depth = 6)})
  response.headers.add('Access-Control-Allow-Origin', '*')
  return response 


if __name__ == '__main__':
  grades = [0.2, 0.75, 0.8, 1, 5, 0]  
  app.run(debug=False)
