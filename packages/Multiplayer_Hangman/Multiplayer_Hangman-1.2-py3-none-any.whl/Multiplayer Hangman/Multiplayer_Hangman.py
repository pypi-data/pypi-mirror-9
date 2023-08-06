# -*- Coding: utf-8 -*-


#_Importing Modules_#
import Game_Data.Graphics as Graphics
import platform
import socket
import pickle
import time
import sys
import os
#_Importing Modules_#




#Global Variables#
running  = True
language = None
sock     = None
client   = None
ip       = ""
port     = 8397
kbps     = 0.03
clear    = None
pause    = None
#Global Variables#




#***************************************************Function Main***************************************************#
def main():
    global language, clear

    #----Creating the clear variable----#
    #Windows platform.
    if (platform.system() == "Windows"):
        clear = "cls"
        pass

    #Linux and MacOs platforms.
    else:
        clear = "clear"
        pass
    #----Creating the clear variable----#

    

    #----------Trying to load saved settings----------#
    try:
        file = open("Game_Data\\Saves\\settings.dat", "rb")
        settings = pickle.load(file)
        file.close()

        #-----Checking what language to use-----#
        if (settings[0] == "English"):
            import Game_Data.English as language #Choosing english.
            pass

        else:
            import Game_Data.Greek as language   #Choosing greek.
            pass
        #-----Checking what language to use-----#
        
    #----------Trying to load saved settings----------#

    #Failed to load settings.
    except:
        Language() #Go to the language menu.
        pass

    #Go to main menu.
    Menu()
    return 0
#***************************************************Function Main***************************************************#




#===================================================Function Menu===================================================#
def Menu():

    #-------------------Main Menu-------------------#
    while running:

        os.system(clear)#Cleaning the console.

        #-------------User Menu Info-------------#
        print("====="+language.filename+"=====")
        print("1) "+language.create_game)
        print("2) "+language.join_game)
        print("3) "+language.options)
        print("4) "+language.instructions)
        print("5) "+language.credits_)
        print("6) "+language.quit_)
        print("====="+language.filename+"=====\n")
        #-------------User Menu Info-------------#

        #Take user's input.
        choose = input(language.choose+": ")

        #Start new game.
        if (choose == "1"):
            createGame()
            continue

        #Join a game.
        elif (choose == "2"):
            joinGame()
            continue

        #Language Settings.
        elif (choose == "3"):
            Language()
            continue

        #Instructions.
        elif (choose == "4"):
            Info()
            continue

        #Credits.
        elif (choose == "5"):
            Credits()
            continue

        #Exit the program.
        elif (choose == "6"):
            sys.exit()
            break

        #Continue.
        else:
            continue
    #-------------------Main Menu-------------------#
#===================================================Function Menu===================================================#




#===================================================Function Info===================================================#
def Info():
    os.system(clear)#Cleaning the console.
    
    print("================="+language.instructions+"=================")
    print(language.info)
    print("================="+language.instructions+"=================\n\n")

    input(language.Continue)
    return
#===================================================Function Info===================================================#




#==================================================Function Credits=================================================#
def Credits():
    os.system(clear)#Cleaning the console.
    
    print("================="+language.credits_+"=================")
    print(language.credits_info)
    print("================="+language.credits_+"=================\n\n")

    input(language.Continue)
    return
#==================================================Function Credits=================================================#




#==================================================Function Language================================================#
def Language():
    global language

    while running:
        os.system(clear)#Cleaning the console.

        print("=================")
        print("== 1) English  ==")
        print("== 2) Ελληνικά ==")
        print("=================\n")

        choose = input("Language/Γλώσσα: ")

        #Choose English.
        if (choose == "1"):
            import Game_Data.English as language
            save_language = "English"
            break

        #Choose Greek.
        elif (choose == "2"):
            import Game_Data.Greek as language
            save_language = "Greek"
            break

        else:
            continue

    #Ask the user if he want's to save this settings.
    Ask = askYesNo("Do you want to save this settings/Να αποθηκευτούν αυτές οι ρυθμίσεις?")

    #Answered yes.
    if (Ask):
        saveSettings(variables = [save_language])
        pass
#==================================================Function Language================================================#




#==================================================Function askYesNo================================================#
def askYesNo(message):

    while running:
        os.system(clear)
        
        inp = input(message + "(y/n): ")

        #If yes return true.
        if (inp.lower() == "y"):
            return True

        #If no return false.
        elif (inp.lower() == "n"):
            return False

        else:
            continue
#==================================================Function askYesNo================================================#




#================================================Function saveSettings==============================================#
def saveSettings(variables = []):

    #Try to make a new directory(if it't not exist already).
    try:
        os.mkdir("Game_Data\\Saves")
        pass

    #Directory exist so skip this.
    except:
        pass

    #------------Saving the settings------------#
    file = open("Game_Data\\Saves\\settings.dat", "wb")
    pickle.dump(variables, file)
    file.close()
    #------------Saving the settings------------#
    return
#================================================Function saveSettings==============================================#




#=================================================Function createGame===============================================#
def createGame():
    global sock, client

    #Creating a socket object.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #Trying to bind the socket to the local machine.
    try:
        sock.bind((ip, port))#Binding.
        sock.listen(1)       #Listening to 1.
        os.system(clear)
        
        print(language.waitinForClient) #Printing a message.
        client, addr = sock.accept()    #Accepting a client.
        os.system(clear)
        
        print(language.clientAccepted) #Printing a message.
        input(language.Continue)
        pass


    #For a reason, failed to bind the socket to the local machine.
    except:
        os.system(clear)
        print(language.failedToCreateGame)
        input(language.Continue)
        return

    #This try-except is been used to catch connection error from the sock socket.
    try:
        startGameFromServer() #Starting the game.
        client.close() #Closing the connection.
        pass

    #Exception catched.
    except:
        os.system(clear)
        print(language.connectionError) #Printing an error message.
        input(language.Continue)
        
    return
#=================================================Function createGame===============================================#




#==================================================Function joinGame================================================#
def joinGame():
    global sock
    os.system(clear)

    #Creating a socket object.
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    IP = input("IP: ") #Getting the ip from the user.

    #Trying to connect to a server.
    try:
        os.system(clear)
        sock.connect((IP, port))  #Connecting.
        print(language.connected)
        input(language.Continue)
        pass

    #Failed to connect.
    except:
        os.system(clear)
        print(language.failedToConnect)
        input(language.Continue)
        return

    #This try-except is been used to catch connection error from the sock socket.
    try:
        strartGameFromClient()
        sock.close()
        pass

    #Exception catched.
    except:
        os.system(clear)
        print(language.connectionError) #Printing an error message.
        input(language.Continue)
        
    return
#==================================================Function joinGame================================================#




#=============================================Function startGameFromServer==========================================#
def startGameFromServer():
    os.system(clear)

    #___________________Variables___________________#
    hidden_word    = input(language.giveHiddenWord)
    listed_word    = list(hidden_word)
    guess_word     = []
    entered_letter = []
    life           = 8
    current_graph  = 0
    #___________________Variables___________________#

    #Filling the guess_word with under _ .
    for i in range(len(listed_word)):
        guess_word.append("_")
        pass

    #---Making vissible the first and the last letter in guess_word---#
    guess_word[0] = listed_word[0]
    guess_word[len(listed_word)-1] = listed_word[len(listed_word)-1]
    #---Making vissible the first and the last letter in guess_word---#


    #Sending to the client the hidden word.
    client.send( str.encode(hidden_word) )
    time.sleep(kbps)


    #--------------------------Game Mechanism--------------------------#
    while running:
        os.system(clear)

        #------------Information for the user------------#
        print("=========="+language.status+"==========")
        print(language.word+": "+hidden_word)
        print(language.entered+": "+str(entered_letter))
        print(language.life+": "+str(life))
        print(language.guess+": "+str(guess_word))
        print("=========="+language.status+"==========")
        #------------Information for the user------------#

        print("\n\n")
        print(Graphics.graphics[current_graph])

        #Getting the actions of the client.
        data = bytes.decode( client.recv(1024) )


        #If action is </Quickloose\>(This player is loosing because the client guessed the word at once).
        if (data == "</Quickloose\>"):
            os.system(clear)
            print(Graphics.graphics[current_graph])
            print("\n\n")

            print(language.guess+": "+str(guess_word)+"\n")
            print(language.Quickloose)
            input(language.Continue)
            return

        #If action is </LetterFound/>, update guess_word.
        elif (data == "</LetterFound/>"):

            #Taking the place in guess word from the client.
            i    = int( bytes.decode( client.recv(1024) ) )

            #Taking the character.
            char = bytes.decode( client.recv(1024) )

            #Updateing the guess_word.
            guess_word[i] = char
            pass


        #If action is </Entered/>, update the entered_letter and the life variables.
        elif (data == "</Entered/>"):

            #Taking the character.
            char = bytes.decode( client.recv(1024) )

            #Update the life variable.
            life = int( bytes.decode( client.recv(1024) ) )
            current_graph += 1

            #Update the entered_letter variable.
            entered_letter.append(char)
            pass


        #If action is </win/> then this player win the game.
        elif (data == "</win/>"):

            os.system(clear)
            print(Graphics.graphics[current_graph])
            print("\n\n")

            print(language.guess+": "+str(guess_word)+"\n")
            print(language.win)
            input(language.Continue)
            return

        #If action is </win/> then this player loosing the game because the client has found all the letters from the hidden word.
        elif (data == "</loose/>"):
            os.system(clear)
            print(Graphics.graphics[current_graph])
            print("\n\n")

            print(language.guess+": "+str(guess_word)+"\n")
            print(language.loose)
            input(language.Continue)
            return
    #--------------------------Game Mechanism--------------------------#
#=============================================Function startGameFromServer==========================================#
            

            

#=============================================Function strartGameFromClient=========================================#
def strartGameFromClient():
    os.system(clear)

    print(language.waitingPreparation)

    #___________________Variables___________________#
    hidden_word    = bytes.decode(sock.recv(1024)) #Taking the hidden word from the server.
    listed_word    = list(hidden_word)
    guess_word     = []
    entered_letter = []
    life           = 8
    current_graph  = 0
    #___________________Variables___________________#

    #Filling the guess_word with under _ .
    for i in range(len(listed_word)):
        guess_word.append("_")
        pass

    #---Making vissible the first and the last letter in guess_word---#
    guess_word[0] = listed_word[0]
    guess_word[len(listed_word)-1] = listed_word[len(listed_word)-1]
    #---Making vissible the first and the last letter in guess_word---#


    #--------------------------Game Mechanism--------------------------#
    while running:
        os.system(clear)

        #____Variables____#
        inListedWord = 0
        inGuessWord  = 0
        #____Variables____#


        #------------Information for the user------------#
        print("=========="+language.status+"==========")
        print(language.guess+": "+str(guess_word))
        print(language.entered+": "+str(entered_letter))
        print(language.life+": "+str(life))
        print("=========="+language.status+"==========\n")
        #------------Information for the user------------#

        print("\n")
        print(Graphics.graphics[current_graph])
        print("\n\n")

        #Taking input from the user.
        take = input(language.takeInput+": ")


        if take == "":
            continue

        #The player found the word at once.
        if (take == hidden_word):
            os.system(clear)
            print(Graphics.graphics[current_graph])
            print("\n\n")

            #Printing some info to the user.
            print(language.word+": "+str(hidden_word)+"\n")
            print(language.win)
            
            sock.send( str.encode("</Quickloose\>") ) #Sending the action to the server.
            time.sleep(kbps)
            
            input(language.Continue)
            return

        #Searching if the user already typed this letter#
        for i in range( len(listed_word) ):

            #If this letter exist in the current place of the listed_word.
            if (take == listed_word[i]):
                inListedWord += 1
                pass

            #If this letter exist in the current place of the guess_word.
            if (take == guess_word[i]):
                inGuessWord += 1
                pass
        #Searching if the user already typed this letter#


        #If inListedWord == inGuessWord it means that this letter(take) has been already typed.
        if ( (inListedWord == inGuessWord) and (inListedWord != 0 and inGuessWord != 0) ):
            print("\n\n"+language.alreadyFound)
            input(language.Continue)
            continue


        #Searching to see if this letter is in the hidden word.
        for i in range( len(listed_word) ):

            #The letter exist in the hidden word.
            if (take == listed_word[i]):
                guess_word[i] = take #Update the guess_word.

                #Sending the action </LetterFound/> to the server.
                sock.send( str.encode("</LetterFound/>") )
                time.sleep(kbps)

                #Sending the place of the letter.
                sock.send( str.encode(str(i)) )
                time.sleep(kbps)

                #Sending the character(take).
                sock.send( str.encode(take) )
                time.sleep(kbps)
                pass
            pass


        #The player failed to find a letter.
        if ( (take not in entered_letter) and  (take not in listed_word) ):
            
            entered_letter.append(take) #Update the entered_letter.
            life -= 1 #Lossing life.
            current_graph += 1

            #Sending the action </Entered/> in the server.
            sock.send( str.encode("</Entered/>") )
            time.sleep(kbps)

            #Sending the character take.
            sock.send( str.encode(take) )
            time.sleep(kbps)

            #Sending the updated life variable.
            sock.send( str.encode(str(life)) )
            time.sleep(kbps)
            pass


        #End of life(This player is loosing.).
        if (life <= 0):
            os.system(clear)
            print(Graphics.graphics[current_graph])
            print("\n\n")

            #Printing some info for the player.
            print(language.word+": "+str(hidden_word)+"\n")
            print(language.loose)

            #Sending the action </win/> to the server.
            sock.send( str.encode("</win/>") )
            time.sleep(kbps)
            
            input(language.Continue)
            return

        #This player wins because he found all the letters one by one.
        if (guess_word == listed_word):
            os.system(clear)
            print(Graphics.graphics[current_graph])
            print("\n\n")

            #Printing some info for the player.
            print(language.word+": "+str(hidden_word)+"\n")
            print(language.win)

            #Sending the action </loose/> to the server.
            sock.send( str.encode("</loose/>") )
            time.sleep(kbps)
            
            input(language.Continue)
            return
    #--------------------------Game Mechanism--------------------------#
    
#=============================================Function strartGameFromClient=========================================#


#Starting the program.
if(__name__ == "__main__"):
    main()
