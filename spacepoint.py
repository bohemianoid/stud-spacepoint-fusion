import pywinusb.hid as hid
from time import sleep
import math
from pymouse import PyMouse
import msvcrt

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
        self.yaw         = None
        self.pitch       = None
        self.roll        = None

        self._mouse      = PyMouse()
        self.yaw0        = 0
        self.pitch0      = 0

        self._x_dim, self._y_dim = self._mouse.screen_size()

        self.start()
        self.update()

    def start( self ) :
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
                print( '>> [Space]  to calibrate' )
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

        #b0 = data[ 15 ]&1;
        #b1 = ( data[ 15 ]&2 )>>1;
        #self.buttons = ( b0 , b1 )

        self.euler()

    def euler( self ) :
        sqx = self.quat[ 0 ]*self.quat[ 0 ]
        sqy = self.quat[ 1 ]*self.quat[ 1 ]
        sqz = self.quat[ 2 ]*self.quat[ 2 ]
        sqw = self.quat[ 3 ]*self.quat[ 3 ]

        self.yaw   = ( 180/math.pi )*math.atan2( 2.0*( self.quat[ 0 ]*self.quat[ 1 ]+
                     self.quat[ 2 ]*self.quat[ 3 ] ), ( sqx-sqy-sqz+sqw ) )
        self.pitch = ( 180/math.pi )*math.asin( -2.0*( self.quat[ 0 ]*self.quat[ 2 ]-
                     self.quat[ 1 ]*self.quat[ 3 ] ) )
        self.roll  = ( 180/math.pi )*math.atan2( 2.0*( self.quat[ 1 ]*self.quat[ 2 ]+
                     self.quat[ 0 ]*self.quat[ 3 ] ), ( -sqx-sqy+sqz+sqw ) )

    def pointer( self ) :
        if self.yaw and self.pitch :
            self._mouse.move( int( self._x_dim/2+self.yaw-self.yaw0 ),
                              int( self._y_dim/2-self.pitch-self.pitch0 ) )

            if msvcrt.kbhit() :
                if ord( msvcrt.getch() ) == 32 :
                    self.yaw0   = self.yaw
                    self.pitch0 = self.pitch

if __name__ == '__main__' :
    #hid.core.show_hids()
    fusion = SpacePoint()
