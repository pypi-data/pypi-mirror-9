## Script (Python) "initializeJsBuffer"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=
##


class jsBuffer:

    jsBuffer = [ ]
    jsDirectBuffer = [ ]


    def addJS( self, code_js ):
        #self.jsBuffer.append( code_js )
        self.jsBuffer.append( "%s;" % code_js )

    def addJSDirect( self, code_js ):
        #self.jsDirectBuffer.append( code_js )
        self.jsDirectBuffer.append( "%s;" % code_js )

    def addFile( self, name_file ):
        fichier = getattr( context, "%s.min.js" % name_file )
        self.jsBuffer.append( str( fichier ) )

    def addFileDirect( self, name_file ):
        fichier = getattr( context, "%s.min.js" % name_file )
        self.jsDirectBuffer.append( str( fichier ) )

    def getFile( self, name_file ):
        return str( getattr( context, "%s.min.js" % name_file ) )

    def getBuffer( self ):
        if self.jsBuffer:
            js = [ "\n/*<![CDATA[*/" ]
            js.append( "$( document ).ready( function ( ) {" )
            js.append( "\n".join( self.jsBuffer ) )
            js.append( "} );" )
            js.append( "/*]]>*/\n\t\t" )
            return "\n".join( js )
        else:
            return None

    def getDirectBuffer( self ):
        if self.jsDirectBuffer:
            js = [ "\n".join( self.jsDirectBuffer ) ]
            self.jsDirectBuffer = [ ]
            js.append( "\n\t\t" )
            return "\n".join( js )
        else:
            return None


return jsBuffer( )
