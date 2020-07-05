import hashlib
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import time
from datetime import datetime
import numpy as np
import os, sys
import shutil
import exifread

SOURCE_IMAGES = os.path.join("U:\\", "Users","ian","Pictures")
DESTINATION_IMAGES = os.path.join("C:\\", "Users","ian","Pictures", "Deduped")

def file_hash(filepath):
    with open(filepath, 'rb') as f:
        return md5(f.read()).hexdigest()


def recursiveList(dir, idx=0):
    file_list = {}
    valid = 0
    for index, entry in enumerate(os.listdir(dir)):
        fqe=os.path.join(dir, entry)
        if entry[0] not in ['.', '$'] and entry.split(".")[-1] not in ['dat', 'ini', 'db', 'DB1', 'DB2']:
            if os.path.isfile(fqe):
                if os.path.getsize(fqe)>10000:
                    file_list[idx+valid]=fqe
                    valid += 1
            else:
                new_files, nvalid = recursiveList(fqe, idx=valid+idx)
                print(f"{fqe}: {nvalid} Images found")
                valid += nvalid
                file_list.update(new_files)
    return (file_list, valid)


def hashImg(img):
    with open(img, 'rb') as f:
        filehash = hashlib.md5(f.read()).hexdigest()
    return filehash

def imgYear(img):
    return str(min(datetime.fromtimestamp(os.path.getmtime(img)).year, datetime.fromtimestamp(os.path.getctime(img)).year))

HASHES = {}
DUPLICATES = []

def buildHashSets(files):
    global HASHES
    global DUPLICATES
    copies = 0 
    duplicates = 0
    failures = 0
    for index, file in files.items():
        imgHash = hashImg(file)
        if imgHash in HASHES:
            DUPLICATES.append(index)
            duplicates +=1
        else:
            HASHES[imgHash]=file
            year = imgYear(file)
            filename = os.path.split(file)[1]
            os.makedirs(os.path.join(DESTINATION_IMAGES, year), exist_ok=True)
            try:
                if os.path.exists(os.path.join(DESTINATION_IMAGES, year, filename)):
                    filenames = filename.split(".")
                    filename = filenames[0]+'.'+str(int(time.time()))+'.'+filenames[1]
                    print(f"Renamed {os.path.join(DESTINATION_IMAGES, year, filename)}")
                shutil.copy2(file, os.path.join(DESTINATION_IMAGES, year, filename))
                copies +=1
            except Exception as e:
                print(f"Couldnt copy {file} - {e}. Skipping")
                shutil.copy2(file, os.path.join(DESTINATION_IMAGES, 'copy_failures', filename))
                failures += 1
    return copies, duplicates, failures

if __name__=="__main__":
    st = time.time()
    print(f"\n\n\tStarting directory {os.getcwd()}\n")
    os.chdir(SOURCE_IMAGES)
    print(f"\tCurrent working directory {os.getcwd()}")
    print(f"\tDestination directory {DESTINATION_IMAGES}\n")
    if input("Continue? [Y/n]    ")!='Y':
        print("Ok, please check your path and try again. For best performance, use a different physical drive from the source for the destination. ")
        sys.exit(0)
    print("Making sure destination exists")
    os.makedirs(DESTINATION_IMAGES, exist_ok=True)
    os.makedirs(os.path.join(DESTINATION_IMAGES, 'copy_failures'))
    print("Recurisvely building image list... ")
    files, fileCount = recursiveList(SOURCE_IMAGES)
    print(f"Total files found: {fileCount}")
    print(f"Deduping to {DESTINATION_IMAGES}")
    copies, duplicates, failures = buildHashSets(files)
    print(f"Time Taken: {time.time()-st/60:.2f} min")
    print(f"Duplicates: {duplicates} ==? {len(DUPLICATES)}")
    print(f"Failures: {failures}")
    print(f"Copies: {copies} ==? {len(HASHES)}")

