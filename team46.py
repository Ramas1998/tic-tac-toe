import random
import datetime
import copy

class Team46:
    def __init__(self):
    	''' initialise variables'''
        self.INF = int(1e9)
        self.timeLimit = datetime.timedelta(seconds = 15)
        self.begin = 0
        self.mark = 'x'
        self.idx = 0
        self.depth = 0
        self.val = [[],[],[],[]]
        self.fac = [[],[],[],[]]
        for i in range(4):
            for j in range(4):
                self.val[i].append(4)
                self.fac[i].append(3)
                if self.is_corner(i,j):
                    self.val[i][j] = 6
                    self.fac[i][j] = 2
                elif self.is_centre(i,j):
                    self.val[i][j] = 3
                    self.fac[i][j] = 4
        
        # self.zobrist = [ [ [ [ [ random.randint(0, 2**64) , random.randint(0, 2**64) ] \
		#  for i in range(17) ] for j in range(17)] for k in range(16)] for l in range(16)]

    def move(self, board, old_move, flag):
    	''' start move '''
        self.mark = flag
        global board_copy
        board_copy = copy.deepcopy(board)
        board_state_map = copy.deepcopy(board.board_status)
        curr = copy.deepcopy(old_move)
        self.begin = datetime.datetime.utcnow()
        ans = self.IDS(curr)
        # print "final move: " , ans
        return ans

    def check_time(self):
    	''' check for timeout error '''
        if datetime.datetime.utcnow() - self.begin > self.timeLimit:
            return True
        return False

    def IDS(self, root):
    	''' Iterative deepeninng search'''
        guess = 0
        for depth in range(1, 8):
            self.depth = depth
            # print "---------------------", depth, "-------------------"
            guess, move = self.alpha_beta(True, root, -self.INF, self.INF, depth, False)
            # print(self.depth)
            if self.check_time() :
                break
            if guess > 100000000:
                return move
            saved_move = move
        return saved_move

    def alpha_beta(self, maxmove, root, alpha, beta, depth, bonusmove):
    	''' minimax alpha_beta'''
        status = board_copy.find_terminal_state()
        if status[1] == "WON":
            if status[0] == self.mark:
                return self.INF, root
            else:
                return -self.INF, root
    
        children = board_copy.find_valid_move_cells(root)
        random.shuffle(children)
        nSiblings = len(children)

        if depth == 0 or nSiblings == 0:
            answer = root
            if self.check_time():
                return 0, answer
            g = self.heuristic(maxmove, root, bonusmove)
            return g, answer
            
        if maxmove:
            g = -self.INF
            answer = children[0]
            if self.check_time():
                    return g, answer

            i = 0
            while (i < nSiblings):
                c = children[i]

                # Retain current block state for later restoration
                blockVal = board_copy.block_status[c[0]/4][c[1]/4]

                # Mark current node as taken by us for future reference
                board_copy.update(root, c, self.mark)

                #check for bonus move
                flag_occupied = board_copy.block_status[c[0]/4][c[1]/4]
                if flag_occupied == self.mark and not bonusmove :
                    val, temp = self.alpha_beta(True, c, alpha, beta, depth-1, True)
                else :
                    val, temp = self.alpha_beta(False, c, alpha, beta, depth-1, False)

                # Revert Board state
                board_copy.board_status[c[0]][c[1]] = '-'
                board_copy.block_status[c[0]/4][c[1]/4] = blockVal

                if val > g:
                    g = val
                    answer = c
                alpha = max(alpha, g)
                if self.check_time():
                    return g, answer
                if alpha >= beta :
                    break
                i = i + 1
            maxmove = True

        else:
            g = self.INF
            answer = children[0]
            if self.check_time():
                return g, answer
            i = 0
            while (i < nSiblings):
                c = children[i]
                # Retain current block state for later restoration
                blockVal = board_copy.block_status[c[0]/4][c[1]/4]

                oflag = self.mark
                if oflag == 'x':
                    oflag = 'o'
                else :
                    oflag = 'x'
                # Mark current node as taken by us for future reference
                board_copy.update(root, c, oflag)

                #check for bonus move
                flag_occupied = board_copy.block_status[c[0]/4][c[1]/4]
                
                if flag_occupied == oflag and not bonusmove :
                    val, temp = self.alpha_beta(False , c, alpha, beta, depth-1, True)
                else :
                    val, temp = self.alpha_beta(True, c, alpha, beta, depth-1, False)
                
                # Revert Board state
                board_copy.board_status[c[0]][c[1]] = '-'
                board_copy.block_status[c[0]/4][c[1]/4] = blockVal

                if val < g:
                    g = val
                    answer = c
                beta = min(beta, g)
                if self.check_time():
                    return g, answer
                if alpha >= beta :
                    break
                i = i + 1
            maxmove = False

        return g, answer

    def checkdiamond(self, currblockX, currblockY, flag, oflag, bs):
    	''' checking if diamond is forming based on top cell of diamond'''
        scounter = 0
        ocounter = 0
        save = [ [0, 0], [1,-1], [1,1], [2,0]]
        for cell in save:
            if bs[currblockX + cell[0] ][currblockY + cell[1]] is flag:
                scounter += 1
            elif bs[currblockX + cell[0] ][currblockY + cell[1] ] is oflag:
                ocounter += 1
        if not ocounter:
            return scounter
        return -1

    def is_centre(self, row, col):
    	''' checking for centre cell'''
        if row in (1,2) and col in (1,2):
            return 1
        return 0

    def is_corner(self, row, col):
    	''' checking for corner cell'''
        if row in (0,3) and col in (0,3):
            return 1
        return 0

    def check_current_board_state(self, segment, flag, oflag):
    	''' calculating heuristic based on current board state'''
        lheur = 0
        req_diamond = [(0,1), (0,2), (1,1), (1,2)]
        if flag is self.mark:
            val_arr = [ 0, 50, 325, 600]
            val_arr_diamond = [ 0, 50, 350, 700]
        else:
            val_arr = [0, 50, 240, 600]
            val_arr_diamond = [ 0, 50, 260, 600]
            
        flag_diamond = 1
        # check if any diamond will be possible
        if (segment[1][1] == segment[1][2] == oflag or \
            segment[1][1] == segment[2][1] == oflag or \
            segment[2][2] == segment[1][2] == oflag or \
            segment[2][2] == segment[2][1] == oflag):
            flag_diamond = 1.5

        if flag_diamond == 1:
            for cell in req_diamond:
                val = self.checkdiamond(cell[0],cell[1],flag,oflag,segment)
                if val == -1:
                    lheur -= 50
                else :
                    lheur += val_arr_diamond[val]

        # heuristic evaluation for rows and columns
        for i in range(4):
            scounter_row = 0
            ocounter_row = 0
            scounter_column = 0
            ocounter_column = 0
            for j in range(4):
                if segment[i][j] == flag:
                    scounter_row+=1
                elif segment[i][j] == oflag:
                    ocounter_row+=1

                if segment[j][i] == flag:
                    scounter_column+=1
                elif segment[j][i] == oflag:
                    ocounter_column+=1
            if ocounter_row == 0:
                lheur += flag_diamond * val_arr[scounter_row]

            if ocounter_column == 0:
                lheur += flag_diamond * val_arr[scounter_column]

        return lheur

    def check_oppwin(self, nextblockX, nextblockY, oflag, flag):
    	''' checking if opposition wins and eliminating it'''
        poss = 0
        board_status = board_copy.board_status
        for i in range(0,4):
            nuts = 0 
            for j in range(0,4):
                if (board_status[i+4*nextblockX][j+4*nextblockY] == oflag):
                    nuts+=1
                elif (board_status[i+4*nextblockX][j+4*nextblockY] == flag):
                    nuts-=1
            if nuts == 3:
                poss +=1

        for i in range(0,4):
            nuts = 0 
            for j in range(0,4):
                if (board_status[j+4*nextblockX][i+4*nextblockY] == oflag):
                    nuts+=1
                elif (board_status[j+4*nextblockX][i+4*nextblockY] == flag):
                    nuts-=1
            if nuts == 3:
                poss +=1
        
        for i in range(0,2):
            for j in range(0,2):
                diam =  board_status[4*nextblockX+i][4*nextblockY+j+1] == oflag + \
                        board_status[4*nextblockX+i+1][4*nextblockY+j] == oflag + \
                        board_status[4*nextblockX+i+1][4*nextblockY+j+2] == oflag + \
                        board_status[4*nextblockX+i+2][4*nextblockY+j+1] == oflag - \
                        board_status[4*nextblockX+i][4*nextblockY+j+1] == flag - \
                        board_status[4*nextblockX+i+1][4*nextblockY+j] == flag - \
                        board_status[4*nextblockX+i+1][4*nextblockY+j+2] == flag - \
                        board_status[4*nextblockX+i+2][4*nextblockY+j+1] == flag
                if (diam ==3 ):
                    poss+=1
        return poss

    def heuristic(self, maxmove, move, bonusmove):
    	''' calculating heuristic value'''
        currblockX = move[0]/4
        currblockY = move[1]/4
        nextblockX = move[0]%4
        nextblockY = move[1]%4
        bs = board_copy.block_status
        BS = board_copy.board_status
        immwin = [500, -4000, -4500]
        flag = self.mark
        if flag == 'x':
            oflag = 'o'
        else:
            oflag = 'x'

        heur = 0

        if self.depth == 1 and not bonusmove and bs[currblockX][currblockY] == flag:
            children = board_copy.find_valid_move_cells((move[0], move[1]))
            for child in children:
                blockVal = board_copy.block_status[child[0]/4][child[1]/4]
                board_copy.update(move, child, flag)
                heur = 1000000000 + self.heuristic(child, 1)
                board_copy.board_status[child[0]][child[1]] = '-'
                board_copy.block_status[child[0]/4][child[1]/4] = blockVal
            return heur

        if bs[nextblockX][nextblockY] != '-':
            if maxmove:
                heur += 1500/self.depth
            else:
                heur -= 1500/self.depth

        if self.depth < 2:
            ret  = self.check_oppwin(nextblockX,nextblockY,oflag,flag)
            if ret >= len(immwin):
                heur -= 5000
            else:
                heur += immwin[ret]


        a, b = board_copy.find_terminal_state()
        if b == "WON":
            if a==flag:
                heur += 1000000000
            elif a==oflag:
                heur -= 1000000000
        elif b == "DRAW":
            pts1=0
            pts2=0
            for i in range(4):
                for j in range(4):
                    if board_copy.block_status[i][j] == flag:
                        pts1 += self.val[i][j]
                    if board_copy.block_status[i][j] == oflag:
                        pts2 += self.val[i][j]
            heur+=(pts1-pts2)*25
        else:
            for i in range(4):
                for j in range(4):
                    if bs[i][j] == flag:
                        heur += self.val[i][j] * 120
                    elif bs[i][j] == oflag:
                        heur -= self.val[i][j] * 120
                    else:
                        temp = [ [BS[4*i+k][4*j+l] for l in range(4)] for k in range(4)]
                        scale = 1
                        heur += self.check_current_board_state(temp, flag, oflag) * self.fac[i][j] /(2 * self.depth)
                        heur -= self.check_current_board_state(temp, oflag, flag) * self.fac[i][j] /(2 * self.depth)

            heur += self.check_current_board_state(bs, flag, oflag) * 7 / self.depth
            heur -= self.check_current_board_state(bs, oflag, flag) * 7 / self.depth
        return heur


# class Team46:
#     def __init__(self):
#         self.INF = int(1e9)
#         self.maxmove = False
#         self.timeLimit = datetime.timedelta(seconds = 2)
#         self.begin = 0
#         self.mark = 'x'
#         self.transpositionTable = {}
#         self.index = 0
#         self.moveOrder = dict()
#         self.depth = 0
#         self.val = [[],[],[],[]]
#         self.fac = [[],[],[],[]]
#         for i in range(4):
#             for j in range(4):
#                 self.val[i].append(4)
#                 self.fac[i].append(3)
#                 if self.is_corner(i,j):
#                     self.val[i][j] = 6
#                     self.fac[i][j] = 2
#                 elif self.is_centre(i,j):
#                     self.val[i][j] = 3
#                     self.fac[i][j] = 4
        
#         self.zobrist = [ [ [ [ [ random.randint(0, 2**64) , random.randint(0, 2**64) ] \
# 		 for i in range(17) ] for j in range(17)] for k in range(16)] for l in range(16)]

#     def move(self, board, old_move, flag):
#         self.mark = flag
#         global board_copy
#         board_copy = copy.deepcopy(board)
#         curr = copy.deepcopy(old_move)
#         self.begin = datetime.datetime.utcnow()
#         ans = self.IDS(curr)
#         print "final move: " , ans
#         return ans

#     def check_time(self):
#         if datetime.datetime.utcnow() - self.begin > self.timeLimit:
#             return True
#         return False

#     def IDS(self, root):
#         guess = 0
#         for depth in range(1, 8):
#             self.depth = depth
#             self.transpositionTable = {}
#             guess, move = self.MTDF(root, guess, depth)
#             print(self.depth)
#             if self.check_time() :
#                 break
#             if guess > 100000000:
#                 return move
#             saved_move = move
#         return saved_move

#     def MTDF(self, root, guess, depth):
#         g = guess
#         upperbound = self.INF
#         lowerbound = -self.INF
#         while lowerbound < upperbound:
#             if g == lowerbound:
#                 beta = g + 1
#             else:
#                 beta = g
#             self.index = 0
#             self.maxmove = True
#             g, move = self.AlphaBetaWithMemory(root, beta - 1, beta, depth)
#             if self.check_time():
#                 return g, move
#             if g < beta:
#                 upperbound = g
#             else:
#                 lowerbound = g
#         return g, move

#     def calcZobristHash(self, root):
#         h = 0
#         bs = board_copy.board_status
#         for i in range(0, 16):
#             for j in range(0, 16):
#                 if bs[i][j] == 'x':
#                     h = h^self.zobrist[i][j][root[0]+1][root[1]+1][0]
#                 elif bs[i][j] == 'o':
#                     h = h^self.zobrist[i][j][root[0]+1][root[1]+1][1]
#         return h

#     def cantorPairing(self, a, b):
#         return (a + b)*(a + b + 1)/2 + b

#     def getMarker(self, flag):
#         if flag == 'x':
#             return 'o'
#         return 'x'

#     def AlphaBetaWithMemory(self, root, alpha, beta, depth):
#         board_hash = self.calcZobristHash(root)
#         loweridx = self.cantorPairing(board_hash, 1)
#         upperidx = self.cantorPairing(board_hash, 2)

#         lower = -2*self.INF, root
#         upper = 2*self.INF, root

#         # Transposition table lookup
#         if (loweridx in self.transpositionTable):
#             lower = self.transpositionTable[loweridx]
#             if (lower[0] >= beta):
#                 return lower

#         if (upperidx in self.transpositionTable):
#             upper = self.transpositionTable[upperidx]
#             if (upper[0] <= alpha):
#                 return upper

#         status = board_copy.find_terminal_state()
#         if status[1] == "WON":
#             if self.maxmove:
#                 return -self.INF, root
#             else:
#                 return self.INF, root
    
#         # Update values of alpha and beta based on values in Transposition Table
#         alpha = max(alpha, lower[0])
#         beta = min(beta, upper[0])

#         # Get Unique Hash for moveOrder Table lookup
#         moveHash = self.cantorPairing(board_hash, self.index)
#         moveInfo = []

#         # Reordered moves already present!
#         if moveHash in self.moveOrder:
#             children = []
#             children.extend(self.moveOrder[moveHash])
#             nSiblings = len(children)

#         else:
#             children = board_copy.find_valid_move_cells(root)
#             nSiblings = len(children)

#         if depth == 0 or nSiblings == 0:
#             answer = root
#             if self.check_time():
#                 return 0, answer
#             g = self.heuristic(root, 0)

#         # Node is a max node
#         elif self.maxmove:
#             g = -self.INF
#             answer = children[0]
#             # Return value if time up
#             if self.check_time():
#                     return g, answer

#             # Save original alpha value
#             a = alpha
#             i = 0
#             while ((g < beta) and (i < nSiblings)):
#                 self.maxmove = False
#                 c = children[i]

#                 #Retain current block state for later restoration
#                 blockVal = board_copy.block_status[c[0]/4][c[1]/4]

#                 # Mark current node as taken by us for future reference
#                 board_copy.update(root, c, self.mark)
#                 self.index += 1

#                 val, temp = self.AlphaBetaWithMemory(c, a, beta, depth-1)

#                 # Revert Board state
#                 board_copy.board_status[c[0]][c[1]] = '-'
#                 board_copy.block_status[c[0]/4][c[1]/4] = blockVal
#                 self.index -= 1

#                 # Append returned values to moveInfo
#                 temp = (val, c)
#                 moveInfo.append(temp)

#                 if val > g:
#                     g = val
#                     answer = c

#                 a = max(a, g)
#                 i = i + 1
#             self.maxmove = True

#         # Node is a min node
#         else:
#             g = self.INF
#             answer = children[0]
#             # Return value if time up
#             if self.check_time():
#                 return g, answer
#             # Save original beta value
#             b = beta
#             i = 0
#             while ((g > alpha) and (i < nSiblings)):
#                 self.maxmove = True
#                 c = children[i]
#                 # Retain current block state for later restoration
#                 blockVal = board_copy.block_status[c[0]/4][c[1]/4]

#                 # Mark current node as taken by us for future reference
#                 board_copy.update(root, c, self.getMarker(self.mark))
#                 self.index += 1

#                 val, temp = self.AlphaBetaWithMemory(c, alpha, b, depth-1)

#                 # Revert Board state
#                 board_copy.board_status[c[0]][c[1]] = '-'
#                 board_copy.block_status[c[0]/4][c[1]/4] = blockVal
#                 self.index -= 1

#                 # Append returned values to moveInfo
#                 temp = (val, c)
#                 moveInfo.append(temp)

#                 if val < g:
#                     g = val
#                     answer = c

#                 b = min(b, g)
#                 i = i + 1
#             self.maxmove = False

#         temp = []

#         if self.maxmove:
#             moveInfo = sorted(moveInfo, reverse = True)
#         else:
#             moveInfo = sorted(moveInfo)

#         for i in moveInfo:
#             temp.append(i[1])
#             children.remove(i[1])

#         random.shuffle(children)

#         self.moveOrder[moveHash] = []
#         self.moveOrder[moveHash].extend(temp)
#         self.moveOrder[moveHash].extend(children)

#         # if(len(self.moveOrder[moveHash]) != nSiblings):

#         # Traditional transposition table storing of bounds
#         # ----------------------------------------------------#
#         # Fail low result implies an upper bound
#         if g <= alpha:
#             self.transpositionTable[upperidx] = g, answer

#         # Fail high result implies a lower bound
#         if g >= beta:
#             self.transpositionTable[loweridx] = g, answer

#         return g, answer

#     def checkdiamond(self, currblockX, currblockY, flag, oflag, bs):
#         scounter = 0
#         ocounter = 0
#         save = [ [0, 0], [1,-1], [1,1], [2,0]]
#         for cell in save:
#             if bs[currblockX + cell[0] ][currblockY + cell[1]] is flag:
#                 scounter += 1
#             elif bs[currblockX + cell[0] ][currblockY + cell[1] ] is oflag:
#                 ocounter += 1
#         if not ocounter:
#             return scounter
#         return -1

#     def is_centre(self, row, col):
#         if row in (1,2) and col in (1,2):
#             return 1
#         return 0

#     def is_corner(self, row, col):
#         if row in (0,3) and col in (0,3):
#             return 1
#         return 0

#     def check_current_board_state(self, segment, flag, oflag):
#         lheur = 0
#         req_diamond = [(0,1), (0,2), (1,1), (1,2)]
#         val_arr = [ 50, 100, 225, 400]
#         val_arr_diamond = [ 100, 200, 450, 800]
#         flag_diamond = 1
#         if (segment[1][1] == segment[1][2] == oflag or \
#             segment[1][1] == segment[2][1] == oflag or \
#             segment[2][2] == segment[1][2] == oflag or \
#             segment[2][2] == segment[2][1] == oflag):
#             flag_diamond = 1.5

#         if flag_diamond == 1:
#             for cell in req_diamond:
#                 val = self.checkdiamond(cell[0],cell[1],flag,oflag,segment)
#                 if val == -1:
#                     lheur -= 50
#                 else :
#                     lheur += val_arr_diamond[val]

#         for i in range(4):
#             scounter_row = 0
#             ocounter_row = 0
#             scounter_column = 0
#             ocounter_column = 0
#             for j in range(4):
#                 if segment[i][j] == flag:
#                     scounter_row+=1
#                 elif segment[i][j] == oflag:
#                     ocounter_row+=1

#                 if segment[j][i] == flag:
#                     scounter_column+=1
#                 elif segment[j][i] == oflag:
#                     ocounter_column+=1
#             if ocounter_row == 0:
#                 lheur += val_arr[scounter_row]

#             if ocounter_column == 0:
#                 lheur += val_arr[scounter_column]

#             if scounter_row == 0:
#                 lheur -= val_arr[ocounter_row]

#             if scounter_column == 0:
#                 lheur -= val_arr[ocounter_column]

#         return lheur

#     def check_oppwin(self, nextblockX, nextblockY, oflag, flag):
#         poss = 0
#         board_status = board_copy.board_status
#         for i in range(0,4):
#             nuts = 0 
#             for j in range(0,4):
#                 if (board_status[i+4*nextblockX][j+4*nextblockY] == oflag):
#                     nuts+=1
#                 elif (board_status[i+4*nextblockX][j+4*nextblockY] == flag):
#                     nuts-=1
#             if nuts == 3:
#                 poss +=1

#         for i in range(0,4):
#             nuts = 0 
#             for j in range(0,4):
#                 if (board_status[j+4*nextblockX][i+4*nextblockY] == oflag):
#                     nuts+=1
#                 elif (board_status[j+4*nextblockX][i+4*nextblockY] == flag):
#                     nuts-=1
#             if nuts == 3:
#                 poss +=1
        
#         for i in range(0,2):
#             for j in range(0,2):
#                 diam =  board_status[4*nextblockX+i][4*nextblockY+j+1] == oflag + \
#                         board_status[4*nextblockX+i+1][4*nextblockY+j] == oflag + \
#                         board_status[4*nextblockX+i+1][4*nextblockY+j+2] == oflag + \
#                         board_status[4*nextblockX+i+2][4*nextblockY+j+1] == oflag - \
#                         board_status[4*nextblockX+i][4*nextblockY+j+1] == flag - \
#                         board_status[4*nextblockX+i+1][4*nextblockY+j] == flag - \
#                         board_status[4*nextblockX+i+1][4*nextblockY+j+2] == flag - \
#                         board_status[4*nextblockX+i+2][4*nextblockY+j+1] == flag
#                 if (diam ==3 ):
#                     poss+=1
#         return poss

#     def heuristic(self, move, bonusmove):

#         currblockX = move[0]/4
#         currblockY = move[1]/4
#         nextblockX = move[0]%4
#         nextblockY = move[1]%4
#         bs = board_copy.block_status
#         BS = board_copy.board_status
#         immwin = [500, -2000, -2200, -2300]
#         flag = self.mark
#         if flag == 'x':
#             oflag = 'o'
#         else:
#             oflag = 'x'

#         heur = 0

#         if self.depth == 1 and not bonusmove and bs[currblockX][currblockY] == flag:
#             children = board_copy.find_valid_move_cells((move[0], move[1]))
#             for child in children:
#                 blockVal = board_copy.block_status[child[0]/4][child[1]/4]
#                 board_copy.update(move, child, flag)
#                 heur = 1000000000 + self.heuristic(child, 1)
#                 board_copy.board_status[child[0]][child[1]] = '-'
#                 board_copy.block_status[child[0]/4][child[1]/4] = blockVal


#         # if self.depth == 1 and bs[currblockX][currblockY] == flag :

#         if bs[nextblockX][nextblockY] != '-':
#             if self.maxmove:
#                 heur += 1500/self.depth
#             else:
#                 heur -= 1500/self.depth

#         if self.depth < 2:
#             ret  = self.check_oppwin(nextblockX,nextblockY,oflag,flag)
#             if ret > len(immwin):
#                 heur -= 2500
#             else:
#                 heur += immwin[ret]


#         a, b = board_copy.find_terminal_state()
#         if b == "WON":
#             if a==flag:
#                 heur += 100000000
#             elif a==oflag:
#                 heur -= 100000000
#         elif b == "DRAW":
#             pts1=0
#             pts2=0
#             for i in range(4):
#                 for j in range(4):
#                     if board_copy.block_status[i][j] == flag:
#                         pts1 += self.val[i][j]
#                     if board_copy.block_status[i][j] == oflag:
#                         pts2 += self.val[i][j]
#             heur+=(pts1-pts2)*20
#         else:
#             for i in range(4):
#                 for j in range(4):
#                     if bs[i][j] == flag:
#                         heur += self.val[i][j] *  120
#                     elif bs[i][j] == oflag:
#                         heur -= self.val[i][j] * 120
#                     else:
#                         temp = [ [BS[4*i+k][4*j+l] for l in range(4)] for k in range(4)]
#                         heur += self.check_current_board_state(temp, flag, oflag) * self.fac[i][j] /6
#                         heur -= self.check_current_board_state(temp, oflag, flag) * self.fac[i][j] /6

#             heur += self.check_current_board_state(bs, flag, oflag) * 4
#             heur -= self.check_current_board_state(bs, oflag, flag) * 4
#         if self.depth % 2 == 1 and self.is_centre(nextblockX, nextblockY) :
#             return heur * 0.85
#         return heur

        # if bs[currblockX][currblockY] == flag:
        #   heur+=1000
        #   if (currblockX == 1 or currblockX == 2) and (currblockY == 0 or currblockY == 1):
        #       scounter = 0
        #       scounter = self.checkdiamond(currblockX, currblockY, up, flag, oflag)
        #       if scounter is not (-1):
        #           heur += scounter*400
        #   if (currblockX == 1 or currblockX == 2) and (currblockY == 2 or currblockY == 3):
        #       scounter = 0
        #       scounter = self.checkdiamond(currblockX, currblockY, down, flag, oflag)
        #       if scounter is not (-1):
        #           heur += scounter*400
        #   if (currblockX == 0) and (currblockY == 1 or currblockY == 2):
        #       scounter = 0
        #       scounter = self.checkdiamond(currblockX, currblockY, left, flag, oflag)
        #       if scounter is not (-1):
        #           heur += scounter*400
        #   if (currblockX == 3) and (currblockY == 1 or currblockY == 2):
        #       scounter = 0
        #       scounter = self.checkdiamond(currblockX, currblockY, right, flag, oflag)
        #       if scounter is not (-1):
        #           heur += scounter*400
            
        # elif bs[currblockX][currblockY] == oflag:
        #   heur-=300
