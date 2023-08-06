import os
from deterministic_encryption_utils.encryption.EncryptionExtensions import FilenameSaltProvider

class NameFilenameSaltProvider(FilenameSaltProvider):
    
    def getId(self):
        return "filename"
    
    def getSaltFor(self, absoluteFilePath):
        if not os.path.exists(absoluteFilePath):
            raise ValueError("The given path must exist.")
        return os.path.basename(absoluteFilePath)
