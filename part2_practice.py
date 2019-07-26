
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import random

def get_driver():
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options = option)
    return driver

class AI2048:
    def __init__(self):
        self.driver = get_driver()
        self.driver.get('https://play2048.co/')
        self.size = 4 # 盤面行列大小

        # 盤面資訊(二維list儲存)
        self.cells = [[0 for _ in range(self.size)] for _ in range(self.size)]

        # 移動策略(包含四個移動方向)
        self.strategies = [{ 'action': Keys.UP,    'direction': 'up' }, 
                           { 'action': Keys.DOWN,  'direction': 'down' }, 
                           { 'action': Keys.LEFT,  'direction': 'left' }, 
                           { 'action': Keys.RIGHT, 'direction': 'right' }]

    # 用來算盤面分數的函式
    def get_score(self, result):
        cells = result['cells']
        total_score = result['score1']

        # 拿出每一行的資料呼叫 get_score2_and_score3 函式
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(cells[i][j])
            total_score += self.get_score2_and_score3(row)

        # 拿出每一列的資料呼叫 get_score2_and_score3 函式
        for i in range(self.size):
            col = []
            for j in range(self.size):
                col.append(cells[j][i])
            total_score += self.get_score2_and_score3(col)

        """ 另一種寫法
        for i in range(self.size):
            total_score += self.get_score2_and_score3([cells[i][j] for j in range(self.size)])
            total_score += self.get_score2_and_score3([cells[j][i] for j in range(self.size)])
        """
        return total_score

    # 用來算一行或一列的(score2 + score3)的函式
    def get_score2_and_score3(self, line):
        score2 = 0
        score3 = 0
        for i in range(self.size - 1):
            if line[i + 1] > line[i]:
                score2 += line[i + 1] + line[i]
            else:
                score2 -= line[i + 1] + line[i]
            if line[i + 1] == line[i]:
                score3 += line[i]
        return abs(score2) * 0.3 + score3

    def first_move(self):
        best_action = None
        best_score = -10000

        for strategy in self.strategies:
            layer1_result = self.try_move(self.cells, strategy['direction'])

            if layer1_result['movable']:
                score = self.set_number(layer1_result)
                if (best_score < score):
                    best_action = strategy['action']
                    best_score = score

        return best_action

    def set_number(self, layer1_result):
        empty_pos = self.get_empty_positions(layer1_result['cells'])
        total_score = 0
        total_movable = 0

        # 找每個盤面的空白處
        for pos in empty_pos:
            # 在該空白處依照機率分佈放入 2 或 4
            tile = random.choice([2] * 9 + [4])
            cells = [[layer1_result['cells'][i][j] for j in range(self.size)] for i in range(self.size)]
            cells[pos // self.size][pos % self.size] = tile

        ########## 把程式碼寫在這行下面 ##########
            score = self.second_move(cells)
            if score > 0 : 
                total_score += score + layer1_result['score1']
                total_movable += 1
        if total_movable == 0 :
            return 0
        else :
            return total_score / total_movable


        ########## 把程式碼寫在這行上面 ##########

    def second_move(self, cells):
        best_score = -10000
            
        ########## 把程式碼寫在這行下面 ##########
        for strategy in self.strategies:
            result = self.try_move(cells, strategy['direction'])
            if result['movable']:
                score = self.get_score(result)
                if score > best_score : 
                    best_score = score

        ########## 把程式碼寫在這行上面 ##########

        return best_score

    def play(self):
        # 每次做出移動決策之前，先到網頁到拿取盤面資訊
        try:
            self.get_cells()
        except:
            return True

        action = self.first_move()
        if action == None: # 沒辦法移動(死局)
            return False
        
        # 送出決定的移動方向給瀏覽器
        self.driver.find_element_by_tag_name('body').send_keys(action)
        return True

    def try_move(self, cells, direction):
        if direction == 'up':
            return self.try_up(cells)
        if direction == 'down':
            return self.try_down(cells)
        if direction == 'left':
            return self.try_left(cells)
        if direction == 'right':
            return self.try_right(cells)

    def try_left(self, cells):
        tmp_cells = [[cells[i][j] for j in range(self.size)] for i in range(self.size)]
        '''
        a = []
        for i in range(100):
            a.append(i)

        a = [i for i in range(100)]
        '''


        return self.move_left(tmp_cells)
 
    def try_right(self, cells):
        tmp_cells = [[cells[i][self.size - 1 - j] for j in range(self.size)] for i in range(self.size)]
        result = self.move_left(tmp_cells)
        result['cells'] = [[result['cells'][i][self.size - 1 - j] for j in range(self.size)] for i in range(self.size)]
        return result

    def try_up(self, cells):
        tmp_cells = [[cells[j][i] for j in range(self.size)] for i in range(self.size)]
        result = self.move_left(tmp_cells)
        result['cells'] = [[result['cells'][j][i] for j in range(self.size)] for i in range(self.size)]
        return result
     
    def try_down(self, cells):
        tmp_cells = [[cells[self.size - 1 - j][i] for j in range(self.size)] for i in range(self.size)]
        result = self.move_left(tmp_cells)
        result['cells'] = [[result['cells'][j][self.size - 1 - i] for j in range(self.size)] for i in range(self.size)]
        return result

        #
    def move_left(self, cells):
        movable = False
        score1 = 0
        for x in range(self.size):
            # 如果有空格就往左推
            # e.g. 2 0 2 4 -> 2 2 4 0 
            pre = 0
            for y in range(self.size):
                if cells[x][y]:
                    cells[x][pre] = cells[x][y]
                    if y != pre:
                        cells[x][y] = 0
                        movable = True
                    pre += 1

            # 合併鄰近的tile
            # e.g. 2 2 4 0 -> 4 0 4 0
            for y in range(self.size - 1):
                if cells[x][y] and cells[x][y] == cells[x][y + 1]:
                    cells[x][y] += cells[x][y]
                    score1 += cells[x][y]
                    cells[x][y + 1] = 0
                    movable = True

            # 再一次如果有空格就往左推
            # e.g. 4 0 4 0 -> 4 4 0 0 
            pre = 0
            for y in range(self.size):
                if cells[x][y]:
                    cells[x][pre] = cells[x][y]
                    if y != pre:
                        cells[x][y] = 0
                        #movable = True
                    pre += 1

        return { 'movable': movable, 'score1': score1, 'cells': cells }

    # 取得網頁上的盤面資訊
    def get_cells(self):
        self.cells = [[0 for _ in range(self.size)] for _ in range(self.size)]
        tiles = self.driver.find_elements_by_class_name('tile')

        # example class "tile tile-8 tile-position-1-2"
        for tile in tiles:
            attr = tile.get_attribute('class').split()
            value = int(attr[1].split('-')[1]) # example: 8
            x = int(attr[2].split('-')[3]) - 1 # example: 1
            y = int(attr[2].split('-')[2]) - 1 # example: 0
            self.cells[x][y] = value

    # 獲得盤面上空著的位置
    def get_empty_positions(self, cells):
        return [i for i in range(self.size * self.size) if cells[i // self.size][i % self.size] == 0]


# 主程式碼
ai = AI2048()
sleep(2)

while ai.play():
    sleep(0.02)

sleep(5)
ai.driver.quit()
