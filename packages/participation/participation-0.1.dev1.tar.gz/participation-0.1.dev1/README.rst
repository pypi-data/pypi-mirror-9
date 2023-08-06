==================================================================
Social participation data analysis and exploitation
==================================================================

Routines for analysis and synthesis of RDF social participation data.
Idealized facilites include:

   - Observance of expected stability and overall measures of each instance.
   - Integration of data from a number of instances.
   - Integration of data from a usual social platforms (Facebook, Twitter, LinkedIn).
   - Recommendation of resources through topological and textual criteria, with explicit routines and potential uses.
   - Synthesis of audiovisual artifacts to ease observation, probing and exploitation.
   - Translation of participatory data to RDF.
   - HTTP utilities, such as bootstrapping participatory ontologies or an access to resource recommendation routines.

Public data, such as provided by the Gmane database or donated profiles from private networks (e.g. Facebook), or gathered by Twitter, can be incorporated as RDF in the Social Graph.

Usage example
=================

.. code:: python

    import participation as P

    # downloads Social Participation data from Participabr,
    # Cidade Democrática and AA from datahub.io
    P.download()

    # The triplification routines are available:
    # accesses Participa.br data on PostgreSQL and save RDF Xml and Turtle
    P.triplification.ParticipaTriplification("dbname","username")
    # accesses Participa.br data on PostgreSQL and save RDF Xml and Turtle
    P.triplification.AATriplification("dbname","username","dbname2","username2","ircLog.txt")
    # accesses Participa.br data on PostgreSQL and save RDF Xml and Turtle
    P.triplification.OCDTriplify("dbname","username")

    # print number of users in each RDF graph
    # print number of incidences of each
    # print vocabulary

    import social as S
    # To load GDF file:
    fg=S.GDFgraph("../data/RenatoFabbri06022014.gdf") # graph should be on fg.G
    # find posts by friends with similar names

    # To make an abstract animation with the overall network:
    song=S.FSong(fg.G,"fsong/",True,True,False,True)
    # Check mixedVideo.webm

    # Add information about users that are equivalent (through RDF).
    # make network with and without that information

    # Make recommendation based on a target resource
    # Make recommendation of percolatory method

    # Rise a flask instance, point an example meteor interface

    # more ***under construction***
    # Enjoy!
