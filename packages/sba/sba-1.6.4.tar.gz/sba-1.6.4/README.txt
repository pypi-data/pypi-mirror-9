===============================================================
Python wrapper for Lourakis' sparse bundle adjustment C library 
===============================================================

Enjoy! The most recent version can be obtained from bitbucket via::

    hg clone ssh://hg@bitbucket.org/devangel77b/python-sba

As prerequisites, you will also need to install the sba library as a shared object (libsba.so) (Makefile with shared object target included here) and the sba projections library (libsbaprojs.so)::

    http://www.ics.forth.gr/~lourakis/sba
    https://bitbucket.org/devangel77b/libsbaprojs

See HOWTO.txt for details. 

Typical usage
=============

The main way to use this is as follows::

    import sba

    cameras = sba.Cameras.fromTxt('cams.txt')
    points = sba.Points.fromTxt('pts.txt',cameras.ncameras)
    newcams, newpts, info = sba.SparseBundleAdjust(cameras,points)

If you wish to alter the default and autodetected options, you can
create an Options object and change it, and then pass it to sba::

    options = sba.Options.fromInputs(points,cameras)
    # can also update options.XXX to appropriate values
    newcams,newpts,info = sba.SparseBundleAdjust(cameras,points,options)

Hopefully this is cleaner than the original way to call it in C. 
    
Contributors
============

The original sba C library was written by Manolis Lourakis and is 
described in Lourakis, Manolis I A and Antonis A Argyros (2004), "The design 
and implementation of a generic sparse bundle adjustment software package 
based on the Levenberg-Marquardt algorithm", FOURTH_ICS TR-340.

If using this package in research work, we would appreciate you citing it: D Theriault, N Fuller, B Jackson, E Bluhm, D Evangelista, Z Wu, M Betke, and T Hedrick (2014). A protocol and calibration method for accurate multi-camera field videography. J exp Biol 217:1843-1848. The BibTeX entry is::

    @article{Theriault:2014,
      author = {Theriault, D and Fuller, N and Jackson, B and Bluhm, E and Evangelista, D and Wu, Z and Betke, M and Hedrick, T},
      title = {A protocol and calibration method for accurate multi-camera field videography},
      journal = {J exp Biol},
      doi={10.1242/jeb.100529},
      year = {2014},
      volume = {217},
      pages = {1843--1848}
    }


Thanks also to
==============

Manolis Lourakis and Antonis Argyros, Ty Hedrick, Evan Bluhm, my mom and the academy. Version 1.6.4 has bug fixes from Isaac Yeaton and Nick Gravish. 
