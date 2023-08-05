#!/usr/bin/env python
#-*- coding:utf-8 -*-


###############################################################
# CLAM: Computational Linguistics Application Mediator
# -- Settings --
#       by Maarten van Gompel (proycon)
#       http://ilk.uvt.nl/~mvgompel
#       Induction for Linguistic Knowledge Research Group
#       Universiteit van Tilburg
#       
#       Licensed under GPLv3
#
###############################################################

from clam.common.parameters import *
from clam.common.formats import *
from clam.common.viewers import *
from clam.common.digestauth import pwhash
from sys import path
from os import uname

REQUIRE_VERSION = 0.2

SYSTEM_ID = "frog"
SYSTEM_NAME = "Frog"
SYSTEM_DESCRIPTION = "Frog is a suite containing a tokeniser, PoS-tagger, lemmatiser, morphological analyser, and dependency parser for Dutch, developed at Tilbug University. It will be the successor of Tadpole but is still under heavy development. "

#Root directory for CLAM
host = uname()[1]
if host == 'aurora': #proycon's laptop
    CLAMDIR = "/home/proycon/work/clam"
    ROOT = "/home/proycon/work/frog.clam/"
    PORT = 8000
    URLPREFIX = 'frog'
else:
    raise Exception("Help! I don't know where I'm running from! Configure me!")


#Users and passwords
USERS = None #Enable this instead if you want no authentication
#USERS = { 'username': pwhash('username', SYSTEM_ID, 'secret') } #Using pwhash and plaintext password in code is not secure!! 


#List of supported Input formats by the system
INPUTFORMATS = [ PlainTextFormat('utf-8',['txt']) ]

#List of delivered Output formats by the system
OUTPUTFORMATS = [ TadpoleFormat('utf-8',['frogged'], viewer=FrogViewer() ) ]

#The system command (Use the variables $STATUSFILE $DATAFILE $PARAMETERS $INPUTDIRECTORY $OUTPUTDIRECTORY $USERNAME)
COMMAND = CLAMDIR +  "/wrappers/frogwrapper.sh $STATUSFILE $INPUTDIRECTORY $OUTPUTDIRECTORY $PARAMETERS"

PARAMETERS =  [ 
    ('Components', [       
        BooleanParameter('tok','--tok', 'Tokenise only','Use Frog as a standalone tokeniser, performs only tokenisation and no other taggings', forbid=['vtok']),
        BooleanParameter('vtok','--vtok', 'Tokenise only (verbosely)', 'Like the previous option, but explicitly show types assigned to the tokens.', forbid=['tok']),
        BooleanParameter('legtok','-l', 'Use legacy tokeniser', 'Use legacy TPtokenizer instead of the new one', forbid=['vtok']),
        BooleanParameter('noparser','--skip=p', 'Disable dependency parser', 'Disables the dependency parser, strongly recommended for faster results and lower memory consumption.')

    ])
]
