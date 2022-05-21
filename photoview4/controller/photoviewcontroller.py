import time
import threading

import photoview4.model.filemanager
import photoview4.view.photoView

class photoviewcontroller(object):
    def __init__( self, config ) -> None:

        """ Config 内容の読み込み """
        self.googleDrivePath = config['DEFAULT']['googleDrivePath']
        self.storePath = config['DEFAULT']['storePath']
        self.randomWeightdefault = int(config['DEFAULT']['randomWeightdefault'])
        self.mergeDuration = int(config['DEFAULT']['mergeDuration'])
        self.showDuration = int(config['DEFAULT']['showDuration'])

        """ スレッドの開始 """
        self.thread = threading.Thread(target=self.fileMerge)
        self.thread.start()

class raspiCloudController( photoviewcontroller ):
    def __init__( self, config ) -> None:
        super().__init__( config )

        """ Config 内容の読み込み """
        self.rclonePath = config['DEFAULT']['rclonePath']

        """ ファイルビューアの起動 """
        self.photoView = photoview4.view.photoView.PhotoViewRaspiFbi()

        """ file manager の起動 """
        self.fileManager = photoview4.model.filemanager.RcloneFileManager( self.rclonePath, self.googleDrivePath, self.randomWeightdefault, self.storePath, False )

    def startup( self ):
        while True:
            try:
                """ ファイルを表示する """
                file = self.fileManager.getDownloadFile()
                self.photoView.displayPhoto( self.storePath + "/" + file )

                """ 指定の時間 sleep """
                time.sleep( self.mergeDuration )

                self.fileManager.deleteActualFile( file )
            except:
                pass

    def fileMerge( self ):
        while True:
            time.sleep( self.mergeDuration )
            
            if( self.fileManager.isDBCreateFinished() ):
                fileManager_for_merge = photoview4.model.filemanager.RcloneFileManager( self.rclonePath, self.googleDrivePath, self.randomWeightdefault, self.storePath, True )
        
                while( not fileManager_for_merge.isDBCreateFinished() ):
                    pass            
                
                self.fileManager.mergeDatabase( fileManager_for_merge.getDatabase() )
                del fileManager_for_merge
