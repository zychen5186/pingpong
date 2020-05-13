"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm
import random



def ml_loop(side: str):#呼叫此程式的程式中，助教已有設定好1P的板子side會設1P，所以def裡的程式直接依判別side值為何來決定該如何動作
    """
    The main loop for the machine learning process
    The `side` parameter can be used for switch the code for either of both sides,
    so you can write the code for both sides in the same script. Such as:
    ```python
    if side == "1P":
        ml_loop_for_1P()
    else:
        ml_loop_for_2P()
    ```
    @param side The side which this script is executed for. Either "1P" or "2P".
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here
    ball_served = False
    flag = 0    
    blocker_pre = 0

    def move_to(player, pred) : #move platform to predicted position to catch ball 
        if (player == '1P'):
            if scene_info["platform_1P"][0]+20  > (pred-5) and scene_info["platform_1P"][0]+20 < (pred+5): return 0 # NONE
            elif scene_info["platform_1P"][0]+20 <= (pred-5) : return 1 # goes right
            else : return 2 # goes left
        else :
            if scene_info["platform_2P"][0]+20  > (pred-10) and scene_info["platform_2P"][0]+20 < (pred+10): return 0 # NONE
            elif scene_info["platform_2P"][0]+20 <= (pred-10) : return 1 # goes right
            else : return 2 # goes left
        
    def ml_loop_for_1P(blocker_dir): #預測1P該在的位置
        global flag
        if(scene_info["ball"][1]<=260 and scene_info["ball"][1]>=240):
            print("ball_x",scene_info["ball"][1], scene_info["ball"][0])
        if scene_info["ball_speed"][1] > 0 : # 球正在向下 # ball goes down
            ball_x = scene_info["ball"][0]
            ball_y = scene_info["ball"][1]
            ball_speed_x = scene_info["ball_speed"][0]
            ball_speed_y = scene_info["ball_speed"][1]
            
            #判斷2P回球是否會打到blocker側邊            
            if(scene_info["ball"][1] <= 240):
 #               print()
                # x_top = (240-scene_info["ball"][1] ) / scene_info["ball_speed"][1]
                # x_bottom = (260-scene_info["ball"][1] ) / scene_info["ball_speed"][1]
                block_x = (240-scene_info["ball"][1] ) / scene_info["ball_speed"][1]
#                print(x)
                #print("x_top, x_bottom:", x_top, x_bottom)
                slope = abs(scene_info["ball_speed"][0] / scene_info["ball_speed"][1])
                conflict_pred = scene_info["ball"][0]+(scene_info["ball_speed"][0] * block_x)

                bound = conflict_pred // 200 # Determine if it is beyond the boundary 
                if (bound > 0): # pred > 200 # fix landing position #超出右邊邊界
                    if (bound%2 == 0) : 
                        conflict_pred = conflict_pred - bound*200  
                        flag = 1 #flag 1 表撞到blocker時往右                  
                    else :
                        conflict_pred = 200 - (conflict_pred - 200*bound)
                        flag = 2 #flag 2 表撞到blocker時往左
                elif (bound < 0) : # pred < 0 超出左邊邊界
                    if (bound%2 ==1) :
                        conflict_pred = abs(conflict_pred - (bound+1) *200)
                        flag = 1
                    else :
                        conflict_pred = conflict_pred + (abs(bound)*200)
                        flag = 2

                #bias = 20//abs(scene_info["ball_speed"][1])
                blocker_pos_pred = scene_info["blocker"][0] + (blocker_dir * block_x)
                if(blocker_pos_pred > 170):
                    blocker_pos_pred = 170 - (blocker_pos_pred - 170)#-5*bias
                elif(blocker_pos_pred < 0):
                    blocker_pos_pred = abs(blocker_pos_pred)#+5*bias
                # else:
                #     if(blocker_dir>0):
                #         blocker_pos_pred += 5*bias
                #     else:
                #         blocker_pos_pred -= 5*bias
                #確定球會撞到blocker左邊反彈
                # print(flag)
                # print("speed:", ball_speed_x, ball_speed_y)
                print("conflict_pred",conflict_pred)
                print("blocker:", scene_info["blocker"][0])
                print("blocker_pos_pred",blocker_pos_pred, blocker_pos_pred+30)
                if (flag == 1 and conflict_pred < (blocker_pos_pred + 15) and conflict_pred > (blocker_pos_pred-20*slope)) :
                    print("會撞到左邊")
                    ball_x = blocker_pos_pred
                    ball_y = 240 + ((blocker_pos_pred - conflict_pred) / slope)
                    ball_speed_x = -abs(scene_info["ball_speed"][0])
                #確定球會撞到blocker右邊反彈  
#                print(blocker_pos_pred+30, blocker_pos_pred+30+20*slope)
                if (flag == 2 and conflict_pred > (blocker_pos_pred+15) and conflict_pred < (blocker_pos_pred+30+20*slope)) :
                    print("會撞到右邊")
                    ball_x = blocker_pos_pred + 30
                    ball_y = 240 + ((conflict_pred - (blocker_pos_pred+30)) / slope)
                    ball_speed_x = abs(scene_info["ball_speed"][0])
                
            x = (scene_info["platform_1P"][1] - ball_y) // ball_speed_y # 幾個frame以後會需要接(y距離/ball y速度)  # x means how many frames before catch the ball
            pred = ball_x + (ball_speed_x * x)  # 預測最終位置 # pred means predict ball landing site 
            bound = pred // 200 # Determine if it is beyond the boundary
            if (bound > 0): # pred > 200 # fix landing position #超出右邊邊界
                if (bound%2 == 0) : 
                    pred = pred - bound*200                    
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) : # pred < 0 超出左邊邊界
                if (bound%2 ==1) :
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            #對回球瞬間做判斷，決定怎麼回會最好        
            if (x <= 1) :
                #print("pred:",pred)
                #print("1p platform", scene_info["platform_1P"][0],scene_info["platform_1P"][0]+40)
                if(pred<15):
                    return 2
                elif(pred>185):
                    return 1
                
                dist = (160+(420-scene_info["ball"][1])) / scene_info["ball_speed"][1]
                #計算球彈到blocker時的位置
                ball_blocker_pred = scene_info["ball"][0] + ((scene_info["ball_speed"][0])*dist)
                ball_blocker_cut_pred = scene_info["ball"][0] + ((scene_info["ball_speed"][0])*dist)
                if(abs(scene_info["ball_speed"][0])-scene_info["ball_speed"][1] == 0):
                    if(scene_info["ball_speed"][0]<0):
                        ball_blocker_cut_pred = scene_info["ball"][0] + ((scene_info["ball_speed"][0]-3)*dist)
                    else:
                        ball_blocker_cut_pred = scene_info["ball"][0] + ((scene_info["ball_speed"][0]+3)*dist)
                    
                ball_blocker_bound = ball_blocker_pred // 200
                ball_blocker_cut_bound = ball_blocker_cut_pred // 200
                #假設一般
                if (ball_blocker_bound > 0):
                    if (ball_blocker_bound%2 == 0):
                        ball_blocker_pred = ball_blocker_pred - ball_blocker_bound*200 
                    else :
                        ball_blocker_pred = 200 - (ball_blocker_pred - 200*ball_blocker_bound)
                elif (ball_blocker_bound < 0) :
                    if (ball_blocker_bound%2 ==1):
                        ball_blocker_pred = abs(ball_blocker_pred - (ball_blocker_bound+1) *200)
                    else :
                        ball_blocker_pred = ball_blocker_pred + (abs(ball_blocker_bound)*200)
                #假設切球
                if (ball_blocker_cut_bound > 0):
                    if (ball_blocker_cut_bound%2 == 0):
                        ball_blocker_cut_pred = ball_blocker_cut_pred - ball_blocker_cut_bound*200 
                    else :
                        ball_blocker_cut_pred = 200 - (ball_blocker_cut_pred - 200*ball_blocker_cut_bound)
                elif (ball_blocker_cut_bound < 0) :
                    if (ball_blocker_cut_bound%2 ==1):
                        ball_blocker_cut_pred = abs(ball_blocker_cut_pred - (ball_blocker_cut_bound+1) *200)
                    else :
                        ball_blocker_cut_pred = ball_blocker_cut_pred + (abs(ball_blocker_cut_bound)*200)                       
                #計算球到blocker y座標時，blocker此時位置        
                blocker_pos_pred = scene_info["blocker"][0] + (blocker_dir * dist)
                if(blocker_pos_pred > 170):
                    blocker_pos_pred = 170 - (blocker_pos_pred - 170)
                if(blocker_pos_pred < 0):
                    blocker_pos_pred = abs(blocker_pos_pred)
                #如果預測切球之後會使得球打到障礙物，則選擇反向反彈，但當反彈或切球都會撞到障礙物時則無法避免
                #print("ball_blocker_pred:" ,ball_blocker_pred, "blocker_pos_pred:", blocker_pos_pred, blocker_pos_pred+30)
                #print("ball_blocker_cut_pred:" ,ball_blocker_cut_pred, "blocker_pos_pred:", blocker_pos_pred, blocker_pos_pred+30)
                if(pred >= scene_info["platform_1P"][0]+40):
                    #print("右")
                    return 1
                elif(pred <= scene_info["platform_1P"][0]):
                    #print("左")
                    return 2                
                #blocker預測範圍加15增加容錯率
                elif(ball_blocker_cut_pred < blocker_pos_pred-12 or ball_blocker_cut_pred > blocker_pos_pred+42):
                    #print("accelerate")
                    if(scene_info["ball_speed"][0]<0 and not(scene_info["platform_1P"][0]+40-5 < pred)):
                        return 2
                    elif(scene_info["ball_speed"][0]>0 and not(scene_info["platform_1P"][0]+5 > pred)):
                        return 1
                elif(ball_blocker_pred < blocker_pos_pred-12 or ball_blocker_pred > blocker_pos_pred+42):
                    #print("NONE")
                    return 0
                else:
                    #print("reverse")
                    if(scene_info["ball_speed"][0]<0 and not(scene_info["platform_1P"][0]+5 > pred)):
                        return 1
                    elif(scene_info["ball_speed"][0]>0 and not(scene_info["platform_1P"][0]+40-5 < pred)):
                        return 2    

                    # print("random")
                    # if (rand < 0.33):
                    #     return 1
                    # elif (rand>=0.33 and rand<0.66):
                    #     return 2
                    # else:
                    #     return 0
            else:
                #print("normal")
                return move_to(player = '1P',pred = pred)

        else : # 球正在向上 # ball goes up
            flag = 0
            return move_to(player = '1P',pred = 100)
       

    def ml_loop_for_2P(blocker_dir):  # as same as 1P
        if scene_info["ball_speed"][1] > 0 : 
            return move_to(player = '2P',pred = 100)
        else : 
            x = ( scene_info["platform_2P"][1]+30-scene_info["ball"][1] ) // scene_info["ball_speed"][1] 
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x) 
            bound = pred // 200 
            rand = random.random()
            if (bound > 0):
                if (bound%2 == 0):
                    pred = pred - bound*200 
                else :
                    pred = 200 - (pred - 200*bound)
            elif (bound < 0) :
                if bound%2 ==1:
                    pred = abs(pred - (bound+1) *200)
                else :
                    pred = pred + (abs(bound)*200)
            if (x <= 1) :
                if (pred >= scene_info["platform_2P"][0]+25) :
                    return 1
                elif (pred <= scene_info["platform_2P"][0]+15) :
                    return 2
                else:
                    if (rand < 0.33):
                        return 1
                    elif (rand>=0.33 and rand<0.66):
                        return 2
                    else:
                        return 0
            else:
                return move_to(player = '2P',pred = pred)
        

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        blocker_dir = scene_info["blocker"][0] - blocker_pre
        blocker_pre = scene_info["blocker"][0]

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game({"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})#以dict形式傳入，內有兩個參數
            ball_served = True
        else:
            #if(scene_info["ball"][0]<=scene_info["blocker"][0]+30 and scene_info["ball"][0]>=scene_info["blocker"][0] and scene_info["ball"][1]>=scene_info["blocker"][1] and scene_info["ball"][1]<=scene_info["blocker"][1]+20):
                #print("ball pos:",scene_info["ball"][0], scene_info["ball"][1])


            if side == "1P":
                command = ml_loop_for_1P(blocker_dir)
            else:
                command = ml_loop_for_2P(blocker_dir)

            if command == 0:
                comm.send_to_game({"frame": scene_info["frame"], "command": "NONE"})
            elif command == 1:
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            else :
                comm.send_to_game({"frame": scene_info["frame"], "command": "MOVE_LEFT"}) 