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
        self.players = []
        for i in range(players):
            self.players.append(Player(self,name=str(i)))
        self.__shuffle()

    def __shuffle(self):
        self._deck = Cards.cards()
        random.shuffle(self._deck)

    def draw_card(self):
        return self._deck.pop()

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
        
    def turn(self, max_score: int) -> None:
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
            logging.info(f"[Player {self.name}] new score: {self.round_score}")

    def play_freeze(self) -> None:
        pass

    def play_draw_3(self) -> None:
        pass

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
    p1 = Player(game)
    for i in range(50):
        p1.turn(0)
        if p1.active == False:
            print("*"*80)
            print("New Round")
            print("*"*80)
            p1.active = True
        else:
            print("-"*80)
    pass