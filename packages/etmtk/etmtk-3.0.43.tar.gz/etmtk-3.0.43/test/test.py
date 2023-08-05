#Copyright (c) 2009, Julian Aloofi
#All rights reserved.

#Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

#    * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import Tkinter
from PIL import Image, ImageTk
import tkSnack

##initializing some stuff
#new Tk window
root = Tkinter.Tk()
#initialize sound
tkSnack.initializeSnack(root)
#create and open sound file
crapalert = tkSnack.Sound(load='../Resources/crapalert.wav')
#open the image, Tkinter just can read gifs, so we need PIL
crapimg = Image.open('../Resources/crapalert.png')
crapbuttimg = ImageTk.PhotoImage(crapimg)
#creating the window
mainframe = Tkinter.Frame(root)
mainframe.pack(side=Tkinter.TOP, fill = Tkinter.X)

#let's create a button handler
def crapAlert():
	"""
	Results in a crap-alert sound and a notification
	"""
	#play the sound
	crapalert.play()

#create the button and connect to the handler
crapbutton = Tkinter.Button(mainframe, compound = Tkinter.TOP, width=400, height=400, image=crapbuttimg, command=crapAlert)
crapbutton.pack(side=Tkinter.LEFT, padx=2, pady=2)

#let's go
root.mainloop()
