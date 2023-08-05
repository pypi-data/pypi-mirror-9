#    Copyright (C) 2015 mUniKeS
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

from random import shuffle
from unicodedata import lookup
from Tkinter import Tk, Button, PhotoImage, Label
import pygame 

letters = {lookup("tibetan letter ka"):("ka", "../sounds/kha.ogg"), 
          lookup("tibetan letter kha"):("k'a", "../sounds/kha.ogg"),
          lookup("tibetan letter ga"):("k_'a", "../sounds/kha.ogg"),
          lookup("tibetan letter nga"):("nga", "../sounds/kha.ogg")}
num_letters = 4

def shuffle_dictionary (dictionary):
    """
    Return random keys of dictionary
    """
    # Python 3 
    # keys =  list(dictionary.keys())
    # Python 2 
    keys = dictionary.keys()
    shuffle(keys)
    return keys
        
def generate_letters(list_letters, num_letters):
    """
    Return a right letter and a list of shuffle letters
    """
    right_letter = list_letters[0]
    letters = list_letters[0:num_letters]
    shuffle(letters)
    return right_letter, letters

def play_ogg(list_oggs):
    """
    Play a list of oggs
    """
    i=0
    SONG_END = pygame.USEREVENT + 1
    pygame.mixer.music.set_endevent(SONG_END)
    pygame.mixer.music.load(list_oggs[i])
    pygame.mixer.music.play()
  
    running = True
    while running:
        for event in pygame.event.get():
            if  i >= len(list_oggs) - 1:
                running = False
            elif event.type == SONG_END:
                pygame.mixer.music.load(list_oggs[i+1])
                pygame.mixer.music.play()
            i+=1     
 
def right_button(button):
    """
    Right answer, button right green and sound
    """
    button.config(background = "green")
    button.config(activebackground="green")
    pygame.mixer.music.load('../sounds/right.ogg')
    pygame.mixer.music.play()
    
def wrong_button(button):
    """
    Wrong answer, button right green and sound
    """
    button.config(background = "red")
    button.config(activebackground="red")
    pygame.mixer.music.load('../sounds/wrong.ogg')
    pygame.mixer.music.play()
    
# random the letters
keys = shuffle_dictionary(letters)
right_answer, answers = generate_letters(keys, num_letters)
# lista de sonidos
list_oggs = []
i= 0
for i in range(0, num_letters):
    list_oggs.append(letters[answers[i]][1])
    i+=1

pygame.init()
# Tkinter
ventana = Tk()
play = PhotoImage(file='../images/play.png')
ventana.geometry("185x260+100+80")
label = Label(ventana, text = right_answer, font=("", 80))
label.pack()
 
play_sound=Button(ventana,width=40,height=30,fg='black',
            image=play, command=lambda: play_ogg(list_oggs)).place(x=5,y=102)
option_1 = Button(ventana,width=7,height=3,fg='black', 
                  text=letters[answers[0]][0])
option_1.place(x=5,y=140)
option_2 = Button(ventana,width=7,height=3,fg='black', 
                  text=letters[answers[1]][0])
option_2.place(x=5,y=200) 
option_3 = Button(ventana,width=7,height=3,fg='black', 
                  text=letters[answers[2]][0])
option_3.place(x=95,y=140)
option_4 = Button(ventana,width=7,height=3,fg='black', 
                  text=letters[answers[3]][0])
option_4.place(x=95,y=200)
option_1.config(command=lambda: right_button(option_1) if answers[0] == right_answer else wrong_button(option_1) )
option_2.config(command=lambda: right_button(option_2) if answers[1] == right_answer else wrong_button(option_2))
option_3.config(command=lambda: right_button(option_3) if answers[2] == right_answer else wrong_button(option_3))
option_4.config(command=lambda: right_button(option_4) if answers[3] == right_answer else wrong_button(option_4))
 
ventana.mainloop()
pygame.quit()