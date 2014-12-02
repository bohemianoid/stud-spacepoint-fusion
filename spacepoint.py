import pywinusb.hid as hid
from time import sleep
import math
from pymouse import PyMouse

class SpacePoint :

    def __init__( self ) :
        self._vendor_id  = 0x20ff
        self._product_id = 0x0100
        self._hid_raw    = None
        self._hid_quat   = None
        self._frequency  = 125
        self.mag         = None
        self.acc         = None
        self.gyr         = None
        self.buttons     = None
        self.quat        = None
        self.grav        = None
        self.euler       = None

        self._mouse      = PyMouse()
        self._screen     = self._mouse.screen_size()
        self.euler_old   = None

        self.find()
        self.update()

    def find( self ) :
        device_filter = hid.HidDeviceFilter( vendor_id = self._vendor_id,
                        product_id = self._product_id )

        interfaces = device_filter.get_devices()

        if not interfaces :
            print( 'Device not found.' )

        else:
            for interface in interfaces :
                if interface.product_name == 'Raw Interface' :
                    self._hid_raw = interface
                if interface.product_name == 'Quaternions' :
                    self._hid_quat = interface

    def update( self ) :
        if self._hid_raw and self._hid_quat :
            try:
                self._hid_raw.open()
                self._hid_raw.set_raw_data_handler( self.raw_handler )

                self._hid_quat.open()
                self._hid_quat.set_raw_data_handler( self.quat_handler )

                print( 'Device is running...' )
                print( '>> [Ctrl+c] to stop' )

                while self._hid_raw.is_plugged() and self._hid_quat.is_plugged() :
                    self.pointer()
                    sleep( 1/float( self._frequency ) )
                return

            except KeyboardInterrupt :
                return

            finally:
                self._hid_raw.close()
                self._hid_quat.close()
                print( 'Device stopped.' )

    def raw_handler( self, data ) :
        m0 = data[ 1 ]|( data[ 2 ]<<8 )
        m1 = data[ 3 ]|( data[ 4 ]<<8 )
        m2 = data[ 5 ]|( data[ 6 ]<<8 )
        self.mag = ( m0, m1, m2 )

        a0 = data[ 7 ]|( data[ 8 ]<<8 )
        a1 = data[ 9 ]|( data[ 10 ]<<8 )
        a2 = data[ 11 ]|( data[ 12 ]<<8 )
        self.acc = ( a0, a1, a2 )

        g0 = data[ 13 ]|( data[ 14 ]<<8 )
        g1 = data[ 15 ]|( data[ 16 ]<<8 )
        g2 = data[ 17 ]|( data[ 18 ]<<8 )
        self.gyr = ( g0, g1, g2 )

        b0 = data[ 19 ]&1;
        b1 = ( data[ 19 ]&2 )>>1;
        self.buttons = ( b0, b1 )

    def quat_handler( self, data ) :
        g1 = ( ( data[ 1 ]|( data[ 2 ] )<<8 )-32768 )*6.0/32768.0
        g2 = ( ( data[ 3 ]|( data[ 4 ] )<<8 )-32768 )*6.0/32768.0
        g3 = ( ( data[ 5 ]|( data[ 6 ] )<<8 )-32768 )*6.0/32768.0
        self.grav = ( g1 , g2 , g3 )

        q0 = ( ( data[ 7 ]|( data[ 8 ]<<8 ) )-32768 )/32768.0
        q1 = ( ( data[ 9 ]|( data[ 10 ]<<8 ) )-32768 )/32768.0
        q2 = ( ( data[ 11 ]|( data[ 12 ]<<8 ) )-32768 )/32768.0
        q3 = ( ( data[ 13 ]|( data[ 14 ]<<8 ) )-32768 )/32768.0
        self.quat = ( q0 , q1 , q2 , q3 )

        sq0 = q0*q0
        sq1 = q1*q1
        sq2 = q2*q2
        sq3 = q3*q3

        yaw   = ( 180/math.pi )*math.atan2( 2.0*( q0*q1+q2*q3 ),
                  ( sq0-sq1-sq2+sq3 ) )
        pitch = ( 180/math.pi )*math.asin( -2.0*( q0*q2-q1*q3 ) )
        roll  = ( 180/math.pi )*math.atan2( 2.0*( q1*q2+q0*q3 ),
                  ( -sq0-sq1+sq2+sq3 ) )
        self.euler = ( yaw, pitch, roll )

        #b0 = data[ 15 ]&1;
        #b1 = ( data[ 15 ]&2 )>>1;
        #self.buttons = ( b0 , b1 )

    def pointer( self ) :
        if self.euler :
            if not self.euler_old :
                self.euler_old = self.euler

            dyaw = self.euler[ 0 ]-self.euler_old[ 0 ]

            x, y = self._mouse.position()

            if abs( dyaw ) > 0.4 and abs( dyaw ) < 270 :
                dx = int( 20*dyaw )

            else :
                dx = 0

            dy = int( 20*( self.euler[ 1 ]-self.euler_old[ 1 ] ) )

            self._mouse.move( x+dx, y-dy )

            self.euler_old = self.euler

        if self.buttons :
            x, y = self._mouse.position()

            if self.buttons[ 0 ] == 1 :
                self._mouse.press( x, y, 1 )
            else :
                self._mouse.release( x, y, 1 )

            if self.buttons[ 1 ] == 1 :
                self._mouse.press( x, y, 2 )
            else :
                self._mouse.release( x, y, 2 )

            if sum( self.buttons ) == 2 :
                self._mouse.move( self._screen[ 0 ]/2, self._screen[ 1 ]/2 )

if __name__ == '__main__' :
    #hid.core.show_hids()
    fusion = SpacePoint()
