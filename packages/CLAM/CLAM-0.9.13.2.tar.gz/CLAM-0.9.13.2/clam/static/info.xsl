<?xml version="1.0" encoding="utf-8" ?>

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xlink="http://www.w3.org/1999/xlink">

<xsl:output method="html" encoding="UTF-8" omit-xml-declaration="yes" doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN" doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd" indent="yes" cdata-section-elements="script"/>

<xsl:template match="/clam">
  <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
  <xsl:call-template name="head" />
  <body>
    <div id="container">
    	<div id="header"><h1><xsl:value-of select="@name"/></h1></div>
    	
    	<div class="box">
    	 <h3>Introduction</h3>
    	 <p>
           This is the info page for the <em><xsl:value-of select="@name"/></em> webservice, a <a href="https://proycon.github.io/clam/">CLAM</a>-based webservice. This page contains some technical information useful for users wanting to interface with this webservice. The  <em><xsl:value-of select="@name"/></em> webservice is a <a href="http://en.wikipedia.org/wiki/REST">RESTful</a> webservice, which implies that usage of the four HTTP verbs (<tt>GET, POST, PUT, DELETE</tt>) on pre-defined URLs is how you can communicate with it. In turn, the response will be a standard HTTP response code along with content in CLAM XML, CLAM Upload XML, or CLAM Metadata XML format where applicable. It is recommended to read the <a href="https://proycon.github.io/clam/">CLAM manual</a> to get deeper insight into the operation of CLAM webservices.
    	 </p>
		</div>

		<div id="description" class="box">
		 <h3>Description of <xsl:value-of select="@name"/></h3>		        
         <xsl:value-of select="description" />
        </div>       
        
        <div id="restspec" class="box">
    	 <h3>RESTful Specification</h3>
    	 
         <p>A full generic RESTful specification for CLAM can be found in Appendix A of the <a href="https://proycon.github.io/clam">CLAM manual</a>. The procedure specific to <em><xsl:value-of select="@name"/></em> is described below. Clients interfacing with this webservice should follow this procedure:    	
    	 </p>

         <xsl:if test="count(/clam/profiles/profile) > 0">

         <h4>Project Paradigm</h4>
    	  
    	 <ol>
    		<li><strong>Create a <em>project</em></strong> - Issue a <tt>HTTP PUT</tt> on <tt><xsl:value-of select="@baseurl"/>/<em>{yourprojectname}</em></tt>
				<ul>
					<li>Will respond with <tt>HTTP 201 Created</tt> if successful.</li>
					<li>Will respond with <tt>HTTP 401 Unauthorized</tt> if incorrect or no user credentials were passed. User credentials have to be passed using HTTP Digest Authentication</li>
					<li>Will respond with <tt>HTTP 403 Permission Denied</tt> if you specified if an error arises, most often due to an invalid Project ID; certain characters including spaces, slashes and ampersands, are not allowed.</li>
				</ul> 
    		</li>    	    		
    		<li><strong>Upload one or more files</strong> - Issue a <tt>HTTP POST</tt> on <tt><xsl:value-of select="@baseurl"/>/<em>{yourprojectname}</em>/input/<em>{filename}</em></tt>. The POST request takes the following parameters:
    			<ul>
    				<li><tt>inputtemplate</tt> - The input template for this upload, determines the type of file that is expected. The <em><xsl:value-of select="@name"/></em> webservice defines the following Input Templates:
						<ul>
							<xsl:for-each select="//InputTemplate">
								<li><tt>inputtemplate=<xsl:value-of select="@id" /></tt> - <xsl:value-of select="@label" /> (<xsl:value-of select="@format" />). If you use this input template you can specify the following extra parameters:
								<ul> 
								<xsl:apply-templates />
								</ul>
								</li>
							</xsl:for-each>
						</ul>
    				</li>
    				<li><tt>file</tt> - HTTP file data.</li>
    				<li><tt>contents</tt> - full string contents of the file (can be used as an alternative to of file)</li>
    				<li><tt>url</tt> - URL to the input file, will be grabbed from the web (alternative to file)</li>
    				<li><tt>metafile</tt> - HTTP file data of a file in CLAM Metadata XML format, specifying metadata for this file (for advanced use)</li>
    				<li><tt>metadata</tt> - As above, but string contents instead of HTTP file (for advanced use)</li>     				
    			</ul>
    			<br /><em>Responses</em>:
    			<ul>
					<li>Will respond with <tt>HTTP 200 OK</tt> if successful, and returns CLAM Upload XML with details on the uploaded files (they may have been renamed automatically)</li>
					<li>Will respond with <tt>HTTP 401 Unauthorized</tt> if incorrect or no user credentials were passed. User credentials have to be passed using HTTP Digest Authentication</li>
					<li>Will respond with <tt>HTTP 403 Permission Denied</tt> if the upload is not valid, the file may not be of the correct type, have an invalid name, or there may be problems with specified parameters for the file. Returns CLAM Upload XML with the specific details</li>
					<li>Will respond with <tt>HTTP 404 Not Found</tt> if the project does not exist</li>
    			</ul>
    		</li>
    		
    		<li><strong>Start project execution with specified parameters</strong> - Issue a <tt>HTTP POST</tt> on <tt><xsl:value-of select="@baseurl"/>/<em>{yourprojectname}</em>/</tt>. The POST request takes the following parameters:
    			<ul>
					<xsl:apply-templates />
				</ul>
				<br /><em>Responses:</em>
				<ul>
					<li>Will respond with <tt>HTTP 202 Accepted</tt> if successful, and returns the CLAM XML for the project's current state.</li>
					<li>Will respond with <tt>HTTP 401 Unauthorized</tt> if incorrect or no user credentials were passed. User credentials have to be passed using HTTP Digest Authentication</li>
					<li>Will respond with <tt>HTTP 403 Permission Denied</tt> if the system does not have sufficient files uploaded to run, or if there are parameter errors. Will return CLAM XML with the project's current state, including parameter errors. In the CLAM XML response, <tt>/CLAM/status/@errors</tt> (XPath) will be <em>yes</em> if errors occurred, <em>no</em> otherwise.</li>
					<li>Will respond with <tt>HTTP 404 Not Found</tt> if the project does not exist</li>
				</ul>
			</li>    
			<li><strong>Poll the project status with a regular interval and check its status until it is flagged as finished</strong> - Issue (with a regular interval) a <tt>HTTP GET</tt> on <tt><xsl:value-of select="@baseurl"/>/<em>{yourprojectname}</em>/</tt> .
			<ul>
			<li>Will respond with <tt>HTTP 200 OK</tt> if successful, and returns the CLAM XML for the project's current state. The state of the project is stored in the CLAM XML response, in <tt>/CLAM/status/@code/</tt> (XPath), this code takes on one of three values:
			<ul>
				<li>0 - The project is in an accepting state, accepting file uploads and waiting to be started</li>
				<li>1 - The project is in execution</li>
				<li>2 - The project has finished</li>
			</ul> 
			</li>
			<li>Will respond with <tt>HTTP 401 Unauthorized</tt> if incorrect or no user credentials were passed. User credentials have to be passed using HTTP Digest Authentication</li>
			<li>Will respond with <tt>HTTP 404 Not Found</tt> if the project does not exist</li>
			</ul>    
			</li>
			<li><strong>Retrieve the desired output file(s)</strong> - Issue a <tt>HTTP GET</tt> on <tt><xsl:value-of select="@baseurl"/>/<em>{yourprojectname}</em>/output/<em>{outputfilename}</em></tt>.  A list of available output files can be obtained by querying the project's state (HTTP GET on <tt><xsl:value-of select="@baseurl"/>/<em>{yourprojectname}</em>/</tt>) and iterating over <tt>/CLAM/output/file/name</tt> (XPath). A <tt>template</tt> attribute will be available on these nodes indicating what output template was responsible for generating this file. The following output templates are defined for this webservice:
				<ul>
					<xsl:for-each select="//OutputTemplate">
						<li><tt><xsl:value-of select="@id" /></tt> - <xsl:value-of select="@label" /> (<xsl:value-of select="@format" />). </li>
					</xsl:for-each>
				</ul>			
				<br /><em>Responses:</em>			
				<ul>
					<li>Will respond with <tt>HTTP 200 OK</tt> if successful, and returns the content of the file (along with the correct mime-type for it)</li>
					<li>Will respond with <tt>HTTP 401 Unauthorized</tt> if incorrect or no user credentials were passed. User credentials have to be passed using HTTP Digest Authentication</li>
					<li>Will respond with <tt>HTTP 404 Not Found</tt> if the file or project does not exist</li>
				</ul>
			</li>		
			<li><strong>Delete the project</strong> (otherwise it will remain on the server and take up space) - Issue a <tt>HTTP DELETE</tt> on <tt><xsl:value-of select="@baseurl"/>/<em>{yourprojectname}</em>/</tt>.
<br /><em>Responses:</em>
<ul>
    			<li>Will respond with <tt>HTTP 200 OK</tt> if successful, and returns CLAM Upload XML with details on the uploaded files (they may have been renamed automatically)</li>
    			<li>Will respond with <tt>HTTP 401 Unauthorized</tt> if incorrect or no user credentials were passed. User credentials have to be passed using HTTP Digest Authentication</li>
    			<li>Will respond with <tt>HTTP 403 Permission Denied</tt> if the upload is not valid, the file may not be of the correct type, have an invalid name, or there may be problems with specified parameters for the file. Returns CLAM Upload XML with the specific details</li>
    			<li>Will respond with <tt>HTTP 404 Not Found</tt> if the project does not exist</li>
    			</ul>
			</li>
    	 </ol>
         
        </xsl:if>
        <xsl:if test="count(/clam/actions/action) > 0">

        <h4>Actions</h4>

        <p>Actions are simple remote procedure calls that can be executed in real-time, they will return HTTP 200 on success with a response fitting the specified MIME type. On fatal server-side errors, they may return <tt>HTTP 500 Server Error</tt> with an error message. Other HTTP errors may be returned, but this is customly defined by underlying function, rather than CLAM itself.</p>

        <ul>
        <xsl:for-each select="/clam/actions/action">
          <li><strong><xsl:value-of select="@name" /></strong> -- <tt><xsl:value-of select="/clam/@baseurl" />/actions/<xsl:value-of select="@id" />/</tt><br />
              <em><xsl:value-of select="@description" /></em><br />
              <xsl:choose>
              <xsl:when test="@method"> 
                Method: <tt><xsl:value-of select="@method" /></tt><br />
              </xsl:when>
              <xsl:otherwise>
                Methods: <tt>GET</tt>, <tt>POST</tt><br />
              </xsl:otherwise>
              </xsl:choose>
              <xsl:if test="@allowanonymous = 'yes'">
                (<em>Anonymous access allowed</em>)<br />
              </xsl:if>
              Returns: <tt><xsl:value-of select="@mimetype" /></tt><br />Parameters:<br />
              <ol>
              <xsl:apply-templates />
              </ol>
          </li>
        </xsl:for-each>
        </ul>


        </xsl:if>
    	  
    	</div>
    	
    	
    	<div class="box">
    	 <h3>CLAM Client API for Python</h3>
    	 <p>
    	 Using the CLAM Client API for Python greatly facilitates the writing of clients for this webservice, as the API will allow for more higher-level programming, taking care of all the necessary basics of RESTful communication. The following is a <em>skeleton</em> Python script you can use as a <em>template</em> for your client to communicate with this webservice.
    	 </p>
    	 
<pre class="pythoncode">
<em>#!/usr/bin/env python</em>
<strong>import</strong> clam.common.client
<strong>import</strong> clam.common.data
<strong>import</strong> clam.common.status
<strong>import</strong> random
<strong>import</strong> sys
<strong>import</strong> time

<em>#create client, connect to server.</em>
<em>#the latter two arguments are required for authenticated webservices, they can be omitted otherwise</em>
clamclient = clam.common.client.CLAMClient("<xsl:value-of select="@baseurl"/>", username, password)



<xsl:if test="count(/clam/profiles/profile) > 0">

<em>#Set a project name (it is recommended to include a sufficiently random naming component here, to allow for concurrent uses of the same client)</em>
project = "projectname" + str(random.getrandbits(64))

<em>#Now we call the webservice and create the project (in this and subsequent methods of clamclient, exceptions will be raised on errors).</em>
clamclient.create(project)

<em>#Get project status and specification</em>
data = clamclient.get(project)


<em>#Add one or more input files according to a specific input template. The following input templates are defined,</em>
<em>each may allow for extra parameters to be specified, this is done in the form of Python keyword arguments to the <tt>addinputfile()</tt> method, (parameterid=value)</em>
<xsl:for-each select="//InputTemplate">
<em>#inputtemplate="<xsl:value-of select="@id" />" #<xsl:value-of select="@label" /> (<xsl:value-of select="@format" />)</em>
<em>#	The following parameters may be specified for this input template:</em>
<xsl:for-each select="./*">
<em>#		<xsl:value-of select="@id" />=...  #(<xsl:value-of select="name()" />) -   <xsl:value-of select="@name" /> -  <xsl:value-of select="@description" /></em>
<xsl:if test="@required = 'true'">
	<em>#		this parameter is REQUIRED! </em>	
</xsl:if>
<xsl:if test="name() = 'ChoiceParameter'">
	<em>#		valid choices for this parameter: </em>
	<xsl:for-each select="choice">
		<em>#			<xsl:value-of select="@id" /> - <xsl:value-of select="." /></em> 
	</xsl:for-each>	
</xsl:if>
<xsl:if test="@multi = 'true'">
	<em>#		Multiple choices may be combined for this parameter as a comma separated list </em>	
</xsl:if>
</xsl:for-each>
</xsl:for-each>
clamclient.addinputfile(project, data.inputtemplate(inputtemplate), localfilename)


<em>#Start project execution with custom parameters. Parameters are specified as Python keyword arguments to the <tt>start()</tt> method <tt>(parameterid=value)</tt></em>
<xsl:for-each select="//parameters/parametergroup/*">
<em>#<xsl:value-of select="@id" />=...  #(<xsl:value-of select="name()" />) -   <xsl:value-of select="@name" /> -  <xsl:value-of select="@description" /></em>
<xsl:if test="@required = 'true'">
	<em>#	this parameter is REQUIRED! </em>	
</xsl:if>
<xsl:if test="name() = 'ChoiceParameter'">
	<em>#	valid choices for this parameter: </em>
	<xsl:for-each select="choice">
		<em>#	<xsl:value-of select="@id" /> - <xsl:value-of select="." /></em> 
	</xsl:for-each>	
</xsl:if>
<xsl:if test="@multi = 'true'">
	<em>#	Multiple choices may be combined for this parameter as a comma separated list </em>	
</xsl:if>
</xsl:for-each>
data = clamclient.start(project)


<em>#Always check for parameter errors! Don't just assume everything went well! Use startsafe() instead of start</em>
<em>#to simply raise exceptions on parameter errors.</em>
<strong>if</strong> data.errors:
    <strong>print</strong> >>sys.stderr,"An error occured: " + data.errormsg
    <strong>for</strong> parametergroup, paramlist in data.parameters:
        <strong>for</strong> parameter in paramlist:
            <strong>if</strong> parameter.error:
                <strong>print</strong> >>sys.stderr,"Error in parameter " + parameter.id + ": " + parameter.error
    clamclient.delete(project) #delete our project (remember, it was temporary, otherwise clients would leave a mess)
    sys.exit(1)

<em>#If everything went well, the system is now running, we simply wait until it is done and retrieve the status in the meantime</em>
<strong>while</strong> data.status != clam.common.status.DONE:
    time.sleep(5) #wait 5 seconds before polling status
    data = clamclient.get(project) #get status again
    <strong>print</strong> >>sys.stderr, "\tRunning: " + str(data.completion) + '% -- ' + data.statusmessage

<em>#Iterate over output files</em>
<strong>for</strong> outputfile <strong>in</strong> data.output:
    <strong>try</strong>:
        outputfile.loadmetadata() #metadata contains information on output template
    <strong>except</strong>:
        <strong>continue</strong>          
    
    outputtemplate = outputfile.metadata.provenance.outputtemplate_id
    <em>	#You can check this value against the following predefined output templates, and determine desired behaviour based on the output template:</em>
    <xsl:for-each select="//OutputTemplate">
	<em>	#if outputtemplate == "<xsl:value-of select="@id" />": #<xsl:value-of select="@label" /> (<xsl:value-of select="@format" />)</em>
	</xsl:for-each>
      
    <em>	#Download the remote file</em>
    outputfile.copy(localfilename)
    
    <em>	#..or iterate over its (textual) contents one line at a time:</em>
	<strong>	for</strong> line <strong>in</strong> outputfile.readlines():
		<strong>print</strong> line

<em>#delete the project (otherwise it would remain on server and clients would leave a mess)</em>
clamclient.delete(project)

</xsl:if>


<xsl:if test="count(/clam/actions/action) > 0">
<em>#A fictitious sample showing how to use the actions:</em>
result = clamclient.action('someaction', someparameter='blah',otherparameter=42, method='GET')
</xsl:if>

</pre>
    	</div>
    	
<div class="box">
    	<h3>CLAM XML</h3>
    	<p>To inspect the CLAM XML format, simply view the source of this current page, or any CLAM page. A formal schema definition in RelaxNG format will be available <a href="https://github.com/proycon/clam/blob/master/docs/clam.rng">here</a>. This documentation was automatically generated from the service description in CLAM XML format.</p>     	
</div>    	
            
        <xsl:call-template name="footer" />
               
        
        
    </div>
  </body>
  </html>
</xsl:template>




<xsl:template name="head">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title><xsl:value-of select="@name"/> :: <xsl:value-of select="@project"/></title>
    <link rel="stylesheet" href="{/clam/@baseurl}/static/base.css" type="text/css"></link>
    <link rel="stylesheet" href="{/clam/@baseurl}/style.css" type="text/css"></link>
  </head>
</xsl:template>

<xsl:template name="footer">
    <div id="footer" class="box">Powered by <strong>CLAM</strong> v<xsl:value-of select="/clam/@version" /> - Computational Linguistics Application Mediator<br />by Maarten van Gompel<br /><a href="http://clst.ru.nl">Centre for Language and Speech Technology</a>, <a href="http://www.ru.nl">Radboud University Nijmegen</a><br /><a href="http://ilk.uvt.nl">Induction of Linguistic Knowledge Research Group</a>, <a href="http://www.uvt.nl">Tilburg University</a>

<span class="extracredits">
<strong>CLAM</strong> is funded by <a href="http://www.clarin.nl/">CLARIN-NL</a> and started under the projects <strong><em>TICCLops</em></strong> <sub> (09-011)</sub>, coordinated by Martin Reynaert, and <strong>TTNWW</strong>, WP1 and WP2, respectively coordinated by Martin Reynaert and Antal van den Bosch.
</span>
</div>

</xsl:template>




<xsl:template match="StaticParameter|staticparameter">  <!-- lowercase variant is required because of some XSLT issues in Mozilla -->
	<li><tt><xsl:value-of select="@id" /></tt> - <strong><xsl:value-of select="@name" /></strong> (static parameter, fixed immutable value: <tt><xsl:value-of select="@value" /></tt>) - <xsl:value-of select="@description" />
	<xsl:if test="@required = 'yes'">
		<strong>Note: This is a required parameter!</strong>
	</xsl:if>
	</li>
</xsl:template>


<xsl:template match="BooleanParameter|booleanparameter">  <!-- lowercase variant is required because of some XSLT issues in Mozilla -->
	<li><tt><xsl:value-of select="@id" /></tt> - <strong><xsl:value-of select="@name" /></strong> (boolean parameter) -  <xsl:value-of select="@description" />
	<xsl:if test="@required = 'yes'">
		<strong>Note: This is a required parameter!</strong>
	</xsl:if>	
	</li>
</xsl:template>


<xsl:template match="StringParameter|stringparameter">  <!-- lowercase variant is required because of some XSLT issues in Mozilla -->
	<li><tt><xsl:value-of select="@id" /></tt> - <strong><xsl:value-of select="@name" /></strong> (string parameter) -  <xsl:value-of select="@description" />
	<xsl:if test="@required = 'yes'">
		<strong>Note: This is a required parameter!</strong>
	</xsl:if>	
	</li>
</xsl:template>




<xsl:template match="TextParameter|textparameter">  <!-- lowercase variant is required because of some XSLT issues in Mozilla -->
	<li><tt><xsl:value-of select="@id" /></tt> - <strong><xsl:value-of select="@name" /></strong> (text parameter) -  <xsl:value-of select="@description" />
	<xsl:if test="@required = 'yes'">
		<strong>Note: This is a required parameter!</strong>
	</xsl:if>	
	</li>
</xsl:template>


<xsl:template match="IntegerParameter|integerparameter">  <!-- lowercase variant is required because of some XSLT issues in Mozilla -->
	<li><tt><xsl:value-of select="@id" /></tt> - <strong><xsl:value-of select="@name" /></strong> (integer parameter) -  <xsl:value-of select="@description" />
	<xsl:if test="@required = 'yes'">
		<strong>Note: This is a required parameter!</strong>
	</xsl:if>		
	</li>
</xsl:template>

<xsl:template match="FloatParameter|floatparameter">  <!-- lowercase variant is required because of some XSLT issues in Mozilla -->
	<li><tt><xsl:value-of select="@id" /></tt> - <strong><xsl:value-of select="@name" /></strong> (float parameter) -  <xsl:value-of select="@description" />
	<xsl:if test="@required = 'yes'">
		<strong>Note: This is a required parameter!</strong>
	</xsl:if>		
	</li>
</xsl:template>


<xsl:template match="ChoiceParameter|choiceparameter">  <!-- lowercase variant is required because of some XSLT issues in Mozilla -->
	<li><tt><xsl:value-of select="@id" /></tt> - <strong><xsl:value-of select="@name" /></strong> (multiple-choice parameter) -  <xsl:value-of select="@description" />
	<xsl:if test="@required = 'true'">
		<strong>Note: This is a required parameter!</strong>
	</xsl:if>		
	<xsl:if test="@multi = 'true'">
		<strong>Note: Multiple values may be combined for this parameter as a comma separated list</strong>
	</xsl:if>
	<br />Available value choices:		
	<ul>
		<xsl:for-each select="choice">
			<li><em><xsl:value-of select="@id" /></em> - <xsl:value-of select="." /></li>
		</xsl:for-each>
	</ul>	
	</li>
</xsl:template>

<xsl:template match="converter|viewer|project|meta|inputsource">
</xsl:template>

</xsl:stylesheet>
