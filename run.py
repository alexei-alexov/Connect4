#!bin/usr/env python
# coding: utf-8
import sys
import random

import pygame

from falling_token import FallingToken
from consts import *

pygame.init()


class Game(object):

    def __init__(self):
        self.prepare()
        self.loop()

    def prepare(self):
        self.font = pygame.font.SysFont("monospace", 16)
        icon = pygame.Surface((32, 32))
        icon.fill(C_WIN)
        # icon.blit(self.font.render("4", 1, C_EMPTY), (0, 0))
        pygame.display.set_icon(icon)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Connect4")
        self.create_active_column_surface()
        self.game_start()        
        
    def game_start(self):
        self.table = [[EMPTY] * FIELD_COLUMNS for i in xrange(FIELD_ROWS)]
        self.token_surface = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT))
        self.refresh_token_surface()
        self.gui_surface = pygame.Surface((PANEL_WIDTH, SCREEN_HEIGHT))
        self.falling_token = None
        self.restart = False
        self.create_cover_surface()
        self.turn = FIRST
        self.state = self.state_turn_wait
        self.turns = TURNS
        self.winner_surface = None

    def create_active_column_surface(self):
        self.active_column_surface = pygame.Surface((TOKEN_CONTENT_SIZE, SCREEN_HEIGHT))
        self.active_column_surface.set_colorkey(C_EMPTY)
        self.active_column_surface.fill(C_WIN)
        for row_index in xrange(FIELD_ROWS):
            pygame.draw.circle(
                self.active_column_surface,
                C_EMPTY,
                (
                    TOKEN_CONTENT_SIZE / 2,
                    TOKEN_CONTENT_SIZE * row_index + TOKEN_CONTENT_SIZE / 2
                ),
                TOKEN_R
            )
            

    def create_cover_surface(self):
        self.cover_surface = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT))
        self.cover_surface.set_colorkey(C_EMPTY)
        pygame.draw.rect(self.cover_surface, C_COVER, (0, 0, FIELD_WIDTH, FIELD_HEIGHT))
        shift_left = 0
        shift_top = 0
        for row in self.table:
            for column in row:
                pygame.draw.circle(
                    self.cover_surface,
                    C_EMPTY,
                    (
                        shift_left + TOKEN_CONTENT_SIZE / 2,
                        shift_top + TOKEN_CONTENT_SIZE / 2
                    ),
                    TOKEN_R
                )
                shift_left += DRAW_TOKEN_SHIFT                
            shift_left = 0
            shift_top += DRAW_TOKEN_SHIFT

    def switch_turn(self):
        self.turn = SECOND if self.turn == FIRST else FIRST

    def loop(self):
        self.clock = pygame.time.Clock()
        self.delta = 0
        self.running = True
        self.mouse = (-1, -1)
        self.click = False
        while self.running:
            self.tick()
            self.render()
            self.get_input()
            
            self.delta = self.clock.tick(60)

    def get_input(self):
        self.mouse = pygame.mouse.get_pos()
        self.click = False
        self.restart = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # print "CLICKED"
                # print pygame.mouse.get_pressed()
                self.click = pygame.mouse.get_pressed()[0]
                # print self.click
            elif event.type == pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_r]:
                    self.restart = True

    def tick(self):
        self.state()

    def make_check_winner(self, x, y):
        """Check if new token in given x and y made someone a winner"""
        # check if there is 4 connected
        winning_combinations = []
        #  check horizontal
        horizontal_line = self.check_line(x, y, 1, 0)
        if len(horizontal_line) > 3: 
            winning_combinations.append(horizontal_line)
        #  check vertical
        vertical_line = self.check_line(x, y, 0, 1)
        if len(vertical_line) > 3: 
            winning_combinations.append(vertical_line)
        #  check primary diagonal
        primary_line = self.check_line(x, y, 1, 1)
        if len(primary_line) > 3: 
            winning_combinations.append(primary_line)
        #  check secondary diagonal
        secondary_line = self.check_line(x, y, 1, -1)
        if len(secondary_line) > 3: 
            winning_combinations.append(secondary_line)

        if len(winning_combinations) > 0:
            self.winner = self.turn
            self.state = self.state_end
            self.winner_surface = pygame.Surface((FIELD_WIDTH, FIELD_HEIGHT))
            pygame.draw.rect(self.winner_surface, C_EMPTY, (0, 0, FIELD_WIDTH, FIELD_HEIGHT))
            self.winner_surface.set_colorkey(C_EMPTY)
            for combination in winning_combinations:
                self.render_winner_combination(combination)
            return True
        # check if there is more moves
        if self.turns == 0:
            self.winner = EMPTY
            self.state = self.state_end
            return True
        return False
    
    def render_winner_combination(self, combination):
        for px, py in combination:
            pygame.draw.circle(
                self.winner_surface,
                C_WIN,
                (px * TOKEN_CONTENT_SIZE + TOKEN_CONTENT_SIZE / 2,
                 py * TOKEN_CONTENT_SIZE + TOKEN_CONTENT_SIZE / 2),
                TOKEN_R + 3
            )
            pygame.draw.circle(
                self.winner_surface,
                C_EMPTY,
                (px * TOKEN_CONTENT_SIZE + TOKEN_CONTENT_SIZE / 2,
                 py * TOKEN_CONTENT_SIZE + TOKEN_CONTENT_SIZE / 2),
                TOKEN_R - 3
            )

    def check_line(self, x, y, speed_x, speed_y):
        """This function return list of connected tokens of same color"""
        result = []
        current_color = self.table[y][x]
        # reverse move
        current_speed_x = -speed_x
        current_speed_y = -speed_y
        new_x = x + current_speed_x
        new_y = y + current_speed_y
        while (new_x > -1 and new_x < FIELD_COLUMNS and
               new_y > -1 and new_y < FIELD_ROWS and
               self.table[new_y][new_x] == current_color):    
            x = new_x
            y = new_y
            new_x = x + current_speed_x
            new_y = y + current_speed_y

        # count
        current_speed_x = speed_x
        current_speed_y = speed_y
        new_x = x + current_speed_x
        new_y = y + current_speed_y
        result.append((x, y))
        while True:
            if new_x == -1 or new_x == FIELD_COLUMNS: break
            if new_y == -1 or new_y == FIELD_ROWS: break
            if self.table[new_y][new_x] != current_color: break
            x = new_x
            y = new_y
            result.append((x, y))
            new_x = x + current_speed_x
            new_y = y + current_speed_y
        return result

    def refresh_token_surface(self):
        pygame.draw.rect(self.token_surface, C_BLACK, (0, 0, FIELD_WIDTH, FIELD_HEIGHT))
        shift_left = 0
        shift_top = 0

        for row in self.table:
            for column in row:
                pygame.draw.circle(
                    self.token_surface,
                    C_LIST[column],
                    (
                        shift_left + TOKEN_CONTENT_SIZE / 2,
                        shift_top + TOKEN_CONTENT_SIZE / 2
                    ),
                    TOKEN_R
                )
                shift_left += DRAW_TOKEN_SHIFT                
            shift_left = 0
            shift_top += DRAW_TOKEN_SHIFT
    
    def render_gui(self):
        # render active cursor column
        pygame.draw.rect(self.gui_surface, C_BLACK, (0, 0, PANEL_WIDTH, SCREEN_HEIGHT))
        self.gui_surface.blit(self.font.render("Turn:", 1, C_EMPTY), (16, 26))
        pygame.draw.circle(self.gui_surface, C_LIST[self.turn], (90 + TOKEN_CONTENT_SIZE / 2, TOKEN_CONTENT_SIZE / 2), TOKEN_R - 5)
        self.gui_surface.blit(self.font.render("".join(["Turns left: ", str(self.turns)]), 1, C_EMPTY), (16, 66))

        if self.state == self.state_end:
            self.gui_surface.blit(self.font.render("GAME OVER", 1, C_EMPTY), (16, 90))
            self.gui_surface.blit(self.font.render(STR_ARR_WINNER[self.winner], 1, C_EMPTY), (16, 120))
            self.gui_surface.blit(self.font.render("PRESS R TO RESTART", 1, C_EMPTY), (16, 150))
        self.screen.blit(self.gui_surface, (SCREEN_WIDTH - PANEL_WIDTH, 0))

        target_row, target_column = self.get_target()
        if target_column != -1:
            self.screen.blit(self.active_column_surface, (target_column * TOKEN_CONTENT_SIZE, 0))

    def render(self):
        pygame.draw.rect(self.screen, C_BLACK, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(self.token_surface, (0, 0))
        
        if self.falling_token:
            self.falling_token.render(self.screen)
        
        self.screen.blit(self.cover_surface, (0, 0))

        if self.winner_surface:
            self.screen.blit(self.winner_surface, (0, 0))

        self.render_gui()

        pygame.display.flip()

    def get_target(self):
        if (self.mouse[0] >= 0 and self.mouse[0] < FIELD_WIDTH and
            self.mouse[1] >= 0 and self.mouse[1] < FIELD_HEIGHT):
            return self.mouse[1] // TOKEN_CONTENT_SIZE, self.mouse[0] // TOKEN_CONTENT_SIZE
        else:
            return -1, -1

    def state_turn_wait(self):
        target_row, target_column = self.get_target()
        
        if self.click:
            if target_row != -1:
                if self.table[0][target_column] == 0:
                    print self.turn
                    self.falling_token = FallingToken(target_column * TOKEN_CONTENT_SIZE, -TOKEN_CONTENT_SIZE, self.turn)
                    self.state = self.state_animation_wait
                    self.turns -= 1

    def state_animation_wait(self):
        token_table_x_index = self.falling_token.x // TOKEN_CONTENT_SIZE
        token_table_y_index = self.falling_token.y // TOKEN_CONTENT_SIZE
        # print "INDEXES: ", token_table_x_index, token_table_y_index
        # print "TABLE: ", self.table[token_table_y_index + 1][token_table_x_index]
        # print "X and Y: ", self.falling_token.x, self.falling_token.y
        if token_table_y_index != FIELD_ROWS - 1 and self.table[token_table_y_index + 1][token_table_x_index] == 0:
            # check if there is where to fall
            self.falling_token.y += TOKEN_FALL_SPEED
        else:
            self.falling_token.render(self.token_surface)
            self.table[token_table_y_index][token_table_x_index] = self.falling_token.color;
            self.falling_token = None
            
            if not self.make_check_winner(token_table_x_index, token_table_y_index):
                self.switch_turn()
                self.state = self.state_turn_wait
    
    def state_end(self):
        if self.restart:
            self.game_start()

game = Game()
