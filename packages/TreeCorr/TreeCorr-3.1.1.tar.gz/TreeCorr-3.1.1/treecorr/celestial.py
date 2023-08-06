# Copyright (c) 2003-2014 by Mike Jarvis
#
# TreeCorr is free software: redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions, and the disclaimer given in the accompanying LICENSE
#    file.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, and the disclaimer given in the documentation
#    and/or other materials provided with the distribution.

# Note: This file was original written for GalSim.  But since I was the author
# of it there, I can republish it here under the TreeCorr license too.  I've
# made a few (slight) modifications from the GalSim version.


angle_units = {
    'arcsec' : 4.84813681109537e-6,
    'arcmin' : 2.90888208665722e-4,
    'deg' : 1.74532925199433e-2,
    'hour' : 2.61799387799149e-1,
    'rad' : 1.,
}
"""The value of various angle units in radians for easy conversion.

Note that there are also shorthand equivalents for these.  e.g. Either::

    4. * treecorr.angle_units['arcsec']
    4. * treecorr.arcsec

would represent 4 arcsec in radians.
"""

arcsec = angle_units['arcsec']  #: 1 arcsec in radians
arcmin = angle_units['arcmin']  #: 1 arcmin in radians
degrees = angle_units['deg']    #: 1 degree in radians
hours = angle_units['hour']     #: 1 hour of angle in radians
radians = angle_units['rad']    #: 1 radian in radians

class CelestialCoord(object):
    """This class defines a position on the celestial sphere, normally given by
    two angles, `ra` and `dec`.

    This class is used to perform various calculations in spherical coordinates, such
    as the angular distance between two points in the sky, the angles in spherical triangles,
    projecting from sky coordinates onto a Euclidean tangent plane, etc.

    A `CelestialCoord` object is constructed from the right ascension and declination:

        >>> coord = treecorr.CelestialCoord(ra, dec)

    The input angles are assumed to be in radians, but we have some helper variables to 
    convert from other units:

    - :const:`treecorr.arcsec`    The value of 1 arcsec in radians = pi/(180*3600)
    - :const:`treecorr.arcmin`    The value of 1 arcmin in radians = pi/(180*60)
    - :const:`treecorr.degrees`   The value of 1 degree in radians = pi/180
    - :const:`treecorr.hours`     The value of 1 hour in radians   = pi/12
    - :const:`treecorr.radians`   The value of 1 radian in radians = 1

    So if you have ra in hours, and dec in degrees, you can write:

        >>> coord = treecorr.CelestialCoord(ra * treecorr.hours, dec * treecorr.degrees)

    After construction, you can access the ra and dec values as read-only attributes.

        >>> ra = coord.ra
        >>> dec = coord.dec

    :param ra:       The right ascension in radians.
    :param dec:      The declination in radian.
    """
    def __init__(self, ra, dec):
        self._ra = ra
        self._dec = dec
        self._x = None  # Indicate that x,y,z are not set yet.

    @property
    def ra(self): return self._ra

    @property
    def dec(self): return self._dec


    def _set_aux(self):
        if self._x is None:
            import math
            self._cosdec = math.cos(self._dec)
            self._sindec = math.sin(self._dec)
            self._cosra = math.cos(self._ra)
            self._sinra = math.sin(self._ra)
            self._x = self._cosdec * self._cosra
            self._y = -self._cosdec * self._sinra
            self._z = self._sindec


    def distanceTo(self, other):
        """Returns the great circle distance between this coord and another one.
        The return value is in radians.

        :param other:   Another `CelestialCoord` object.
        :returns:       The great circle distance in radians between this coord and `other`.
        """
        # The easiest way to do this in a way that is stable for small separations
        # is to calculate the (x,y,z) position on the unit sphere corresponding to each
        # coordinate position.
        #
        # x = cos(dec) cos(ra)
        # y = cos(dec) sin(ra)
        # z = sin(dec)

        self._set_aux()
        other._set_aux()

        # The the direct distance between the two points is
        #
        # d^2 = (x1-x2)^2 + (y1-y2)^2 + (z1-z2)^2

        dsq = (self._x-other._x)**2 + (self._y-other._y)**2 + (self._z-other._z)**2

        # This direct distance can then be converted to a great circle distance via
        #
        # sin(theta/2) = d/2

        import math
        theta = 2. * math.asin(0.5 * math.sqrt(dsq))
        return theta


    def angleBetween(self, coord1, coord2):
        """Find the open angle at the location of the current coord between `coord1` and
        `coord2`.

        :param coord1:  Another `CelestialCoord` object.
        :param coord2:  A third `CelestialCoord` object.
        :returns:       The angle in radians between the great circles to the two other coords.
        """
        # Call A = coord1, B = coord2, C = self
        # Then we are looking for the angle ACB.
        # If we treat each coord as a (x,y,z) vector, then we can use the following spherical
        # trig identities:
        #
        # (A x C) . B = sina sinb sinC
        # (A x C) . (B x C) = sina sinb cosC
        #
        # Then we can just use atan2 to find C, and atan2 automatically gets the sign right.
        # And we only need 1 trig call, assuming that x,y,z are already set up, which is often
        # the case.

        self._set_aux()
        coord1._set_aux()
        coord2._set_aux()

        AxC = ( coord1._y * self._z - coord1._z * self._y ,
                coord1._z * self._x - coord1._x * self._z ,
                coord1._x * self._y - coord1._y * self._x )
        BxC = ( coord2._y * self._z - coord2._z * self._y ,
                coord2._z * self._x - coord2._x * self._z ,
                coord2._x * self._y - coord2._y * self._x )
        sinC = AxC[0] * coord2._x + AxC[1] * coord2._y + AxC[2] * coord2._z
        cosC = AxC[0] * BxC[0] + AxC[1] * BxC[1] + AxC[2] * BxC[2]
        import math
        C = math.atan2(sinC, cosC)
        return C


    def area(self, coord1, coord2):
        """Find the area of the spherical triangle defined by the current coordinate, `coord1`,
        and `coord2`, returning the area in steradians.

        :param coord1:  Another `CelestialCoord` object.
        :param coord2:  A third `CelestialCoord` object.
        :returns:       The area in steradians of the spherical triangle defined by the three
                        coords.
        """
        # The area of a spherical triangle is defined by the "spherical excess", E.
        # There are several formulae for E:
        #    (cf. http://en.wikipedia.org/wiki/Spherical_trigonometry#Area_and_spherical_excess)
        #
        # E = A + B + C - pi
        # tan(E/4) = sqrt(tan(s/2) tan((s-a)/2) tan((s-b)/2) tan((s-c)/2)
        # tan(E/2) = tan(a/2) tan(b/2) sin(C) / (1 + tan(a/2) tan(b/2) cos(C))
        # 
        # We use the last formula, which is stable both for small triangles and ones that are
        # nearly degenerate (which the middle formula may have trouble with).
        #
        # Furthermore, we can use some of the math for angleBetween and distanceTo to simplify
        # this further:
        #
        # In angleBetween, we have formulae for sina sinb sinC and sina sinb cosC.
        # In distanceTo, we have formulae for sin(a/2) and sin(b/2).
        #
        # Define: F = sina sinb sinC
        #         G = sina sinb cosC
        #         da = 2 sin(a/2)
        #         db = 2 sin(b/2)
        # 
        # tan(E/2) = sin(a/2) sin(b/2) sin(C) / (cos(a/2) cos(b/2) + sin(a/2) sin(b/2) cos(C))
        #          = sin(a) sin(b) sin(C) / (4 cos(a/2)^2 cos(b/2)^2 + sin(a) sin(b) cos(C))
        #          = F / (4 (1-sin(a/2)^2) (1-sin(b/2)^2) + G)
        #          = F / (4-da^2) (4-db^2)/4 + G)

        import math
        self._set_aux()
        coord1._set_aux()
        coord2._set_aux()

        AxC = ( coord1._y * self._z - coord1._z * self._y ,
                coord1._z * self._x - coord1._x * self._z ,
                coord1._x * self._y - coord1._y * self._x )
        BxC = ( coord2._y * self._z - coord2._z * self._y ,
                coord2._z * self._x - coord2._x * self._z ,
                coord2._x * self._y - coord2._y * self._x )
        F = AxC[0] * coord2._x + AxC[1] * coord2._y + AxC[2] * coord2._z
        G = AxC[0] * BxC[0] + AxC[1] * BxC[1] + AxC[2] * BxC[2]
        dasq = (self._x-coord1._x)**2 + (self._y-coord1._y)**2 + (self._z-coord1._z)**2
        dbsq = (self._x-coord2._x)**2 + (self._y-coord2._y)**2 + (self._z-coord2._z)**2

        tanEo2 = F / ( 0.25 * (4.-dasq) * (4.-dbsq) + G)
        E = 2. * math.atan( abs(tanEo2) )
        return E


    def project(self, other, projection='lambert'):
        """Use the currect coord as the center point of a tangent plane projection to project
        the `other` coordinate onto that plane.

        This function returns the position (u,v) in the Euclidean coordinate system defined by
        a tangent plane projection around the current coordinate, with +v pointing north and
        +u pointing west.

        There are currently four options for the projection, which you can specify as a string
        value for the `projection` keyword argument:

        - 'lambert' Uses a Lambert azimuthal projection, which preserves the area of small
          patches, but not the angles between points in these patches.  For more information, see
          http://mathworld.wolfram.com/LambertAzimuthalEqual-AreaProjection.html
        - 'stereographic' Uses a stereographic proejection, which preserves angles between points
          in small patches, but not area.  For more information, see 
          http://mathworld.wolfram.com/StereographicProjection.html
        - 'gnomonic' Uses a gnomonic projection (i.e. a projection from the center of the sphere),
          which has the property that all great circles become straight lines.  For more 
          information, see http://mathworld.wolfram.com/GnomonicProjection.html
        - 'postel' Uses a Postel equidistant proejection, which preserves distances from the
          projection point, but not area or angles.  For more information, see
          http://mathworld.wolfram.com/AzimuthalEquidistantProjection.html

        The distance or angle errors increase with distance from the projection point of course.

        :param other:       The coordinate to be projected relative to the current coord.
        :param projection:  Which kind of projection to use. (default: 'lambert')
        :returns:           The projected position (u,v) in radians as a tuple.
        """
        if projection not in [ 'lambert', 'stereographic', 'gnomonic', 'postel' ]:
            raise ValueError('Unknown projection ' + projection)

        self._set_aux()
        other._set_aux()

        # The core calculation is done in a helper function:
        return self._project_core(other._cosra, other._sinra, other._cosdec, other._sindec,
                                  projection)


    def _project_core(self, cosra, sinra, cosdec, sindec, projection):
        # The equations are given at the above mathworld websites.  They are the same except
        # for the definition of k:
        #
        # x = k cos(dec) sin(ra-ra0)
        # y = k ( cos(dec0) sin(dec) - sin(dec0) cos(dec) cos(ra-ra0) )
        #
        # Lambert:
        #   k = sqrt( 2  / ( 1 + cos(c) ) )
        # Stereographic:
        #   k = 2 / ( 1 + cos(c) )
        # Gnomonic:
        #   k = 1 / cos(c)
        # Postel:
        #   k = c / sin(c)
        # where cos(c) = sin(dec0) sin(dec) + cos(dec0) cos(dec) cos(ra-ra0)

        # cos(dra) = cos(ra-ra0) = cos(ra0) cos(ra) + sin(ra0) sin(ra)
        cosdra = self._cosra * cosra + self._sinra * sinra

        # sin(dra) = -sin(ra - ra0)
        # Note: - sign here is to make +x correspond to -ra,
        #       so x increases for decreasing ra.
        #       East is to the left on the sky!
        # sin(dra) = -cos(ra0) sin(ra) + sin(ra0) cos(ra)
        sindra = -self._cosra * sinra + self._sinra * cosra

        # Calculate k according to which projection we are using
        cosc = self._sindec * sindec + self._cosdec * cosdec * cosdra
        if projection[0] == 'l':
            import numpy
            k = numpy.sqrt( 2. / (1.+cosc) )
        elif projection[0] == 's':
            k = 2. / (1. + cosc)
        elif projection[0] == 'g':
            k = 1. / cosc
        else:
            import numpy
            c = numpy.arccos(cosc)
            k = c / numpy.sin(c)

        u = k * cosdec * sindra
        v = k * ( self._cosdec * sindec - self._sindec * cosdec * cosdra )

        return u, v


    def project_rad(self, ra, dec, projection):
        """This is basically identical to the :meth:`~treecorr.CelestialCoord.project` method 
        except that the input `ra`, `dec` are given in radians rather than packaged as a 
        `CelestialCoord` object.

        The main advantage to this is that it will work if `ra` and `dec` are NumPy arrays,
        in which case the output `x`, `y` will also be NumPy arrays.

        See the doc for :meth:`~treecorr.CelestialCoord.project` for more information about the 
        kinds of projection.

        :param ra:          The RA of the coordinate to be projected relative to the current coord.
        :param dec:         The Dec of the coordinate to be projected relative to the current coord.
        :param projection:  Which kind of projection to use. (default: 'lambert')
        :returns:           The projected position (u,v) in radians as a tuple.
        """
        if projection not in [ 'lambert', 'stereographic', 'gnomonic', 'postel' ]:
            raise ValueError('Unknown projection ' + projection)

        self._set_aux()

        import numpy
        cosra = numpy.cos(ra)
        sinra = numpy.sin(ra)
        cosdec = numpy.cos(dec)
        sindec = numpy.sin(dec)

        return self._project_core(cosra, sinra, cosdec, sindec, projection)


    def deproject(self, u, v, projection='lambert'):
        """Do the reverse process from the project() function.

        i.e. This takes in a position (u,v) as a tuple and returns the corresponding celestial
        coordinate, using the current coordinate as the center point of the tangent plane
        projection.

        See the doc for :meth:`~treecorr.CelestialCoord.project` for more information about the 
        kinds of projection.

        :param u:           The projected u value to be deprojected.
        :param v:           The projected v value to be deprojected.
        :param projection:  Which kind of projection to use. (default: 'lambert')
        :returns:           The `CelestialCoord` corresponding to the given projected position.
        """
        if projection not in [ 'lambert', 'stereographic', 'gnomonic', 'postel' ]:
            raise ValueError('Unknown projection ' + projection)

        # Again, do the core calculations in a helper function
        ra, dec = self._deproject_core(u, v, projection)

        return CelestialCoord(ra,dec)


    def _deproject_core(self, u, v, projection):
        # The inverse equations are also given at the same web sites:
        #
        # sin(dec) = cos(c) sin(dec0) + v sin(c) cos(dec0) / r
        # tan(ra-ra0) = u sin(c) / (r cos(dec0) cos(c) - v sin(dec0) sin(c))
        #
        # where
        #
        # r = sqrt(u^2+v^2)
        # c = 2 sin^(-1)(r/2) for lambert
        # c = 2 tan^(-1)(r/2) for stereographic
        # c = tan^(-1)(r)     for gnomonic
        # c = r               for postel

        # Note that we can rewrite the formulae as:
        #
        # sin(dec) = cos(c) sin(dec0) + v (sin(c)/r) cos(dec0)
        # tan(ra-ra0) = u (sin(c)/r) / (cos(dec0) cos(c) - v sin(dec0) (sin(c)/r))
        #
        # which means we only need cos(c) and sin(c)/r.  For most of the projections, 
        # this saves us from having to take sqrt(rsq).

        import numpy
        rsq = u*u + v*v
        if projection[0] == 'l':
            # c = 2 * arcsin(r/2)
            # Some trig manipulations reveal:
            # cos(c) = 1 - r^2/2
            # sin(c) = r sqrt(4-r^2) / 2
            cosc = 1. - rsq/2.
            sinc_over_r = numpy.sqrt(4.-rsq) / 2.
        elif projection[0] == 's':
            # c = 2 * arctan(r/2)
            # Some trig manipulations reveal:
            # cos(c) = (4-r^2) / (4+r^2)
            # sin(c) = 4r / (4+r^2)
            cosc = (4.-rsq) / (4.+rsq)
            sinc_over_r = 4. / (4.+rsq)
        elif projection[0] == 'g':
            # c = arctan(r)
            # cos(c) = 1 / sqrt(1+r^2)
            # sin(c) = r / sqrt(1+r^2)
            cosc = sinc_over_r = 1./numpy.sqrt(1.+rsq)
        else:
            r = numpy.sqrt(rsq)
            cosc = numpy.cos(r)
            sinc_over_r = numpy.sinc(r/numpy.pi)

        # Compute sindec, tandra
        self._set_aux()
        sindec = cosc * self._sindec + v * sinc_over_r * self._cosdec
        # Remember the - sign so +dra is -u.  East is left.
        tandra_num = -u * sinc_over_r
        tandra_denom = cosc * self._cosdec - v * sinc_over_r * self._sindec

        dec = numpy.arcsin(sindec)
        ra = self.ra + numpy.arctan2(tandra_num, tandra_denom)

        return ra, dec


    def deproject_rad(self, u, v, projection='lambert'):
        """This is basically identical to the deproject() function except that the output `ra`,
        `dec` are returned as a tuple (ra, dec) in radians rather than packaged as a 
        `CelestialCoord` object.

        The main advantage to this is that it will work if `u` and `v` are NumPy arrays,
        in which case the output `ra`, `dec` will also be NumPy arrays.

        See the doc for :meth:`~treecorr.CelestialCoord.project` for more information about the 
        kinds of projection.

        :param u:           The projected u value to be deprojected.
        :param v:           The projected v value to be deprojected.
        :param projection:  Which kind of projection to use. (default: 'lambert')
        :returns:           A tuple (ra, dec) of the deprojected coordinates.
        """
        if projection not in [ 'lambert', 'stereographic', 'gnomonic', 'postel' ]:
            raise ValueError('Unknown projection ' + projection)

        return self._deproject_core(u, v, projection)


    def deproject_jac(self, u, v, projection='lambert'):
        """Return the jacobian of the deprojection.

        i.e. if the input position is (u,v) (in radians) then the return matrix is

        J = ( dra/du cos(dec)  dra/dv cos(dec) )
            (    ddec/du          ddec/dv      )

        See the doc for :meth:`~treecorr.CelestialCoord.project` for more information about the 
        kinds of projection.

        :param u:           The projected u value to be deprojected.
        :param v:           The projected v value to be deprojected.
        :param projection:  Which kind of projection to use. (default: 'lambert')
        :returns:           The matrix as a tuple (J00, J01, J10, J11)
        """
        if projection not in [ 'lambert', 'stereographic', 'gnomonic', 'postel' ]:
            raise ValueError('Unknown projection ' + projection)

        # sin(dec) = cos(c) sin(dec0) + v sin(c)/r cos(dec0)
        # tan(ra-ra0) = u sin(c)/r / (cos(dec0) cos(c) - v sin(dec0) sin(c)/r)
        #
        # d(sin(dec)) = cos(dec) ddec = s0 dc + (v ds + s dv) c0
        # dtan(ra-ra0) = sec^2(ra-ra0) dra 
        #              = ( (u ds + s du) A - u s (dc c0 - (v ds + s dv) s0 ) )/A^2 
        # where s = sin(c) / r
        #       c = cos(c)
        #       s0 = sin(dec0)
        #       c0 = cos(dec0) 
        #       A = c c0 - v s s0

        import numpy
        rsq = u*u + v*v
        rsq1 = (u+1.e-4)**2 + v**2
        rsq2 = u**2 + (v+1.e-4)**2
        if projection[0] == 'l':
            c = 1. - rsq/2.
            s = numpy.sqrt(4.-rsq) / 2.
            dcdu = -u
            dcdv = -v
            dsdu = -u/(4.*s)
            dsdv = -v/(4.*s)
        elif projection[0] == 's':
            s = 4. / (4.+rsq)
            c = 2.*s-1.
            ssq = s*s
            dcdu = -u * ssq
            dcdv = -v * ssq
            dsdu = 0.5*dcdu
            dsdv = 0.5*dcdv
        elif projection[0] == 'g':
            c = s = 1./numpy.sqrt(1.+rsq)
            s3 = s*s*s
            dcdu = dsdu = -u*s3
            dcdv = dsdv = -v*s3
        else:
            r = numpy.sqrt(rsq)
            if r == 0.:
                c = s = 1
            else:
                c = numpy.cos(r)
                s = numpy.sin(r)/r
            dcdu = -s*u
            dcdv = -s*v
            dsdu = (c-s)*u/rsq
            dsdv = (c-s)*v/rsq

        self._set_aux()
        s0 = self._sindec
        c0 = self._cosdec
        sindec = c * s0 + v * s * c0
        cosdec = numpy.sqrt(1.-sindec*sindec)
        dddu = ( s0 * dcdu + v * dsdu * c0 ) / cosdec
        dddv = ( s0 * dcdv + (v * dsdv + s) * c0 ) / cosdec

        tandra_num = u * s
        tandra_denom = c * c0 - v * s * s0
        # Note: A^2 sec^2(dra) = denom^2 (1 + tan^2(dra) = denom^2 + num^2
        A2sec2dra = tandra_denom**2 + tandra_num**2
        drdu = ((u * dsdu + s) * tandra_denom - u * s * ( dcdu * c0 - v * dsdu * s0 ))/A2sec2dra
        drdv = (u * dsdv * tandra_denom - u * s * ( dcdv * c0 - (v * dsdv + s) * s0 ))/A2sec2dra

        drdu *= cosdec
        drdv *= cosdec
        return drdu, drdv, dddu, dddv


    def precess(self, from_epoch, to_epoch):
        """This function precesses equatorial ra and dec from one epoch to another.

        It is adapted from a set of fortran subroutines based on (a) pages 30-34 of
        the Explanatory Supplement to the AE, (b) Lieske, et al. (1977) A&A 58, 1-16,
        and (c) Lieske (1979) A&A 73, 282-284.

        :param from_epoch:  The epoch to use for the current coord.
        :param to_epoch:    The new epoch to precess to.
        :returns:           A new `CelestialCoord` of the coordinates in the new epoch.
        """
        if from_epoch == to_epoch: return self

        # t0, t below correspond to Lieske's big T and little T
        t0 = (from_epoch-2000.)/100.
        t = (to_epoch-from_epoch)/100.
        t02 = t0*t0
        t2 = t*t
        t3 = t2*t

        # a,b,c below correspond to Lieske's zeta_A, z_A and theta_A.  They are all in arcsec.
        a = ( (2306.2181 + 1.39656*t0 - 0.000139*t02) * t +
              (0.30188 - 0.000344*t0) * t2 + 0.017998 * t3 ) * angle_units['arcsec']
        b = ( (2306.2181 + 1.39656*t0 - 0.000139*t02) * t +
              (1.09468 + 0.000066*t0) * t2 + 0.018203 * t3 ) * angle_units['arcsec']
        c = ( (2004.3109 - 0.85330*t0 - 0.000217*t02) * t +
              (-0.42665 - 0.000217*t0) * t2 - 0.041833 * t3 ) * angle_units['arcsec']
        import math
        cosa = math.cos(a)
        sina = math.sin(a)
        cosb = math.cos(b)
        sinb = math.sin(b)
        cosc = math.cos(c)
        sinc = math.sin(c)

        # This is the precession rotation matrix:
        xx = cosa*cosc*cosb - sina*sinb
        yx = -sina*cosc*cosb - cosa*sinb
        zx = -sinc*cosb
        xy = cosa*cosc*sinb + sina*cosb
        yy = -sina*cosc*sinb + cosa*cosb
        zy = -sinc*sinb
        xz = cosa*sinc
        yz = -sina*sinc
        zz = cosc

        # Perform the rotation:
        # And note that Lieske defines y with the opposite sign of our convention.
        self._set_aux()
        import numpy
        x2 = xx*self._x - yx*self._y + zx*self._z
        y2 = -xy*self._x + yy*self._y - zy*self._z
        z2 = xz*self._x - yz*self._y + zz*self._z

        new_dec = math.atan2(z2,math.sqrt(x2**2+y2**2)) 
        new_ra = math.atan2(-y2,x2)
        new_coord = CelestialCoord(new_ra,new_dec)
        return new_coord


    def galactic(self, epoch=2000.):
        """Get the longitude and latitude in galactic coordinates corresponding to this position.

        The formulae are implemented in terms of the 1950 coordinates, so we need to
        precess from the current epoch to 1950.  The current epoch is assumed to be 2000
        by default, but you may also specify a different value with the epoch parameter.

        :param epoch:   The epoch to assume for the current coordinates (default: 2000)
        :returns:       The longitude and latitude as a tuple (el, b) in radians.
        """
        # cf. Lang, Astrophysical Formulae, page 13
        # cos(b) cos(el-33) = cos(dec) cos(ra-282.25)
        # cos(b) sin(el-33) = sin(dec) sin(62.6) + cos(dec) sin(ra-282.25) cos(62.6)
        #            sin(b) = sin(dec) sin(62.6) - cos(dec) sin(ra-282.25) sin(62.6)
        import math
        el0 = 33. * angle_units['deg']
        r0 = 282.25 * angle_units['deg']
        d0 = 62.6 * angle_units['deg']
        cosd0 = math.cos(d0)
        sind0 = math.sin(d0)

        temp = self.precess(epoch, 1950.)
        d = temp.dec
        r = temp.ra
        cosd = math.cos(d)
        sind = math.sin(d)
        cosr = math.cos(r - r0)
        sinr = math.sin(r - r0)

        cbcl = cosd*cosr
        cbsl = sind*sind0 + cosd*sinr*cosd0
        sb = sind*cosd0 - cosd*sinr*sind0

        b = math.asin(sb)
        el = math.atan2(cbsl,cbcl) + el0

        return (el, b)


    def copy(self): return CelestialCoord(self._ra, self._dec)

    def __repr__(self): return 'CelestialCoord('+repr(self._ra)+','+repr(self._dec)+')'

