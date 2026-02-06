import random
import logging

logging.basicConfig(level=logging.INFO)

class Cards:
    @staticmethod
    def cards() -> list:
        deck = [0]
        for i in range(1,13):
            for j in range(i):
                deck += [i]
        deck += ['+2']
        deck += ['+4']
        deck += ['+6']
        deck += ['+8']
        deck += ['+10']
        deck += ['x2']
        deck += ['draw 3'] * 3
        deck += ['freeze'] * 3
        deck += ['life'] * 3
        return deck
        

class Game:
    def __init__(self,players:int = 4) -> None:
        self.players: list[Player] = []
        for i in range(players):
            self.players.append(Player(self,name=str(i)))
        self.__shuffle()

    def __shuffle(self):
        self._deck = Cards.cards()
        random.shuffle(self._deck)

    def draw_card(self):
        return self._deck.pop()
    
    def play_game(self) -> None:
        max_score = 0
        #while max_score < 200:
        while self.check_active_players():
            round_max_score = 0
            
            for player in self.players:
                if player.active:
                    active, score, game_score = player.turn(max_score)
                    max_score = max(game_score, max_score)
                    round_max_score = max(score,round_max_score)

                    if player.count_hand() > 6:
                        player.game_score = player.round_score + 15
                        player.active = False
                        logging.info(f"Player {player.name}] won the round + 15 bonus - total {player.round_score+15}")
                        break
        for player in self.players:
            player.reset_hand()
            player.active = True
            player.round_score = 0

    def check_active_players(self) -> bool:
        for player in self.players:
            if player.active:
                return True
        return False
    
    def play_freeze(self, calling_player: 'Player') -> None:
        max_player = None
        for player in self.players:
            if player != calling_player and player.active:
                if max_player is None or (player.game_score + player.round_score) > (max_player.game_score + max_player.round_score):
                    max_player = player

        freeze_player = max_player if max_player is not None else calling_player
        freeze_player.active = False
        logging.info(f"[Player {calling_player.name}] froze Player {freeze_player.name}")

    def play_draw_3(self, calling_player: 'Player') -> None:
        max_player = None
        max_score = 0
        for player in self.players:
            max_score = max(max_score, player.game_score)
            if player != calling_player and player.active:
                if max_player is None or (player.game_score + player.round_score) > (max_player.game_score + max_player.round_score):
                    max_player = player

        draw_player = max_player if max_player is not None else calling_player
        logging.info(f"[Player {calling_player.name}] forced Player {draw_player.name} to draw 3 cards")
        for _ in range(3):
            draw_player.turn(max_score)
            if not draw_player.active:
                break
        

class Player:
    def __init__(self, game: Game, name:str = '') -> None:
        self.game = game
        self.reset_hand()
        self.game_score = 0
        self.round_score = 0
        self.active = True

        if name == '':
            self.name = hash(self)
        else: 
            self.name = name

    def reset_hand(self) -> None:
        self.hand = [0] * 20

    def add_card_to_hand(self, card) -> None:
        logging.info(f"[Player {self.name}] added card to hand: {card}")
        if type(card) == int:
            self.hand[card] = 1
        elif card == '+2':
            self.hand[13] = 1
        elif card == '+4':
            self.hand[14] = 1
        elif card == '+6':
            self.hand[15] = 1
        elif card == '+8':
            self.hand[16] = 1
        elif card == '+10':
            self.hand[17] = 1
        elif card == 'x2':
            self.hand[18] = 1
        elif card == 'life':
            self.hand[19] = 1

    def calculate_score(self) -> int:
        score = 0
        for i in range(13):
            score += self.hand[i] * i
        if self.hand[13]: score += 2
        if self.hand[14]: score += 4
        if self.hand[15]: score += 6
        if self.hand[16]: score += 8
        if self.hand[17]: score += 10
        if self.hand[18]: score *= 2
        return score
        
    def turn(self, max_score: int) -> tuple[bool, int, int]:
        def determine_vector():
            return self.hand + [self.round_score,self.game_score,max_score]
        vector = determine_vector()

        logging.info(f"[Player {self.name}] starting hand: {self.hand_to_str()}")

        action = self.determine_action(vector)

        logging.info(f"[Player {self.name}] action: {action}")

        reward = 0

        if action == 0:
            self.active = False
            self.game_score += self.round_score
            logging.info(f"[Player {self.name}] locked in for {self.round_score} points")
            self.round_score = 0
            reward = 0 #TODO
            self.learn(vector,action,reward,vector)
            
        else:
            new_card = self.game.draw_card()
            logging.info(f"[Player {self.name}] drew {new_card}")
            if type(new_card)==int:
                if self.check_busted(new_card):
                    if self.try_to_use_life():
                        logging.info(f'[Player {self.name}] Used Extra life Card!')
                    else:
                        logging.info(f'[Player {self.name}] Busted!')
                        self.active = False
                        self.round_score = 0
                        reward = -5 #TODO Busted
                else:
                    self.add_card_to_hand(new_card)
                    self.round_score = self.calculate_score()
            else:
                new_card = str(new_card)
                if new_card == 'freeze':
                    self.play_freeze()
                elif new_card == 'draw 3':
                    self.play_draw_3()
                else:
                    self.add_card_to_hand(new_card)
                    self.round_score = self.calculate_score()

            self.learn(vector,action,reward,new_state=determine_vector())
        if self.active == False:
            self.reset_hand()
        else:
            logging.info(f"[Player {self.name}] new hand: {self.hand_to_str()}")
            logging.info(f"[Player {self.name}] # of cards: {self.count_hand()}")
            logging.info(f"[Player {self.name}] new score: {self.round_score}")
        logging.info('*'*80)
        return (self.active,self.round_score,self.game_score)

    def play_freeze(self) -> None:
        self.game.play_freeze(self)

    def play_draw_3(self) -> None:
        self.game.play_draw_3(self)

    def check_busted(self, card: int) -> bool:
        return self.hand[card] == 1

    def determine_action(self, vector: list[int]) -> bool:
        return True
    
    def learn(self,vector: list[int], action: bool, reward: int, new_state: list[int]) -> None:
        pass

    def try_to_use_life(self) -> bool:
        if self.hand[19]:
            self.hand[19] = 0
            return True
        return False

    def count_hand(self) -> int:
        return sum(self.hand[:13])

    def hand_to_str(self) -> str:
        special_cards = {
            13: '+2', 
            14: '+4', 
            15: '+6', 
            16: '+8', 
            17: '+10', 
            18: 'x2', 
            19: 'life'
        }
        
        hand_string = ''
        for i in range(len(self.hand)):
            if self.hand[i] != 0:
                if i > 12:
                    hand_string += special_cards[i] + ' '
                else:
                    hand_string += str(i) + ' '
        return hand_string
        




if __name__ == '__main__':
    game = Game()
    game.play_game()
    pass