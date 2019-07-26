
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import random

#開啟瀏覽器玩2048的⼯具
def get_driver():
    option = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options = option)
    return driver

class AI2048:
    #做初始化設定的函式
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
        total_score = result['score1'] # score1已經算好了
        
        # 試著把三種評分加起來
        ########## 把程式碼寫在這行下面 ##########
        for i in range(4) : 
            total_score += self.get_score2_and_score3(cells[i])
        for i in range(4) : 
            line = []
            for j in range(4) : 
                line.append(cells[j][i])
            total_score += self.get_score2_and_score3(line)
        ########## 把程式碼寫在這行上面 ##########


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

    #決定要怎麼移動的函式
    def move(self):
        best_action = None
        best_score = -10000

        # 先把 63 ~ 71行 刪掉 (這是隨機滑動的版本)
        # 試著比較往四個方向滑動，哪一個分數最高，然後把對應的按鍵操作(Keys.xx)存在best_action
        ########## 把程式碼寫在這行下面 ##########
        for strategy in self.strategies:
            result = self.try_move(self.cells, strategy['direction'])
            if result['movable']:
                score = self.get_score(result)
                if score > best_score : 
                    best_score = score
                    best_action = strategy['action']
        

        ########## 把程式碼寫在這行上面 ##########

        return best_action

    #判斷遊戲是否結束的函式
    def play(self):
        # 每次做出移動決策之前，先到網頁到拿取盤面資訊
        try:
            self.get_cells()
        except:
            return True

        action = self.move()
        if action == None: # 沒辦法移動(死局)
            return False
        
        # 送出最好的滑動方向給瀏覽器
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
                        movable = True
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
