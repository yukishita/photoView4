import subprocess
import os

class PhotoView(object):
    def __init__(self) -> None:
        pass

""" Raspberry Pi fbi でスライドショー """
class PhotoViewRaspiFbi( PhotoView ):
    def __init__(self) -> None:
        super().__init__()
        """ スプラッシュスクリーンの表示 """
        self.displayPhoto( "./photoview4/resource/boot.jpg" )

    def displayPhoto( self, _fileName ):
        try:
            subprocess.Popen( [ "/usr/bin/fbi" , "-T", "1", "-d","/dev/fb0", "-a", _fileName ], shell=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL )
        except:
            raise ValueError("Viewer error")

        return _fileName

    def closeDisplay(self):
        """ プロセスをkill """
        os.system("sudo pkill fbi")
        pass

    def isDisplayable(self):
        """ DisplayがONの時のみ動作させる """  
        out = subprocess.check_output([ "/usr/bin/vcgencmd", "display_power" ] ).decode( "ascii" )
        if( "display_power=1" in out ):
            return True
        else:
            return False