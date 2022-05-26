import subprocess
import threading
import random
import os
import time

class FileManager(object):
    """ コンストラクタ """
    def __init__(self, _weightDefault, _storePath, _indexOnlyMode ) -> None:
        """ メンバ変数 """
        self.fileDB = {}
        self.isStored = False;
        self.isStoreFinished = False;
        self.weightdefault = _weightDefault;
        self.isDBMerging = False;
        self.storePath = _storePath;
        self.downloadedFile = list()
        self.isFileReady = False;

        """ データベースの初期化スレッドの開始 """
        self.thread = threading.Thread(target=self.initDatabase)
        self.thread.start()

        """ インデックスのみ取得の時はファイル取得のスレッドを開始しない """
        if not ( _indexOnlyMode ):
            """ ファイル取得スレッドの開始 """
            self.fileGetThread = threading.Thread(target=self.initFileGet)
            self.fileGetThread.start()

    """ データベースに書き込み """
    def addDB( self, _name ):
        """ ファイル名に対応するカウント値(初期値0) を代入する """
        self.fileDB[ _name ] = 3
        """ 複数のファイルを取得完了したら取得済みに設定する """
        if( 1000 < len( self.fileDB ) ):
            self.isStored = True

    """ データベースのアップデートを完了する """
    def fixDB( self ):
        self.isStored = True
        self.isStoreFinished = True

    """ データーベースからファイル名をランダムに取得 """
    def getRandomFileName( self ):
        """ ファイルが記録ずみの場合に取得する """
        if( self.isStored ):
                """ 重みづけしたランダムなファイル名を取得する """
                candidates = [*self.fileDB]
                weights = [*self.fileDB.values()]
                self.fileName = random.choices(candidates, weights=weights)[0]

                """ 1以上の時、デクリメントする """
                if( 1 < self.fileDB[ self.fileName ] ):
                    self.fileDB[ self.fileName ] -= 1
                else:
                    self.fileDB[ self.fileName ] = self.weightdefault

                return self.fileName
        else:
            raise ValueError("database is not ready")

    """ データベースファイルを取得する """
    def getDatabase( self ):
        return self.fileDB

    """ データベースファイルをマージする """
    def mergeDatabase( self, _db ):
        self.isStored = False
        self.isStoreFinished = False

        self.fileDB = _db | self.fileDB

        self.isStored = True
        self.isStoreFinished = True

    """ データベース取得が完了したか確認する """
    def isDBCreateFinished( self ):
        return self.isStoreFinished

    """ ファイル一覧のアップデート """
    def updateDatabase( self ):
        """ rclone の実行(ls) """
        self.proc = subprocess.Popen( [ self.rclonePath, "ls", self.googleDrivePath ], stdout=subprocess.PIPE )

        """ rclone 出力を取得して fileDB に格納 """
        while True:
            self.line = self.proc.stdout.readline()

            if self.line:
                self.s = self.line.split()
                self.addDB( self.s[1].decode() )

            if not self.line and self.proc.poll() is not None:
                self.fixDB()
                break

    """ 実際のファイルを削除 """
    def deleteActualFile( self, _fileName ):
        try:
            delfile = self.storePath + "/" + _fileName
            os.remove( delfile )

        except:
            """ 削除エラーが発生したときはリストのみ削除する """
            pass

        """ ダウンロードリストを削除 """
        index = self.downloadedFile.index(_fileName)
        del self.downloadedFile[index]

        """ ダウンロードしたファイルがなくなった """
        if( len(self.downloadedFile) == 0 ):
            self.isFileReady = False

""" rclone の実装 """
class RcloneFileManager(FileManager):
    """ コンストラクタ """
    def __init__(self, _rclonePath, _googleDrivePath, _weightDefault, _storePath, _indexOnlyMode ) -> None:

        """ メンバ変数 """
        self.rclonePath = _rclonePath
        self.googleDrivePath = _googleDrivePath

        super().__init__( _weightDefault, _storePath, _indexOnlyMode )

    """ ファイルの取得 """
    def initDatabase( self ):
        """ rclone の実行(ls) """
        while True:
            try:
                self.proc = subprocess.Popen( [ self.rclonePath, "ls", self.googleDrivePath ], stdout=subprocess.PIPE )
                break
            except:
                pass

        """ rclone 出力を取得して fileDB に格納 """
        while True:
            self.line = self.proc.stdout.readline()

            if self.line:
                self.s = self.line.split()
                self.addDB( self.s[1].decode() )

            if not self.line and self.proc.poll() is not None:
                self.fixDB()
                break

    """ 実際のファイルを取得(1ファイル) """
    def getActualFile( self, _fileName ):
        fullPath = self.googleDrivePath + '/' + _fileName
        while True:
            try:
                subprocess.call([ self.rclonePath , "copy", fullPath, self.storePath ])
                break
            except:
                raise ValueError("rclone copy error")
        return _fileName

    """ 実際のファイルを取得(スレッドで常に実行) """
    def initFileGet( self ):
        while True:
            time.sleep( 1 )

            if( self.isStored ):
                if( len(self.downloadedFile) < 5 ):
                    self.downloadedFile.append( self.getActualFile( self.getRandomFileName() ) )
                    self.isFileReady = True

    """ ダウンロードしたファイルを取得 """
    def getDownloadFile( self ):
        if( self.isFileReady ):
            fileName = self.downloadedFile[0]

            return fileName
        else:
            raise ValueError("download file is not ready")
