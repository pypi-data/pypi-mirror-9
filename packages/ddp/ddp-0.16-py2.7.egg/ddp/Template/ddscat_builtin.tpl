' ========== Parameter file for v7.3 ===================' 
'**** Preliminaries ****'
'NOTORQ' = CMDTRQ*6 (DOTORQ, NOTORQ) -- either do or skip torque calculations
'PBCGS2' = CMDSOL*6 (PBCGS2, PBCGST, GPBICG, QMRCCG, PETRKP) -- CCG method
'GPFAFT' = CMETHD*6 (GPFAFT, FFTMKL) -- FFT method
'GKDLDR' = CALPHA*6 (GKDLDR, LATTDR, FLTRCD) -- DDA method
'NOTBIN' = CBINFLAG (NOTBIN, ORIBIN, ALLBIN) -- binary output?
'**** Initial Memory Allocation ****'
100 100 100 = dimensioning allowance for target generation
'**** Target Geometry and Composition ****'
'ELLIPSOID' = CSHAPE*9 shape directive
20 20 20 = shape parameters 1 - 3
1         = NCOMP = number of dielectric materials
'../../diel/Au_evap' = file with refractive index 1
'**** Additional Nearfield calculation? ****'
1 = NRFLD (=0 to skip nearfield calc., =1 to calculate nearfield E)
0.5 0.5 0.5 0.5 0.5 0.5 (fract. extens. of calc. vol. in -x,+x,-y,+y,-z,+z)
'**** Error Tolerance ****'
1.00e-5 = TOL = MAX ALLOWED (NORM OF |G>=AC|E>-ACA|X>)/(NORM OF AC|E>)
'**** Maximum number of iterations ****'
1000     = MXITER
'**** Integration limiter for PBC calculations ****'
1.00e-2 = GAMMA (1e-2 is normal, 3e-3 for greater accuracy)
'**** Angular resolution for calculation of <cos>, etc. ****'
0.5	= ETASCA (number of angles is proportional to [(3+x)/ETASCA]^2 )
'**** Wavelengths (micron) ****'
0.522 0.522 1 'LIN' = wavelengths (1st,last,howmany,how=LIN,INV,LOG,TAB)
'**** Refractive index of ambient medium ****'
1.3300 = NAMBIENT
'**** Effective Radii (micron) **** '
0.010 0.010 1 'LIN' = eff. radii (1st,last,howmany,how=LIN,INV,LOG,TAB)
'**** Define Incident Polarizations ****'
(0,0) (1.,0.) (0.,0.) = Polarization state e01 (k along x axis)
2 = IORTH  (=1 to do only pol. state e01; =2 to also do orth. pol. state)
'**** Specify which output files to write ****'
0 = IWRKSC (=0 to suppress, =1 to write ".sca" file for each target orient.
'**** Specify Target Rotations ****'
0.    0.   1  = BETAMI, BETAMX, NBETA  (beta=rotation around a1)
90.    90.   1  = THETMI, THETMX, NTHETA (theta=angle between a1 and k)
0.    0.   1  = PHIMIN, PHIMAX, NPHI (phi=rotation angle of a1 around k)
'**** Specify first IWAV, IRAD, IORI (normally 0 0 0) ****'
0   0   0    = first IWAV, first IRAD, first IORI (0 0 0 to begin fresh)
'**** Select Elements of S_ij Matrix to Print ****'
9	= NSMELTS = number of elements of S_ij to print (not more than 9)
11 12 21 22 31 33 44 34 43	= indices ij of elements to print
'**** Specify Scattered Directions ****'
'TFRAME' = CMDFRM (LFRAME, TFRAME for Lab Frame or Target Frame)
1 = NPLANES = number of scattering planes
0.  0. 180. 1 = phi, theta_min, theta_max (deg) for plane A
