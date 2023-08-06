#!/usr/bin/python
# -*- coding: utf-8 -*-
## 
## (C) 2007, 2008, 2013-2015 Muthiah Annamalai,
## Licensed under GPL Version 3
## 
## Interpreter for Ezhil language

import os, sys, string, tempfile
from Interpreter import Interpreter, REPL, Lex, get_prog_name, PYTHON3
from ezhil_parser import EzhilParser
from ezhil_scanner import EzhilLex
from errors import RuntimeException, ParseException, TimeoutException
from multiprocessing import Process, current_process
from time import sleep,clock,time
import codecs, traceback

import codecs, sys
if not PYTHON3:
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout)
#sys.stdin = codecs.getreader('utf-8')(sys.stdin)

class EzhilInterpreter( Interpreter ):
    def __init__(self, lexer, debug = False ):
        """ create a Ezhil Interpeter and initialize runtime builtins etc.. in a RAII fashion,
            and associates a Ezhil parser object with this class
        """
        Interpreter.__init__(self,lexer,debug)
        Interpreter.change_parser(self,EzhilParser.factory)
        return
    
    def install_builtins(self):
        """ populate with the builtin functions, while adding our own flavors"""
        Interpreter.install_builtins(self)
        
        #input statements, length constructs
        tamil_equiv = {u"சரம்_இடமாற்று":u"replace", u"சரம்_கண்டுபிடி":u"find",u"நீளம்":u"len",
                       u"சரம்_உள்ளீடு":u"raw_input", u"உள்ளீடு" : u"input" }

        # printf - as per survey request
        tamil_equiv.update( { u"அச்சிடு":u"printf" } )        
        
        #list operators
        tamil_equiv.update( {u"பட்டியல்":u"list",u"பின்இணை":u"append",u"தலைகீழ்":u"reverse",
                             u"வரிசைப்படுத்து":u"sort",u"நீட்டிக்க":u"extend",u"நுழைக்க":u"insert",u"குறியீட்டெண்":u"index",
                             u"வெளியேஎடு":u"pop_list",u"பொருந்தியஎண்":u"count"} )
        
        #generic get/set ops for list/dict
        tamil_equiv.update( { u"எடு":u"__getitem__", u"வை":u"__setitem__",u"சாவிகள்":u"keys"} )
        
        #file operators
        tamil_equiv.update({u"கோப்பை_திற":u"file_open", u"கோப்பை_மூடு":u"file_close",u"கோப்பை_படி":u"file_read",
                            u"கோப்பை_எழுது":u"file_write",u"கோப்பை_எழுது_வரிகள்":u"file_writelines",u"கோப்பை_படி_வரிகள்":u"file_readlines"})
        
        #type
        tamil_equiv.update({u"வகை":u"type"})
        
        for k,v in list(tamil_equiv.items()):
            self.builtin_map[k]=self.builtin_map[v];
        
        try:
            import EZTurtle
        except ImportError as ie:
            if ( self.debug ):
                print(u"ImportError => turtle ",unicode(ie))
            return
        
        # translations for turtle module
        turtle_map = { u"முன்னாடி":u"forward", u"பின்னாடி" :u"backward",
                       u"வலது":u"lt", u"இடது":u"rt",
                       u"எழுதுகோல்மேலே":u"penup",  u"எழுதுகோல்கிழே":u"pendown"}
        for k,v in list(turtle_map.items()):
            vv = u"turtle_"+v;
            self.builtin_map[k] = self.builtin_map[vv]
        
        return

class EzhilRedirectOutput:
    """ class provides the get_output method for reading from a temporary file, and deletes it after that.
        the file creation is also managed here. However restoring stdout, stderr have to be done in the user class
    """
    @staticmethod
    def pidFileName( pid ):
        """ file name with $PID decoration as IPC alt """
        name = "ezhil_"+str(pid)+".out";
        if sys.platform.find('win') >= 0:
            # Windows OS
            name = tempfile.gettempdir()+name
        else:
            # LINUX or like systems
            name = "/tmp/"+name
        return name
    
    def dbg_msg(self,message):
        """ useful routine to debug timeout issues from spawned off process"""
        if ( self.debug ):
            self.actop.write(message)
        return
    
    def __init__(self,redirectop,debug=False):
        self.actop = sys.stdout
        self.op = None
        self.debug=debug
        self.redirectop = redirectop
        self.tmpf = None
        if ( self.redirectop ):
            self.tmpf=tempfile.NamedTemporaryFile(suffix='.output',delete=False)
            self.old_stdout = sys.stdout
            self.old_stderr = sys.stderr
            sys.stdout = self.tmpf
            sys.stderr = self.tmpf
        pass
    
    def __delete__(self):
        if self.redirectop:
            sys.stdout = self.old_stdout
            sys.stderr = self.old_stderr
        pass
	
    def get_output( self ):
        """ read the output from tmpfile once and delete it. Use cached copy for later. Memoized. """ 
        if ( not isinstance(self.op,str) ):
            self.op = ""
            if ( self.redirectop ):
                with open(self.tmpf.name) as fp:
                    self.op = fp.read()
                os.unlink( self.tmpf.name )
                self.tmpf = None
        
        return self.op

class EzhilRedirectInputOutput(EzhilRedirectOutput):
    def __init__(self,input_file,redirectop,debug=False):
        EzhilRedirectOutput.__init__(self,redirectop,debug)
        self.old_stdin = sys.stdin
        self.stdin = codecs.open( input_file , "r", "utf-8" )

class EzhilFileExecuter(EzhilRedirectOutput):
    """ run on construction - build a Ezhil lexer/parser/runtime and execute the file pointed to by @files;
        When constructed with a @TIMEOUT value, the process may terminate without and output, otherwise it dumps the output
        to a file named, 
    """
    def get_output(self):
        return [self.tmpf_name,self.fProcName,self.data]
    
    def __delete__(self):
        if self.tmpf and hasattr(self.tmpf,'name'):
            os.unlink( self.tmpf.name )
            self.tmpf = None
        if self.fProcName:
            os.unlink( self.fProcName )
            self.fProcName = None
        if hasattr(self.p,'terminate'):
            self.p.terminate()
        pass
    
    def __init__(self,file_input,debug=False,redirectop=False,TIMEOUT=None):
        EzhilRedirectOutput.__init__(self,redirectop,debug)
        self.dbg_msg(u"ezil file executer\n")
        self.fProcName = ""
        self.data = ""
        self.tmpf_name = ""		
        self.p = None
        self.TIMEOUT = TIMEOUT
        if ( not redirectop ): #run serially and exit.
            try:
                ezhil_file_parse_eval( file_input,self.redirectop,self.debug)
                self.exitcode = 0
            except Exception as e:
                self.exitcode = -1
                traceback.print_tb(sys.exc_info()[2])
                raise e
        else:
            self.dbg_msg("EzhilFileExecuter - entering the redirect mode\n")
            self.p = Process(target=ezhil_file_parse_eval,kwargs={'file_input':file_input,'redirectop':redirectop,'debug':debug})
        
    def run(self):
        if self.p :
            try:
                self.dbg_msg("begin redirect mode\n")
                self.p.start()
                if ( self.TIMEOUT is not None ):
                    start = time()
                    self.dbg_msg("timeout non-zero\n")
                    raise_timeout = False
                    while self.p.is_alive():
                        self.dbg_msg("in busy loop : %d , %d \n"%(time()-start,self.TIMEOUT))
                        self.dbg_msg("SLEEP\n")
                        sleep(5) #poll every 5 seconds
                        if ( (time() - start) > self.TIMEOUT ):
                            self.dbg_msg("Reached timeout = %d\n"%self.TIMEOUT)
                            raise_timeout = True
                            break
                        # now you try and read all the data from file, , and unlink it all up.
                    self.fProcName = EzhilRedirectOutput.pidFileName(self.p.pid);
                    self.tmpf_name = self.tmpf.name;
                    
                    # dump stuff from fProcName into the stdout
                    fp = open(self.fProcName,'r')
                    print(u"######### ------- dump output ------- ##############")
                    self.data = fp.read()
                    print(self.data)
                    fp.close()

                    if raise_timeout:
                        raise TimeoutException( self.TIMEOUT )
                    #os.unlink( fProcName)
            except Exception as e:
                print("exception ",unicode(e))
                traceback.print_tb(sys.exc_info()[2])
                raise e
            finally:
                # reset the buffers
                if ( self.redirectop ):
                    #self.tmpf.close()
                    sys.stdout = self.old_stdout
                    sys.stderr = self.old_stderr
                    sys.stdout.flush()
                    sys.stderr.flush()

                # cleanup the cruft files
                #if self.tmpf and hasattr(self.tmpf,'name'):
                #    os.unlink( self.tmpf.name )
                #self.tmpf = None
                #if self.fProcName:
                #    os.unlink( self.fProcName )
                #self.fProcName = None

                # nuke the process
                if hasattr(self.p,'terminate'):
                    self.p.terminate()
                self.exitcode  = self.p.exitcode
        else:
            pass #nothing to run

def ezhil_file_parse_eval( file_input,redirectop,debug):
    """ runs as a separate process with own memory space, pid etc, with @file_input, @debug values,
        the output is written out into a file named, "ezhil_$PID.out". Calling process is responsible to
        cleanup the cruft. Note file_input can be a string version of a program to be evaluated if it is
        enclosed properly in a list format
    """
    if ( redirectop ):
        sys.stdout = codecs.open(EzhilRedirectOutput.pidFileName(current_process().pid),"w","utf-8")
        sys.stderr = sys.stdout;
    lexer = EzhilLex(file_input,debug)
    if ( debug ): lexer.dump_tokens()
    parse_eval = EzhilInterpreter( lexer, debug )
    web_ast = parse_eval.parse()
    if( debug ):
        print(unicode(web_ast))
    if ( debug ):  print(u"*"*60);  print(unicode(parse_eval))
    exit_code = 0
    try:
        env = parse_eval.evaluate()
    except Exception as e:
        exit_code = -1
        print(unicode(e))
        if ( debug ):
            traceback.print_tb(sys.exc_info()[2])
            raise e
    finally:
        if ( redirectop ):
            # cerrar - முடி
            sys.stdout.flush()
            sys.stderr.flush()
            #sys.stdout.close()
    return exit_code

def ezhil_file_REPL( file_input, lang, lexer, parse_eval, debug=False):    
    #refactor out REPL for ezhil and exprs
    env = None ## get the first instance from evaluate_interactive
    do_quit = False
    ## world-famous REPL
    with open(file_input) as fp:
        lines = fp.readlines()
    #lines = "\n".join([line.strip() for line in lines])
    totbuffer = ""
    max_lines = len(lines)
    for line_no,Lbuffer in enumerate(lines):
        try:
            curr_line_no = "%s %d> "%(lang,line_no)
            Lbuffer = Lbuffer.strip()
            if ( Lbuffer == 'exit' ):
                do_quit = True
        except EOFError as e:
            print("End of Input reached\n")
            do_quit = True ##evaluate the Lbuffer
        if ( debug ):
            print("evaluating buffer", Lbuffer)
            if ( len(totbuffer) > 0 ):
                print("tot buffer %s"%totbuffer) #debugging aid
        if ( do_quit ):
            print(u"******* வணக்கம்! பின்னர் உங்களை  பார்க்கலாம். *******") 
            return
        try:
            lexer.set_line_col([line_no, 0])
            if len(totbuffer) == 0:
                totbuffer = Lbuffer
            else:
                totbuffer += "\n"+ Lbuffer
            lexer.tokenize(totbuffer)
            [lexer_line_no,c] = lexer.get_line_col( 0 )
            if ( debug ): lexer.dump_tokens()
            try:
                if ( debug ): print (u"parsing buffer item => ",totbuffer)
                parse_eval.parse()
            except Exception as pexp:
                ## clear tokens in lexer
                parse_eval.reset() #parse_eval
                if ( debug ): 
                    print (u"offending buffer item => ",totbuffer)
                    print(unicode(pexp),unicode(pexp.__class__))
                    traceback.print_tb(sys.exc_info()[2])
                    raise pexp
                # Greedy strategy to keep avoiding parse-errors by accumulating more of input.
                # this allows a line-by-line execution strategy. When all else fails we report.
                if ( (line_no + 1) ==  max_lines ):
                    raise pexp
                continue
            totbuffer = ""
            sys.stdout.write(curr_line_no)
            if ( debug ):  print(u"*"*60);  print(unicode(parse_eval))
            [rval, env] = parse_eval.evaluate_interactive(env)
            if hasattr( rval, 'evaluate' ):
                print(rval.__str__())
            elif hasattr(rval,'__str__'): #print everything except a None object
                print( str(rval) )
            else:
                print(u"\n")
        except Exception as e:
            print(e)
            raise e
    return

class EzhilInterpExecuter(EzhilRedirectInputOutput):
    """ run on construction - build a Ezhil lexer/parser/runtime and execute the file pointed to by @files """
    def __init__(self,file_input,debug=False,redirectop=False):
        EzhilRedirectInputOutput.__init__(self,file_input,redirectop)
        
        try:
            lang = u"எழில்"
            lexer = EzhilLex(debug)
            if ( debug ): print( unicode(lexer) )
            parse_eval = EzhilInterpreter( lexer, debug )
            ezhil_file_REPL( file_input, lang, lexer, parse_eval, debug )
        except Exception as e:
            print(u"exception ",unicode(e))
            traceback.print_tb(sys.exc_info()[2])
            raise e
        finally:
            if ( redirectop ):
                #self.tmpf.close()
                sys.stdout = self.old_stdout
                sys.stderr = self.old_stderr
                sys.stdin = self.old_stdin

    @staticmethod
    def runforever():
        EzhilInterpExecuter(sys.stdin)
        return

def ezhil_interactive_interpreter(lang = u"எழில்",debug=False):
    ## interactive interpreter
    lexer = EzhilLex(debug)
    parse_eval = EzhilInterpreter( lexer, debug )
    REPL( lang, lexer, parse_eval, debug )

if __name__ == u"__main__":
    lang = u"எழில்"
    [fnames, debug, dostdin ]= get_prog_name(lang)
    if ( dostdin ):
        ezhil_interactive_interpreter(lang,debug)
    else:
        ## evaluate a files sequentially except when exit() was called in one of them,
        ## while exceptions trapped per file without stopping the flow
        exitcode = 0
        for idx,aFile in enumerate(fnames):
            if ( debug):  print(u" **** Executing file #  ",1+idx,u"named ",aFile)
            try:
                EzhilFileExecuter( aFile, debug ).run()
            except Exception as e:
                print(u"executing file, "+aFile.decode("utf-8")+u" with exception "+unicode(e))
                if ( debug ):
                    #traceback.print_tb(sys.exc_info()[2])
                    raise e
                exitcode = -1
        sys.exit(exitcode)
    pass
